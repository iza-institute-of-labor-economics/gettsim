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
    format_errors_and_warnings,
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    partition_tree_by_reference_tree,
    remove_group_suffix,
    rename_arguments_and_add_annotations,
    tree_get_by_path,
    tree_merge,
    tree_update,
)
from _gettsim.time_conversion import create_time_conversion_functions

if TYPE_CHECKING:
    from _gettsim.gettsim_typing import (
        NestedAggregationDict,
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
    environment : PolicyEnvironment
        The environment containing the functions tree and the specs for aggregation.
    targets_tree : NestedTargetDict
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.
    data_tree : NestedDataDict
        Names of columns in the input data.

    Returns
    -------
    all_functions : NestedFunctionDict
        The functions tree including derived functions.

    """
    # Create derived functions
    (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    ) = _create_derived_functions(
        environment=environment,
        targets_tree=targets_tree,
        data_tree=data_tree,
    )

    # Create groupings
    groupings = create_groupings()

    # Put all functions into a functions tree
    all_functions = functools.reduce(
        tree_merge,
        [
            aggregate_by_p_id_functions,
            time_conversion_functions,
            aggregate_by_group_functions,
            groupings,
        ],
        environment.policy_functions_tree,
    )

    _fail_if_targets_not_in_policy_functions_tree(all_functions, targets_tree)

    return all_functions


def _create_derived_functions(
    environment: PolicyEnvironment,
    targets_tree: NestedTargetDict,
    data_tree: NestedDataDict,
) -> tuple[NestedFunctionDict, NestedFunctionDict, NestedFunctionDict]:
    """
    Create functions that are derived from the user and internal functions.

    These include:
        - functions for converting to different time units
        - aggregation functions
        - combinations of these
    """
    current_policy_functions_tree = environment.policy_functions_tree

    # Create parent-child relationships
    aggregate_by_p_id_functions = _create_aggregate_by_p_id_functions(
        policy_functions_tree=current_policy_functions_tree,
        aggregations_tree_provided_by_env=environment.aggregations_tree,
    )

    # Create functions for different time units
    current_policy_functions_tree = tree_merge(
        current_policy_functions_tree,
        aggregate_by_p_id_functions,
    )
    time_conversion_functions = create_time_conversion_functions(
        policy_functions_tree=current_policy_functions_tree,
        data_tree=data_tree,
    )

    # Create aggregation functions
    current_policy_functions_tree = tree_merge(
        current_policy_functions_tree,
        time_conversion_functions,
    )
    aggregate_by_group_functions = _create_aggregate_by_group_functions(
        policy_functions_tree=current_policy_functions_tree,
        targets_tree=targets_tree,
        data_tree=data_tree,
        aggregations_tree_provided_by_env=environment.aggregations_tree,
    )

    return (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    )


def _create_aggregate_by_p_id_functions(
    policy_functions_tree: NestedFunctionDict,
    aggregations_tree_provided_by_env: NestedAggregationDict,
) -> NestedFunctionDict:
    """Create aggregation functions for linking variables across persons.

    Parameters
    ----------
    policy_functions_tree : NestedFunctionDict
        The functions tree.
    aggregations_tree_provided_by_env :
        The aggregations tree provided by the environment.
    """
    return _create_aggregation_functions(
        policy_functions_tree=policy_functions_tree,
        aggregations_tree=aggregations_tree_provided_by_env,
        aggregation_type="p_id",
    )


def _create_aggregate_by_group_functions(
    policy_functions_tree: NestedFunctionDict,
    targets_tree: NestedTargetDict,
    data_tree: NestedDataDict,
    aggregations_tree_provided_by_env: dict[str, Any],
) -> dict[str, DerivedFunction]:
    """Create aggregation functions."""

    # Add automated aggregation specs to aggregations tree
    automatically_created_aggregations_tree = _create_derived_aggregations_tree(
        policy_functions_tree=policy_functions_tree,
        target_tree=targets_tree,
        data_tree=data_tree,
    )

    # Add automated aggregation specs to aggregations tree
    full_aggregations_tree = tree_merge(
        automatically_created_aggregations_tree,
        aggregations_tree_provided_by_env,
    )

    return _create_aggregation_functions(
        policy_functions_tree=policy_functions_tree,
        aggregations_tree=full_aggregations_tree,
        aggregation_type="group",
    )


def _create_aggregation_functions(
    policy_functions_tree: NestedFunctionDict,
    aggregations_tree: NestedAggregationDict,
    aggregation_type: Literal["group", "p_id"],
) -> NestedFunctionDict:
    """Create aggregation functions."""

    derived_functions = {}

    _all_paths, _all_aggregation_specs, _ = optree.tree_flatten_with_path(
        aggregations_tree
    )

    expected_aggregation_spec_type = (
        AggregateByGroupSpec if aggregation_type == "group" else AggregateByPIDSpec
    )

    for tree_path, aggregation_spec in zip(_all_paths, _all_aggregation_specs):
        # Skip if aggregation spec is not the current aggregation type
        if not isinstance(aggregation_spec, expected_aggregation_spec_type):
            continue

        aggregation_target = tree_path[-1]
        aggregation_method = aggregation_spec.aggr
        qualified_name_source_col = QUALIFIED_NAME_SEPARATOR.join(
            _get_tree_path_from_source_col_name(
                name=aggregation_spec.source_col,
                current_namespace=tree_path[:-1],
            )
        )

        if aggregation_type == "group":
            derived_func = _create_one_aggregate_by_group_func(
                aggregation_target=aggregation_target,
                aggregation_method=aggregation_method,
                qualified_name_source_col=qualified_name_source_col,
                policy_functions_tree=policy_functions_tree,
            )
        else:
            p_id_to_aggregate_by = aggregation_spec.p_id_to_aggregate_by
            derived_func = _create_one_aggregate_by_p_id_func(
                aggregation_target=aggregation_target,
                p_id_to_aggregate_by=p_id_to_aggregate_by,
                qualified_name_source_col=qualified_name_source_col,
                aggregation_method=aggregation_method,
                policy_functions_tree=policy_functions_tree,
            )

        derived_functions = tree_update(
            derived_functions,
            tree_path,
            derived_func,
        )

    return derived_functions


def _create_derived_aggregations_tree(
    policy_functions_tree: NestedFunctionDict,
    target_tree: NestedTargetDict,
    data_tree: NestedDataDict,
) -> NestedAggregationDict:
    """Create automatic aggregation specs.

    Aggregation specifications are created automatically for summation aggregations.

    Parameters
    ----------
    policy_functions_tree :
        The functions tree.
    target_tree :
        The target tree.
    data_tree :
        The data tree.

    Returns
    -------
    derived_aggregations_tree :
        The aggregation specifications derived from the functions and data tree.

    Example
    -------
    If
    - `func_hh` is an argument of the functions in `policy_functions_tree`, or a target
    - and not represented by a function in `policy_functions_tree` or a data column in
        the input data
    then an automatic aggregation specification is created for the sum aggregation of
    `func` by household.
    """
    # Create target tree for aggregations. Aggregation target can be any target provided
    # by the user or any function argument.
    potential_target_tree = tree_merge(
        target_tree,
        _get_potential_aggregation_targets_from_function_arguments(
            policy_functions_tree
        ),
    )

    # Create source tree for aggregations. Source can be any already existing function
    # or data column.
    aggregation_source_tree = tree_merge(
        base_tree=policy_functions_tree,
        update_tree=data_tree,
    )

    # Create aggregation specs.
    derived_aggregations_tree = {}
    for tree_path in optree.tree_paths(potential_target_tree, none_is_leaf=True):
        leaf_name = tree_path[-1]

        # Don't create aggregation specs for targets that aren't groupings or
        # targets that already exist in the source tree.
        aggregation_specs_needed = any(
            leaf_name.endswith(f"_{g}") for g in SUPPORTED_GROUPINGS
        ) and tree_path not in optree.tree_paths(aggregation_source_tree)

        if aggregation_specs_needed:
            # Use qualified name to identify source in the functions tree later.

            agg_specs_single_function = AggregateByGroupSpec(
                aggr="sum",
                source_col=remove_group_suffix(leaf_name),
            )

            derived_aggregations_tree = tree_update(
                tree=derived_aggregations_tree,
                tree_path=tree_path,
                value=agg_specs_single_function,
            )
        else:
            continue

    return derived_aggregations_tree


def _get_potential_aggregation_targets_from_function_arguments(
    policy_functions_tree: NestedFunctionDict,
) -> dict[str, Any]:
    """Get potential aggregation targets from function arguments.

    Note: Function accounts for namespaced function arguments, i.e. function arguments
    that are specified via their qualified instead of their simple name.

    Parameters
    ----------
    policy_functions_tree : dict
        Dictionary containing functions to build the DAG.

    Returns
    -------
    potential_aggregation_targets : dict
        Dictionary containing potential aggregation targets.
    """
    current_tree = {}
    paths_of_policy_functions_tree, flat_policy_functions_tree, _ = (
        optree.tree_flatten_with_path(policy_functions_tree)
    )
    for func, tree_path in zip(
        flat_policy_functions_tree, paths_of_policy_functions_tree
    ):
        for name in get_names_of_arguments_without_defaults(func):
            path_of_function_argument = _get_tree_path_from_source_col_name(
                name=name,
                current_namespace=tree_path[:-1],
            )
            current_tree = tree_update(
                current_tree,
                path_of_function_argument,
            )
    return current_tree


def _annotations_for_aggregation(
    aggregation_method: str,
    qualified_name_source_col: str,
    policy_functions_tree: NestedFunctionDict,
    types_input_variables: dict[str, Any],
) -> dict[str, Any]:
    """Create annotations for derived aggregation functions."""
    annotations = {}
    path_source_col = tuple(qualified_name_source_col.split(QUALIFIED_NAME_SEPARATOR))
    if aggregation_method == "count":
        annotations["return"] = int
    elif path_source_col in optree.tree_paths(policy_functions_tree):
        # Source col is a function in the functions tree
        source_function = tree_get_by_path(policy_functions_tree, path_source_col)
        if "return" in source_function.__annotations__:
            annotations[qualified_name_source_col] = source_function.__annotations__[
                "return"
            ]
            annotations["return"] = _select_return_type(
                aggregation_method, annotations[qualified_name_source_col]
            )
        else:
            # TODO(@hmgaudecker): Think about how type annotations of aggregations
            # of user-provided input variables are handled
            # https://github.com/iza-institute-of-labor-economics/gettsim/issues/604
            pass
    elif path_source_col in optree.tree_paths(types_input_variables):
        # Source col is a basic input variable
        annotations[qualified_name_source_col] = tree_get_by_path(
            types_input_variables, path_source_col
        )
        annotations["return"] = _select_return_type(
            aggregation_method, annotations[qualified_name_source_col]
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
    qualified_name_source_col: str,
    policy_functions_tree: NestedFunctionDict,
) -> DerivedFunction:
    """Create an aggregation function based on aggregation specification.

    Parameters
    ----------
    aggregation_target : str
        Name of the aggregation target.
    aggregation_method : str
        The aggregation method.
    qualified_name_source_col : str
        The qualified source column name.
    policy_functions_tree: NestedFunctionDict
        Functions tree.

    Returns
    -------
    derived_function : DerivedFunction
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

    annotations = _annotations_for_aggregation(
        aggregation_method=aggregation_method,
        qualified_name_source_col=qualified_name_source_col,
        policy_functions_tree=policy_functions_tree,
        types_input_variables=TYPES_INPUT_VARIABLES,
    )

    if aggregation_method == "count":

        @rename_arguments_and_add_annotations(
            mapper={"group_id": group_id}, annotations=annotations
        )
        def aggregate_by_group_func(group_id):
            return grouped_count(group_id)

    else:
        mapper = {
            "qualified_name_source_col": qualified_name_source_col,
            "group_id": group_id,
        }
        if aggregation_method == "sum":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(qualified_name_source_col, group_id):
                return grouped_sum(qualified_name_source_col, group_id)

        elif aggregation_method == "mean":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(qualified_name_source_col, group_id):
                return grouped_mean(qualified_name_source_col, group_id)

        elif aggregation_method == "max":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(qualified_name_source_col, group_id):
                return grouped_max(qualified_name_source_col, group_id)

        elif aggregation_method == "min":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(qualified_name_source_col, group_id):
                return grouped_min(qualified_name_source_col, group_id)

        elif aggregation_method == "any":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(qualified_name_source_col, group_id):
                return grouped_any(qualified_name_source_col, group_id)

        elif aggregation_method == "all":

            @rename_arguments_and_add_annotations(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(qualified_name_source_col, group_id):
                return grouped_all(qualified_name_source_col, group_id)

        else:
            msg = format_errors_and_warnings(
                f"Aggregation method {aggregation_method} is not implemented."
            )
            raise ValueError(msg)

    if aggregation_method == "count":
        derived_from = group_id
    else:
        derived_from = (qualified_name_source_col, group_id)

    return DerivedFunction(
        aggregate_by_group_func,
        leaf_name=aggregation_target,
        derived_from=derived_from,
    )


def _create_one_aggregate_by_p_id_func(
    aggregation_target: str,
    p_id_to_aggregate_by: str,
    qualified_name_source_col: str,
    aggregation_method: str,
    policy_functions_tree: NestedFunctionDict,
) -> DerivedFunction:
    """Create one function that links variables across persons.

    Parameters
    ----------
    aggregation_target : str
        Name of the aggregation target.
    p_id_to_aggregate_by : str
        The column to aggregate by.
    qualified_name_source_col : str
        The qualified source column name.
    aggregation_method : str
        The aggregation method.
    policy_functions_tree: NestedFunctionDict
        Functions tree.

    Returns
    -------
    derived_function : DerivedFunction
        The derived function.

    """
    annotations = _annotations_for_aggregation(
        aggregation_method=aggregation_method,
        qualified_name_source_col=qualified_name_source_col,
        policy_functions_tree=policy_functions_tree,
        types_input_variables=TYPES_INPUT_VARIABLES,
    )

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
            "column": qualified_name_source_col,
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
        derived_from = (qualified_name_source_col, p_id_to_aggregate_by)

    return DerivedFunction(
        aggregate_by_p_id_func,
        leaf_name=aggregation_target,
        derived_from=derived_from,
    )


def _get_tree_path_from_source_col_name(
    name: str,
    current_namespace: list[str] | tuple[str],
) -> tuple[str]:
    """Get the tree path of a source column name that may be qualified or simple.

    This function returns the tree path of a source column name that may be a qualified
    or simple name. If the name is qualified, the path implied by the name is returned.
    Else, the current path plus the simple name is returned.

    Parameters
    ----------
    name : str
        The qualified or simple name.
    current_namespace : list[str]
        The current namespace candidate for 'name'.

    Returns
    -------
    path : tuple[str]
        The path of 'name' in the tree.
    """
    if QUALIFIED_NAME_SEPARATOR in name:
        # 'name' is already namespaced.
        new_tree_path = name.split(QUALIFIED_NAME_SEPARATOR)
    else:
        # 'name' is not namespaced.
        new_tree_path = [*current_namespace, name]

    return tuple(new_tree_path)


def _fail_if_targets_not_in_policy_functions_tree(
    policy_functions_tree: NestedFunctionDict, targets_tree: NestedTargetDict
) -> None:
    """Fail if some target is not among functions.

    Parameters
    ----------
    policy_functions_tree : dict
        Dictionary containing functions to build the DAG.
    targets_tree : dict
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.

    Raises
    ------
    ValueError
        Raised if any member of `targets` is not among functions.

    """
    targets_not_in_functions_tree = partition_tree_by_reference_tree(
        tree_to_partition=targets_tree,
        reference_tree=policy_functions_tree,
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
