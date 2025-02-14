from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Literal

import optree

from _gettsim.aggregation import (
    AggregateByGroupSpec,
    AggregateByPIDSpec,
    all_by_p_id,
    any_by_p_id,
    count_by_p_id,
    grouped_all,
    grouped_any,
    grouped_count,
    grouped_max,
    grouped_mean,
    grouped_min,
    grouped_sum,
    max_by_p_id,
    mean_by_p_id,
    min_by_p_id,
    sum_by_p_id,
)
from _gettsim.config import (
    QUALIFIED_NAME_SEPARATOR,
    SUPPORTED_GROUPINGS,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.functions.derived_function import DerivedFunction
from _gettsim.groupings import create_groupings
from _gettsim.shared import (
    create_tree_from_path_and_value,
    format_errors_and_warnings,
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    partition_tree_by_reference_tree,
    remove_group_suffix,
    rename_arguments_and_add_annotations,
    upsert_path_and_value,
    upsert_tree,
)
from _gettsim.time_conversion import create_time_conversion_functions

if TYPE_CHECKING:
    from _gettsim.gettsim_typing import (
        NestedAggregationSpecDict,
        NestedDataDict,
        NestedFunctionDict,
        NestedTargetDict,
    )
    from _gettsim.policy_environment import PolicyEnvironment


def combine_policy_functions_and_derived_functions(
    environment: PolicyEnvironment,
    targets_tree: NestedTargetDict,
    data_tree: NestedDataDict,
) -> NestedFunctionDict:
    """Create the functions tree including derived functions.

    Create the functions tree by vectorizing all functions, and adding time conversion
    functions, aggregation functions, and combinations of these.

    Check that all targets have a corresponding function in the functions tree or can be
    taken from the data.

    Parameters
    ----------
    environment
        The environment containing the functions tree and the specs for aggregation.
    targets_tree
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.
    data_tree
        Names of columns in the input data.

    Returns
    -------
    The functions tree including derived functions.

    """
    # Create parent-child relationships
    aggregate_by_p_id_functions = _create_aggregation_functions(
        functions_tree=environment.functions_tree,
        aggregations_tree=environment.aggregation_specs_tree,
        aggregation_type="p_id",
    )

    # Create functions for different time units
    current_functions_tree = upsert_tree(
        base_tree=environment.functions_tree,
        update_tree=aggregate_by_p_id_functions,
    )
    time_conversion_functions = create_time_conversion_functions(
        functions_tree=current_functions_tree,
        data_tree=data_tree,
    )

    # Create aggregation functions
    current_functions_tree = upsert_tree(
        base_tree=current_functions_tree,
        update_tree=time_conversion_functions,
    )
    aggregate_by_group_functions = _create_aggregate_by_group_functions(
        functions_tree=current_functions_tree,
        targets_tree=targets_tree,
        data_tree=data_tree,
        aggregations_tree_provided_by_env=environment.aggregation_specs_tree,
    )

    # Create groupings
    groupings = create_groupings()

    # Put all functions into a functions tree
    all_functions = functools.reduce(
        upsert_tree,
        [
            aggregate_by_p_id_functions,
            time_conversion_functions,
            aggregate_by_group_functions,
            groupings,
        ],
        environment.functions_tree,
    )

    _fail_if_targets_not_in_functions_tree(all_functions, targets_tree)

    return all_functions


def _create_aggregate_by_group_functions(
    functions_tree: NestedFunctionDict,
    targets_tree: NestedTargetDict,
    data_tree: NestedDataDict,
    aggregations_tree_provided_by_env: dict[str, Any],
) -> dict[str, DerivedFunction]:
    """Create aggregation functions."""

    # Add automated aggregation specs to aggregations tree
    automatically_created_aggregations_tree = _create_derived_aggregations_tree(
        functions_tree=functions_tree,
        target_tree=targets_tree,
        data_tree=data_tree,
    )

    # Add automated aggregation specs to aggregations tree
    full_aggregations_tree = upsert_tree(
        base_tree=automatically_created_aggregations_tree,
        update_tree=aggregations_tree_provided_by_env,
    )

    return _create_aggregation_functions(
        functions_tree=functions_tree,
        aggregations_tree=full_aggregations_tree,
        aggregation_type="group",
    )


def _create_aggregation_functions(
    functions_tree: NestedFunctionDict,
    aggregations_tree: NestedAggregationSpecDict,
    aggregation_type: Literal["group", "p_id"],
) -> NestedFunctionDict:
    """Create aggregation functions."""

    out_tree = {}

    _all_paths, _all_aggregation_specs = optree.tree_flatten_with_path(
        aggregations_tree
    )[:2]

    expected_aggregation_spec_type = (
        AggregateByGroupSpec if aggregation_type == "group" else AggregateByPIDSpec
    )

    for tree_path, aggregation_spec in zip(_all_paths, _all_aggregation_specs):
        # Skip if aggregation spec is not the current aggregation type
        if not isinstance(aggregation_spec, expected_aggregation_spec_type):
            continue

        annotations = _annotations_for_aggregation(
            aggregation_method=aggregation_spec.aggr,
            source_col=aggregation_spec.source_col,
            namespace_of_function_to_derive=tree_path[:-1],
            functions_tree=functions_tree,
            types_input_variables=TYPES_INPUT_VARIABLES,
        )

        if aggregation_type == "group":
            derived_func = _create_one_aggregate_by_group_func(
                aggregation_target=tree_path[-1],
                aggregation_method=aggregation_spec.aggr,
                source_col=aggregation_spec.source_col,
                annotations=annotations,
            )
        else:
            p_id_to_aggregate_by = aggregation_spec.p_id_to_aggregate_by
            derived_func = _create_one_aggregate_by_p_id_func(
                aggregation_target=tree_path[-1],
                p_id_to_aggregate_by=p_id_to_aggregate_by,
                source_col=aggregation_spec.source_col,
                aggregation_method=aggregation_spec.aggr,
                annotations=annotations,
            )

        out_tree = upsert_path_and_value(
            tree=out_tree,
            tree_path=tree_path,
            value=derived_func,
        )

    return out_tree


def _create_derived_aggregations_tree(
    functions_tree: NestedFunctionDict,
    target_tree: NestedTargetDict,
    data_tree: NestedDataDict,
) -> NestedAggregationSpecDict:
    """Create automatic aggregation specs.

    Aggregation specifications are created automatically for summation aggregations.

    Parameters
    ----------
    functions_tree
        The functions tree.
    target_tree
        The target tree.
    data_tree
        The data tree.

    Returns
    -------
    The aggregation specifications derived from the functions and data tree.

    Example
    -------
    If
    - `func_hh` is an argument of the functions in `functions_tree`, or a target
    - and not represented by a function in `functions_tree` or a data column in
        the input data
    then an automatic aggregation specification is created for the sum aggregation of
    `func` by household.
    """
    # Create tree of potential aggregation function names
    potential_aggregation_function_names = upsert_tree(
        base_tree=target_tree,
        update_tree=_get_potential_aggregation_function_names_from_function_arguments(
            functions_tree
        ),
    )

    # Create source tree for aggregations. Source can be any already existing function
    # or data column.
    aggregation_source_tree = upsert_tree(
        base_tree=functions_tree,
        update_tree=data_tree,
    )

    # Create aggregation specs.
    derived_aggregations_tree = {}
    for tree_path in optree.tree_paths(
        potential_aggregation_function_names, none_is_leaf=True
    ):
        leaf_name = tree_path[-1]

        # Don't create aggregation functions for unsupported groupings or functions that
        # already exist in the source tree.
        aggregation_specs_needed = any(
            leaf_name.endswith(f"_{g}") for g in SUPPORTED_GROUPINGS
        ) and tree_path not in optree.tree_paths(aggregation_source_tree)

        if aggregation_specs_needed:
            # Use qualified name to identify source in the functions tree later.
            derived_aggregations_tree = upsert_path_and_value(
                tree=derived_aggregations_tree,
                tree_path=tree_path,
                value=AggregateByGroupSpec(
                    aggr="sum",
                    source_col=remove_group_suffix(leaf_name),
                ),
            )
        else:
            continue

    return derived_aggregations_tree


def _get_potential_aggregation_function_names_from_function_arguments(
    functions_tree: NestedFunctionDict,
) -> dict[str, Any]:
    """Get potential aggregation function names from function arguments.

    Note: Function accounts for namespaced function arguments, i.e. function arguments
    that are specified via their qualified instead of their simple name.

    Parameters
    ----------
    functions_tree
        Dictionary containing functions to build the DAG.

    Returns
    -------
    Dictionary containing potential aggregation targets.
    """
    current_tree = {}
    paths_of_functions_tree, flat_functions_tree = (
        optree.tree_flatten_with_path(functions_tree)
    )[:2]
    for func, tree_path in zip(flat_functions_tree, paths_of_functions_tree):
        for name in get_names_of_arguments_without_defaults(func):
            path_of_function_argument = _get_tree_path_from_source_col_name(
                name=name,
                current_namespace=tree_path[:-1],
            )
            current_tree = upsert_path_and_value(
                tree=current_tree,
                tree_path=path_of_function_argument,
            )
    return current_tree


def _annotations_for_aggregation(
    aggregation_method: str,
    source_col: str,
    namespace_of_function_to_derive: tuple[str],
    functions_tree: NestedFunctionDict,
    types_input_variables: dict[str, Any],
) -> dict[str, Any]:
    """Create annotations for derived aggregation functions."""
    annotations = {}

    path_of_source_col = _get_tree_path_from_source_col_name(
        name=source_col,
        current_namespace=namespace_of_function_to_derive,
    )
    accessor_source_col = optree.tree_accessors(
        create_tree_from_path_and_value(path_of_source_col),
        none_is_leaf=True,
    )[0]

    if aggregation_method == "count":
        annotations["return"] = int
    elif path_of_source_col in optree.tree_paths(functions_tree):
        # Source col is a function in the functions tree
        source_function = accessor_source_col(functions_tree)
        if "return" in source_function.__annotations__:
            annotations[source_col] = source_function.__annotations__["return"]
            annotations["return"] = _select_return_type(
                aggregation_method, annotations[source_col]
            )
        else:
            # TODO(@hmgaudecker): Think about how type annotations of aggregations
            # of user-provided input variables are handled
            # https://github.com/iza-institute-of-labor-economics/gettsim/issues/604
            pass
    elif path_of_source_col in optree.tree_paths(types_input_variables):
        # Source col is a basic input variable
        annotations[source_col] = accessor_source_col(types_input_variables)
        annotations["return"] = _select_return_type(
            aggregation_method, annotations[source_col]
        )
    else:
        # TODO(@hmgaudecker): Think about how type annotations of aggregations of
        # user-provided input variables are handled
        # https://github.com/iza-institute-of-labor-economics/gettsim/issues/604
        pass
    return annotations


def _select_return_type(aggregation_method: str, source_col_type: type) -> type:
    # Find out return type
    if (source_col_type == int) and (aggregation_method in ["any", "all"]):
        return_type = bool
    elif (source_col_type == bool) and (aggregation_method in ["sum"]):
        return_type = int
    else:
        return_type = source_col_type

    return return_type


def _create_one_aggregate_by_group_func(  # noqa: PLR0912
    aggregation_target: str,
    aggregation_method: str,
    source_col: str,
    annotations: dict[str, Any],
) -> DerivedFunction:
    """Create an aggregation function based on aggregation specification.

    Parameters
    ----------
    aggregation_target
        Name of the aggregation target.
    aggregation_method
        The aggregation method.
    source_col
        The source column.
    annotations
        The annotations for the derived function.

    Returns
    -------
    The derived function.

    """
    # Identify grouping level
    group_id = None
    for g in SUPPORTED_GROUPINGS:
        if aggregation_target.endswith(f"_{g}"):
            group_id = f"groupings__{g}_id"
    if not group_id:
        msg = format_errors_and_warnings(
            "Name of aggregated column needs to have a suffix "
            "indicating the group over which it is aggregated. "
            f"The name {aggregation_target} does not do so."
        )
        raise ValueError(msg)

    if aggregation_method == "count":

        @rename_arguments_and_add_annotations(
            mapper={"group_id": group_id}, annotations=annotations
        )
        def aggregate_by_group_func(group_id):
            return grouped_count(group_id)

    else:
        mapper = {
            "source_col": source_col,
            "group_id": group_id,
        }
        if aggregation_method == "sum":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_sum(source_col, group_id)

        elif aggregation_method == "mean":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_mean(source_col, group_id)

        elif aggregation_method == "max":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_max(source_col, group_id)

        elif aggregation_method == "min":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_min(source_col, group_id)

        elif aggregation_method == "any":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_any(source_col, group_id)

        elif aggregation_method == "all":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_all(source_col, group_id)

        else:
            msg = format_errors_and_warnings(
                f"Aggregation method {aggregation_method} is not implemented."
            )
            raise ValueError(msg)

    if aggregation_method == "count":
        derived_from = group_id
    else:
        derived_from = (source_col, group_id)

    return DerivedFunction(
        function=aggregate_by_group_func,
        leaf_name=aggregation_target,
        derived_from=derived_from,
    )


def _create_one_aggregate_by_p_id_func(
    aggregation_target: str,
    p_id_to_aggregate_by: str,
    source_col: str,
    aggregation_method: str,
    annotations: dict[str, Any],
) -> DerivedFunction:
    """Create one function that links variables across persons.

    Parameters
    ----------
    aggregation_target
        Name of the aggregation target.
    p_id_to_aggregate_by
        The column to aggregate by.
    source_col
        The source column.
    aggregation_method
        The aggregation method.
    annotations
        The annotations for the derived function.

    Returns
    -------
    The derived function.

    """
    # Define aggregation func
    if aggregation_method == "count":

        @rename_arguments_and_add_annotations(
            mapper={
                "p_id_to_aggregate_by": p_id_to_aggregate_by,
                "p_id_to_store_by": "groupings__p_id",
            },
            annotations=annotations,
        )
        def aggregate_by_p_id_func(p_id_to_aggregate_by, p_id_to_store_by):
            return count_by_p_id(p_id_to_aggregate_by, p_id_to_store_by)

    else:
        mapper = {
            "p_id_to_aggregate_by": p_id_to_aggregate_by,
            "p_id_to_store_by": "groupings__p_id",
            "column": source_col,
        }

        if aggregation_method == "sum":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return sum_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_method == "mean":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return mean_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_method == "max":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return max_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_method == "min":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return min_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_method == "any":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return any_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_method == "all":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return all_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        else:
            msg = format_errors_and_warnings(
                f"Aggregation method {aggregation_method} is not implemented."
            )
            raise ValueError(msg)

    if aggregation_method == "count":
        derived_from = p_id_to_aggregate_by
    else:
        derived_from = (source_col, p_id_to_aggregate_by)

    return DerivedFunction(
        function=aggregate_by_p_id_func,
        leaf_name=aggregation_target,
        derived_from=derived_from,
    )


def _get_tree_path_from_source_col_name(
    name: str,
    current_namespace: tuple[str],
) -> tuple[str]:
    """Get the tree path of a source column name that may be qualified or simple.

    This function returns the tree path of a source column name that may be a qualified
    or simple name. If the name is qualified, the path implied by the name is returned.
    Else, the current path plus the simple name is returned.

    Parameters
    ----------
    name
        The qualified or simple name.
    current_namespace
        The current namespace candidate for 'name'.

    Returns
    -------
    The path of 'name' in the tree.
    """
    if QUALIFIED_NAME_SEPARATOR in name:
        # 'name' is already namespaced.
        new_tree_path = name.split(QUALIFIED_NAME_SEPARATOR)
    else:
        # 'name' is not namespaced.
        new_tree_path = [*current_namespace, name]

    return tuple(new_tree_path)


def _fail_if_targets_not_in_functions_tree(
    functions_tree: NestedFunctionDict, targets_tree: NestedTargetDict
) -> None:
    """Fail if some target is not among functions.

    Parameters
    ----------
    functions_tree
        Dictionary containing functions to build the DAG.
    targets_tree
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.

    Raises
    ------
    ValueError
        Raised if any member of `targets` is not among functions.

    """
    targets_not_in_functions_tree = partition_tree_by_reference_tree(
        tree_to_partition=targets_tree,
        reference_tree=functions_tree,
    )[1]
    names_of_targets_not_in_functions = [
        ".".join(path)
        for path in optree.tree_paths(targets_not_in_functions_tree, none_is_leaf=True)
    ]
    if names_of_targets_not_in_functions:
        formatted = format_list_linewise(names_of_targets_not_in_functions)
        msg = format_errors_and_warnings(
            f"The following targets have no corresponding function:\n{formatted}"
        )
        raise ValueError(msg)
