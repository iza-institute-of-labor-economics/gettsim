from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import flatten_dict
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
from _gettsim.function_types import DerivedFunction, GroupByFunction
from _gettsim.shared import (
    format_errors_and_warnings,
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    insert_path_and_value,
    partition_tree_by_reference_tree,
    remove_group_suffix,
    rename_arguments_and_add_annotations,
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
    current_functions_tree = upsert_tree(
        base=aggregate_by_p_id_functions,
        to_upsert=environment.functions_tree,
    )

    # Create functions for different time units
    time_conversion_functions = create_time_conversion_functions(
        functions_tree=current_functions_tree,
        data_tree=data_tree,
    )
    current_functions_tree = upsert_tree(
        base=time_conversion_functions,
        to_upsert=current_functions_tree,
    )

    # Create aggregation functions
    aggregate_by_group_functions = _create_aggregate_by_group_functions(
        functions_tree=current_functions_tree,
        targets_tree=targets_tree,
        data_tree=data_tree,
        aggregations_tree_provided_by_env=environment.aggregation_specs_tree,
    )
    current_functions_tree = upsert_tree(
        base=aggregate_by_group_functions,
        to_upsert=current_functions_tree,
    )

    _fail_if_targets_not_in_functions_tree(current_functions_tree, targets_tree)

    return current_functions_tree


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
        base=automatically_created_aggregations_tree,
        to_upsert=aggregations_tree_provided_by_env,
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

    group_by_functions_tree = flatten_dict.unflatten(
        {
            path: func
            for path, func in flatten_dict.flatten(functions_tree).items()
            if isinstance(func, GroupByFunction)
        }
    )

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
            namespace=tree_path[:-1],
            functions_tree=functions_tree,
            types_input_variables=TYPES_INPUT_VARIABLES,
        )

        if aggregation_type == "group":
            groupby_id = get_groupby_id(
                target_path=tree_path,
                group_by_functions_tree=group_by_functions_tree,
            )
            derived_func = _create_one_aggregate_by_group_func(
                aggregation_target=tree_path[-1],
                aggregation_method=aggregation_spec.aggr,
                source_col=aggregation_spec.source_col,
                annotations=annotations,
                groupby_id=groupby_id,
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

        out_tree = insert_path_and_value(
            base=out_tree,
            path_to_insert=tree_path,
            value_to_insert=derived_func,
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
        base=target_tree,
        to_upsert=_get_potential_aggregation_function_names_from_function_arguments(
            functions_tree
        ),
    )

    # Create source tree for aggregations. Source can be any already existing function
    # or data column.
    aggregation_source_tree = upsert_tree(
        base=functions_tree,
        to_upsert=data_tree,
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
            derived_aggregations_tree = insert_path_and_value(
                base=derived_aggregations_tree,
                path_to_insert=tree_path,
                value_to_insert=AggregateByGroupSpec(
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
                namespace=tree_path[:-1],
            )
            current_tree = insert_path_and_value(
                base=current_tree,
                path_to_insert=path_of_function_argument,
            )
    return current_tree


def _annotations_for_aggregation(
    aggregation_method: str,
    source_col: str,
    namespace: tuple[str],
    functions_tree: NestedFunctionDict,
    types_input_variables: dict[str, Any],
) -> dict[str, Any]:
    """Create annotations for derived aggregation functions."""
    annotations = {}

    path_to_source_col = _get_tree_path_from_source_col_name(
        name=source_col,
        namespace=namespace,
    )
    flat_functions = flatten_dict.flatten(functions_tree)
    flat_types_input_variables = flatten_dict.flatten(types_input_variables)

    if aggregation_method == "count":
        annotations["return"] = int
    elif path_to_source_col in flat_functions:
        # Source col is a function in the functions tree
        source_function = flat_functions[path_to_source_col]
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
    elif path_to_source_col in flat_types_input_variables:
        # Source col is a basic input variable
        annotations[source_col] = flat_types_input_variables[path_to_source_col]
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


def _create_one_aggregate_by_group_func(
    aggregation_target: str,
    aggregation_method: str,
    source_col: str,
    annotations: dict[str, Any],
    groupby_id: str,
) -> DerivedFunction:
    """Create an aggregation function based on aggregation specification.

    Parameters
    ----------
    aggregation_target
        Leaf name of the aggregation target.
    aggregation_method
        The aggregation method.
    source_col
        The qualified source column name.
    annotations
        The annotations for the derived function.
    groupby_id
        The groupby id.

    Returns
    -------
    The derived function.

    """
    if aggregation_method == "count":

        @rename_arguments_and_add_annotations(
            mapper={"groupby_id": groupby_id}, annotations=annotations
        )
        def aggregate_by_group_func(groupby_id):
            return grouped_count(groupby_id)

    else:
        mapper = {
            "source_col": source_col,
            "groupby_id": groupby_id,
        }
        if aggregation_method == "sum":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, groupby_id):
                return grouped_sum(source_col, groupby_id)

        elif aggregation_method == "mean":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, groupby_id):
                return grouped_mean(source_col, groupby_id)

        elif aggregation_method == "max":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, groupby_id):
                return grouped_max(source_col, groupby_id)

        elif aggregation_method == "min":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, groupby_id):
                return grouped_min(source_col, groupby_id)

        elif aggregation_method == "any":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, groupby_id):
                return grouped_any(source_col, groupby_id)

        elif aggregation_method == "all":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, groupby_id):
                return grouped_all(source_col, groupby_id)

        else:
            msg = format_errors_and_warnings(
                f"Aggregation method {aggregation_method} is not implemented."
            )
            raise ValueError(msg)

    if aggregation_method == "count":
        derived_from = groupby_id
    else:
        derived_from = (source_col, groupby_id)

    return DerivedFunction(
        function=aggregate_by_group_func,
        leaf_name=aggregation_target,
        derived_from=derived_from,
    )


def get_groupby_id(
    target_path: tuple[str],
    group_by_functions_tree: NestedFunctionDict,
) -> str:
    """Get the groupby id for an aggregation target.

    The groupby id is the id of the group over which the aggregation is performed. If
    there are multiple groupby ids with the same suffix, the function takes the id
    that shares the first part of the path (uppermost level of namespace) with the
    aggregation target.

    Raises
    ------
    ValueError
        Raised if no groupby id is found.

    Parameters
    ----------
    target_path
        The aggregation target.
    group_by_functions_tree
        The groupby functions tree.

    Returns
    -------
    The groupby id.
    """
    groupby_id = None
    nice_target_name = ".".join(target_path)

    flat_group_by_functions_tree = flatten_dict.flatten(group_by_functions_tree)
    for g in SUPPORTED_GROUPINGS:
        if target_path[-1].endswith(f"_{g}"):
            candidates = {
                path: func
                for path, func in flat_group_by_functions_tree.items()
                if path[-1] == f"{g}_id"
            }
            groupby_id = _select_groupby_id_from_candidates(
                candidates=candidates,
                target_path=target_path,
                nice_target_name=nice_target_name,
            )
            break

    if not groupby_id:
        msg = format_errors_and_warnings(
            "Name of aggregated column needs to have a suffix "
            "indicating the group over which it is aggregated. "
            f"The name {nice_target_name} does not do so."
        )
        raise ValueError(msg)

    return groupby_id


def _select_groupby_id_from_candidates(
    candidates: dict[str, Any],
    target_path: tuple[str],
    nice_target_name: str,
) -> str:
    """Select the groupby id from the candidates.

    If there are multiple candidates, the function takes the one that shares the
    first part of the path (uppermost level of namespace) with the aggregation target.

    Raises
    ------
    ValueError
        Raised if the groupby id is ambiguous.

    Parameters
    ----------
    candidates
        The candidates.
    target_path
        The target path.
    nice_target_name
        The nice target name.

    Returns
    -------
    The groupby id.
    """
    if len(candidates) > 1:
        # Take candidate with same parent namespace
        candidates = {
            path: func for path, func in candidates.items() if path[0] == target_path[0]
        }
        if len(candidates) > 1:
            msg = format_errors_and_warnings(
                f"""
                Grouping ID for target {nice_target_name} is ambiguous. Grouping
                IDs must be unique at the uppermost level of the functions tree.
                """
            )
            raise ValueError(msg)
    return QUALIFIED_NAME_SEPARATOR.join(candidates.keys()[0])


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
                "p_id_to_store_by": "demographics__p_id",
            },
            annotations=annotations,
        )
        def aggregate_by_p_id_func(p_id_to_aggregate_by, p_id_to_store_by):
            return count_by_p_id(p_id_to_aggregate_by, p_id_to_store_by)

    else:
        mapper = {
            "p_id_to_aggregate_by": p_id_to_aggregate_by,
            "p_id_to_store_by": "demographics__p_id",
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
    namespace: tuple[str],
) -> tuple[str]:
    """Get the tree path of a source column name that may be qualified or simple.

    This function returns the tree path of a source column name that may be a qualified
    or simple name. If the name is qualified, the path implied by the name is returned.
    Else, the current path plus the simple name is returned.

    Parameters
    ----------
    name
        The qualified or simple name.
    namespace
        The namespace where 'name' is located.

    Returns
    -------
    The path of 'name' in the tree.
    """
    if QUALIFIED_NAME_SEPARATOR in name:
        # 'name' is already namespaced.
        new_tree_path = name.split(QUALIFIED_NAME_SEPARATOR)
    else:
        # 'name' is not namespaced.
        new_tree_path = [*namespace, name]

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
