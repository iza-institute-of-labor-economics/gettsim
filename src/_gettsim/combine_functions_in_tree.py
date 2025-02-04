from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

import optree

from _gettsim.aggregation import (
    AggregateByGroupSpec,
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
    format_list_linewise,
    get_by_path,
    get_names_of_arguments_without_defaults,
    merge_nested_dicts,
    remove_group_suffix,
    rename_arguments_and_add_annotations,
    tree_path_exists,
    tree_update,
)
from _gettsim.time_conversion import create_time_conversion_functions

if TYPE_CHECKING:
    from _gettsim.gettsim_typing import (
        NestedDataDict,
        NestedFunctionDict,
        NestedTargetDict,
    )
    from _gettsim.policy_environment import PolicyEnvironment


def combine_policy_functions_and_derived_functions(
    environment: PolicyEnvironment,
    targets: NestedTargetDict,
    data: NestedDataDict,
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
    targets : NestedTargetDict
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.
    data : NestedDataDict
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
        environment,
        targets,
        data,
    )

    # Create groupings
    groupings = create_groupings()

    all_functions = functools.reduce(
        merge_nested_dicts,
        [
            aggregate_by_p_id_functions,
            time_conversion_functions,
            aggregate_by_group_functions,
            groupings,
        ],
        environment.policy_functions_tree,
    )

    _fail_if_targets_are_not_among_functions(all_functions, targets)

    return all_functions


def _create_derived_functions(
    environment: PolicyEnvironment,
    targets: NestedTargetDict,
    data: NestedDataDict,
) -> tuple[NestedFunctionDict, NestedFunctionDict, NestedFunctionDict]:
    """
    Create functions that are derived from the user and internal functions.

    This includes:
    - functions for converting to different time units
    - aggregation functions
    - combinations of these
    """
    # Create parent-child relationships
    aggregate_by_p_id_functions = _create_aggregate_by_p_id_functions(
        environment.policy_functions_tree,
        environment.aggregate_by_p_id_specs,
    )

    # Create functions for different time units
    all_functions = merge_nested_dicts(
        environment.policy_functions_tree,
        aggregate_by_p_id_functions,
    )
    time_conversion_functions = create_time_conversion_functions(
        all_functions,
        data,
    )

    # Create aggregation functions
    all_functions = merge_nested_dicts(
        all_functions,
        time_conversion_functions,
    )
    aggregate_by_group_functions = _create_aggregate_by_group_functions(
        all_functions,
        targets,
        data,
        environment.aggregate_by_group_specs,
    )

    return (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    )


def _create_aggregate_by_group_functions(
    functions_tree: NestedFunctionDict,
    targets: NestedTargetDict,
    data: NestedDataDict,
    aggregation_dicts_provided_by_env: dict[str, Any],
) -> dict[str, DerivedFunction]:
    """Create aggregation functions."""
    automatically_created_aggregation_dicts = (
        _create_derived_aggregation_specifications(
            functions_tree=functions_tree,
            user_targets=targets,
            data=data,
        )
    )

    # Add automated aggregation specs.
    # Note: For duplicate keys, explicitly set specs are treated with higher priority
    # than automated specs.
    all_aggregate_by_group_specs = merge_nested_dicts(
        automatically_created_aggregation_dicts,
        aggregation_dicts_provided_by_env,
    )

    derived_functions = {}
    _all_paths, _all_aggregation_specs, _ = optree.tree_flatten_with_path(
        all_aggregate_by_group_specs
    )
    for path, aggregation_spec in zip(_all_paths, _all_aggregation_specs):
        # Unpack aggregation specification
        aggregation_target = path[-1]
        aggregation_method = aggregation_spec.aggr
        qualified_name_source_col = QUALIFIED_NAME_SEPARATOR.join(
            _get_path_from_argument_name(
                argument_name=aggregation_spec.source_col,
                current_namespace=path[:-1],
            )
        )
        _fail_if_aggregation_target_is_namespaced(target=aggregation_target)

        derived_func = _create_one_aggregate_by_group_func(
            aggregation_target=aggregation_target,
            aggregation_method=aggregation_method,
            qualified_name_source_col=qualified_name_source_col,
            functions_tree=functions_tree,
        )

        derived_functions = tree_update(
            derived_functions,
            path,
            derived_func,
        )

    return derived_functions


def _create_derived_aggregation_specifications(
    functions_tree: NestedFunctionDict,
    user_targets: NestedTargetDict,
    data: NestedDataDict,
) -> dict[str, Any]:
    """Create automatic aggregation specs.

    Aggregation specifications are created automatically for summation aggregations.

    Example: If
        - `func_hh` is an argument of the functions in `functions_tree`, or a target
        - and not represented by a function in `functions_tree` or a data column in the
          input data
    then an automatic aggregation specification is created for the sum aggregation of
    `func` by household.
    """
    # Create target tree for aggregations. Aggregation target can be any target provided
    # by the user or any function argument.
    potential_target_tree = merge_nested_dicts(
        user_targets,
        _get_potential_aggregation_targets_from_function_arguments(functions_tree),
    )

    # Create potential source tree for aggregations. Source can be any already existing
    # function or data column.
    aggregation_source_tree = merge_nested_dicts(
        base_dict=functions_tree,
        update_dict=data,
    )

    # Create aggregation specs.
    all_agg_specs = {}
    for path in optree.tree_paths(potential_target_tree, none_is_leaf=True):
        leaf_name = path[-1]

        # Don't create aggregation specs for targets that aren't groupings or
        # targets that already exist in the source tree.
        aggregation_specs_needed = any(
            leaf_name.endswith(f"_{g}") for g in SUPPORTED_GROUPINGS
        ) and not tree_path_exists(aggregation_source_tree, path)

        if aggregation_specs_needed:
            # Use qualified name to identify source in the functions tree later.

            agg_specs_single_function = AggregateByGroupSpec(
                aggr="sum",
                source_col=remove_group_suffix(leaf_name),
            )

            all_agg_specs = tree_update(
                tree=all_agg_specs,
                path=path,
                value=agg_specs_single_function,
            )
        else:
            continue

    return all_agg_specs


def _get_potential_aggregation_targets_from_function_arguments(
    functions_tree: NestedFunctionDict,
) -> dict[str, Any]:
    """Get potential aggregation targets from function arguments.

    Note: Function accounts for namespaced function arguments, i.e. function arguments
    that are specified via their qualified instead of their simple name.

    Parameters
    ----------
    functions_tree : dict
        Dictionary containing functions to build the DAG.

    Returns
    -------
    potential_aggregation_targets : dict
        Dictionary containing potential aggregation targets.
    """
    current_tree = {}
    paths_of_functions_tree, flat_functions_tree, _ = optree.tree_flatten_with_path(
        functions_tree
    )
    for func, path in zip(flat_functions_tree, paths_of_functions_tree):
        for name in get_names_of_arguments_without_defaults(func):
            path_of_function_argument = _get_path_from_argument_name(
                argument_name=name,
                current_namespace=path[:-1],
            )
            current_tree = tree_update(
                current_tree,
                path_of_function_argument,
            )
    return current_tree


def _annotations_for_aggregation(
    aggregation_method: str,
    source_col: str,
    functions_tree: NestedFunctionDict,
    types_input_variables: dict[str, Any],
) -> dict[str, Any]:
    """Create annotations for derived aggregation functions."""
    annotations = {}
    path_source_col = source_col.split(QUALIFIED_NAME_SEPARATOR)

    if aggregation_method == "count":
        annotations["return"] = int
    elif tree_path_exists(functions_tree, path_source_col):
        # Source col is a function in the functions tree
        source_function = get_by_path(functions_tree, path_source_col)
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
    elif tree_path_exists(types_input_variables, path_source_col):
        # Source col is a basic input variable
        annotations[source_col] = get_by_path(types_input_variables, path_source_col)
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
    qualified_name_source_col: str,
    functions_tree: NestedFunctionDict,
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
    functions_tree: NestedFunctionDict
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
        raise ValueError(
            "Name of aggregated column needs to have a suffix "
            "indicating the group over which it is aggregated. "
            f"The name {aggregation_target} does not do so."
        )

    annotations = _annotations_for_aggregation(
        aggregation_method=aggregation_method,
        source_col=qualified_name_source_col,
        functions_tree=functions_tree,
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
            "source_col": qualified_name_source_col,
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
            raise ValueError(
                f"Aggregation method {aggregation_method} is not implemented."
            )

    if aggregation_method == "count":
        derived_from = group_id
    else:
        derived_from = (qualified_name_source_col, group_id)

    return DerivedFunction(
        aggregate_by_group_func,
        leaf_name=aggregation_target,
        derived_from=derived_from,
    )


def _create_aggregate_by_p_id_functions(
    functions_tree: NestedFunctionDict,
    aggregation_dicts_provided_by_env: dict[str, Any],
) -> NestedFunctionDict:
    """Create function dict with functions that link variables across persons."""
    derived_functions = {}

    _all_paths, _all_aggregation_specs, _ = optree.tree_flatten_with_path(
        aggregation_dicts_provided_by_env
    )
    for path, aggregation_spec in zip(_all_paths, _all_aggregation_specs):
        # Unpack aggregation specification
        aggregation_target = path[-1]
        p_id_to_aggregate_by = aggregation_spec.p_id_to_aggregate_by
        aggregation_method = aggregation_spec.aggr
        qualified_name_source_col = QUALIFIED_NAME_SEPARATOR.join(
            _get_path_from_argument_name(
                argument_name=aggregation_spec.source_col,
                current_namespace=path[:-1],
            )
        )
        _fail_if_aggregation_target_is_namespaced(target=aggregation_target)

        derived_func = _create_one_aggregate_by_p_id_func(
            aggregation_target=aggregation_target,
            p_id_to_aggregate_by=p_id_to_aggregate_by,
            qualified_name_source_col=qualified_name_source_col,
            aggregation_method=aggregation_method,
            functions_tree=functions_tree,
        )
        derived_functions = tree_update(derived_functions, path, derived_func)

    return derived_functions


def _create_one_aggregate_by_p_id_func(
    aggregation_target: str,
    p_id_to_aggregate_by: str,
    qualified_name_source_col: str,
    aggregation_method: str,
    functions_tree: NestedFunctionDict,
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
    functions_tree: NestedFunctionDict
        Functions tree.

    Returns
    -------
    derived_function : DerivedFunction
        The derived function.

    """
    annotations = _annotations_for_aggregation(
        aggregation_method=aggregation_method,
        source_col=qualified_name_source_col,
        functions_tree=functions_tree,
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
            msg = f"Aggregation method {aggregation_method} is not implemented."
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


def _get_path_from_argument_name(
    argument_name: str,
    current_namespace: list[str] | tuple[str],
) -> tuple[str]:
    """Get a path from an argument name that may or may not be namespaced.

    If the argument name is namespaced, the path implied by the argument name is
    returned. Else, the current path plus the argument nameis returned.

    Parameters
    ----------
    argument_name : str
        The argument name.
    current_namespace : list[str]
        The current namespace candidate for 'argument_name'.

    Returns
    -------
    path : tuple[str]
        The path.
    """
    if QUALIFIED_NAME_SEPARATOR in argument_name:
        # Source col is already namespaced.
        new_path = argument_name.split(QUALIFIED_NAME_SEPARATOR)
    else:
        # Source col is not namespaced.
        new_path = [*current_namespace, argument_name]

    return tuple(new_path)


def _fail_if_targets_are_not_among_functions(
    functions: NestedFunctionDict, targets: NestedTargetDict
) -> None:
    """Fail if some target is not among functions.

    Parameters
    ----------
    functions : dict
        Dictionary containing functions to build the DAG.
    targets : dict
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.

    Raises
    ------
    ValueError
        Raised if any member of `targets` is not among functions.

    """
    accessors = optree.tree_accessors(targets, none_is_leaf=True)
    targets_not_in_functions = []
    for acc in accessors:
        try:
            acc(functions)
        except KeyError:
            qualified_name = QUALIFIED_NAME_SEPARATOR.join(acc.path)
            targets_not_in_functions.append(qualified_name)

    if targets_not_in_functions:
        formatted = format_list_linewise(targets_not_in_functions)
        raise ValueError(
            f"The following targets have no corresponding function:\n{formatted}"
        )


def _fail_if_aggregation_target_is_namespaced(target: str) -> None:
    """Fail if aggregation target is namespaced.

    The namespace of aggregation targets is automatically determined by the position of
    the aggregation specification in the tree.

    Parameters
    ----------
    target : str
        The target to check.

    Raises
    ------
    ValueError
        Raised if the target is namespaced.

    """
    if QUALIFIED_NAME_SEPARATOR in target:
        raise ValueError(
            f"""
            Aggregation target {target} must not be namespaced. Please provide a simple
            name. The qualified name of the target is determined by the position of the
            aggregation specification in the tree.
            """
        )
