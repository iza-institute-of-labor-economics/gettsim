from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any

import numpy
from optree import tree_flatten_with_path

from _gettsim.aggregation import (
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
    SUPPORTED_GROUPINGS,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.functions.derived_function import DerivedFunction
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.groupings import create_groupings
from _gettsim.shared import (
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    merge_nested_dicts,
    remove_group_suffix,
    tree_flatten_with_qualified_name,
    tree_to_dict_with_qualified_name,
    tree_update,
)
from _gettsim.time_conversion import create_time_conversion_functions

if TYPE_CHECKING:
    from _gettsim.policy_environment import PolicyEnvironment


def add_derived_functions_to_functions_tree(
    environment: PolicyEnvironment,
    targets: dict[str, Any],
    data: dict[str, Any],
) -> dict[str, Any]:
    """Create the functions tree including derived functions.

    Create the functions tree by vectorizing all functions, and adding time conversion
    functions, aggregation functions, and combinations of these.

    Check that all targets have a corresponding function in the functions tree or can be
    taken from the data.

    Parameters
    ----------
    environment : PolicyEnvironment
        The environment containing the functions tree and the specs for aggregation.
    targets : dict
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.
    data : dict
        The data dictionary containing the input columns.

    Returns
    -------
    all_functions : dict
        The functions tree including derived functions.

    """
    names_of_columns_in_data, _, _ = tree_flatten_with_qualified_name(data)

    # Create derived functions
    (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    ) = _create_derived_functions(
        environment,
        targets,
        names_of_columns_in_data,
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
        environment.functions_tree,
    )

    _fail_if_targets_are_not_among_functions(all_functions, targets)

    return all_functions


def filter_overridden_functions(
    functions: dict[str, Any], data: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Filter functions that are overridden by input columns.

    Parameters
    ----------
    functions : dict
        Dictionary containing functions to build the DAG.
    data : dict
        Dictionary containing the input columns.

    Returns
    -------
    functions_not_overridden : dict
        All functions except the ones that are overridden by an input column.
    functions_overridden : dict
        Functions that are overridden by an input column.

    """
    functions_not_overridden = {}
    functions_overridden = {}

    names_of_columns_in_data, _, _ = tree_flatten_with_qualified_name(data)
    function_paths, functions_leafs, _ = tree_flatten_with_path(functions)

    for name, func in zip(function_paths, functions_leafs):
        qualified_name = "__".join(name)
        if qualified_name in names_of_columns_in_data:
            functions_overridden = tree_update(
                functions_overridden,
                name,
                func,
            )
        else:
            functions_not_overridden = tree_update(
                functions_not_overridden,
                name,
                func,
            )

    return functions_not_overridden, functions_overridden


def _create_derived_functions(
    environment: PolicyEnvironment,
    targets: dict[str, Any],
    names_of_columns_in_data: list[str],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """
    Create functions that are derived from the user and internal functions.

    This includes:
    - functions for converting to different time units
    - aggregation functions
    - combinations of these
    """
    # Create parent-child relationships
    aggregate_by_p_id_functions = _create_aggregate_by_p_id_functions(
        environment.functions_tree,
        environment.aggregate_by_p_id_specs,
    )

    # Create functions for different time units
    funcs_with_p_id_aggregation = merge_nested_dicts(
        environment.functions_tree,
        aggregate_by_p_id_functions,
    )
    time_conversion_functions = create_time_conversion_functions(
        funcs_with_p_id_aggregation,
        names_of_columns_in_data,
    )

    # Create aggregation functions
    funcs_with_time_conversion = merge_nested_dicts(
        funcs_with_p_id_aggregation,
        time_conversion_functions,
    )
    aggregate_by_group_functions = _create_aggregate_by_group_functions(
        funcs_with_time_conversion,
        targets,
        names_of_columns_in_data,
        environment.aggregate_by_group_specs,
    )

    return (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    )


def _create_aggregate_by_group_functions(
    functions_tree: dict[str, Any],
    targets: dict[str, Any],
    data_cols: list[str],
    aggregate_by_group_specs: dict[str, Any],
) -> dict[str, DerivedFunction]:
    """Create aggregation functions."""

    aggregation_dicts_provided_by_env = _get_aggregation_dicts(aggregate_by_group_specs)
    automatically_created_aggregation_dicts = (
        _create_derived_aggregation_specifications(
            functions_tree=functions_tree,
            targets=targets,
            data_cols=data_cols,
        )
    )

    # Add automated aggregation specs.
    # Note: For duplicate keys, explicitly set specs are treated with higher priority
    # than automated specs.
    full_aggregate_by_group_spec = merge_nested_dicts(
        automatically_created_aggregation_dicts,
        aggregation_dicts_provided_by_env,
    )

    derived_functions = {}
    for module, agg_dicts_of_module in full_aggregate_by_group_spec.items():
        for func_name, agg_spec in agg_dicts_of_module.items():
            _check_agg_specs_validity(
                agg_specs=agg_spec, agg_col=func_name, module=module
            )
            module_path = module.split("__")
            derived_func = _create_one_aggregate_by_group_func(
                module_path=module_path,
                new_function_name=func_name,
                agg_specs=agg_spec,
                functions_tree=functions_tree,
            )
            function_path = [*module_path, func_name]
            derived_functions = tree_update(
                derived_functions, function_path, derived_func
            )

    return derived_functions


def _create_derived_aggregation_specifications(
    functions_tree: dict[str, Any],
    targets: dict[str, Any],
    data_cols: list[str],
) -> dict[str, Any]:
    """Create automatic aggregation specs.

    Aggregation specifications are created automatically for summation aggregations.

    Example: If
        - `func_hh` is an argument of the functions in `functions_tree`, or
          a target
        - and not represented by a function in `functions_tree` or a data
          column in the input data
    then an automatic aggregation specification is created for the sum aggregation of
    `func` by household.
    """
    # Make specs for automated sum aggregation
    names_to_functions = tree_to_dict_with_qualified_name(functions_tree)
    names_to_targets = tree_to_dict_with_qualified_name(targets)

    potential_source_cols = list(names_to_functions.keys()) + data_cols
    potential_agg_targets = set(
        [
            arg
            for func in names_to_functions.values()
            for arg in get_names_of_arguments_without_defaults(func)
        ]
        + list(names_to_targets.keys())
    )

    automated_sum_aggregate_by_group_cols = [
        col
        for col in potential_agg_targets
        if (col not in names_to_functions)
        and any(col.endswith(f"_{g}") for g in SUPPORTED_GROUPINGS)
        and (remove_group_suffix(col) in potential_source_cols)
    ]

    automated_sum_aggregate_by_group_specs = {}
    for agg_col in automated_sum_aggregate_by_group_cols:
        path = agg_col.split("__")
        func_name = path[-1]
        # Create module name for path in tree; None if func is in main namespace
        module_name = "__".join(path[:-1]) if len(path) > 1 else None
        update_dict = {"aggr": "sum", "source_col": remove_group_suffix(agg_col)}
        automated_sum_aggregate_by_group_specs = tree_update(
            automated_sum_aggregate_by_group_specs,
            [module_name, func_name] if module_name else [func_name],
            update_dict,
        )

    return automated_sum_aggregate_by_group_specs


def rename_arguments(func=None, mapper=None, annotations=None):
    if not annotations:
        annotations = {}

    def decorator_rename_arguments(func):
        old_parameters = dict(inspect.signature(func).parameters)
        parameters = []
        for name, param in old_parameters.items():
            if name in mapper:
                parameters.append(param.replace(name=mapper[name]))
            else:
                parameters.append(param)

        signature = inspect.Signature(parameters=parameters)

        reverse_mapper = {v: k for k, v in mapper.items()}

        @functools.wraps(func)
        def wrapper_rename_arguments(*args, **kwargs):
            internal_kwargs = {}
            for name, value in kwargs.items():
                if name in reverse_mapper:
                    internal_kwargs[reverse_mapper[name]] = value
                elif name not in mapper:
                    internal_kwargs[name] = value
            return func(*args, **internal_kwargs)

        wrapper_rename_arguments.__signature__ = signature
        wrapper_rename_arguments.__annotations__ = annotations

        return wrapper_rename_arguments

    if callable(func):
        return decorator_rename_arguments(func)
    else:
        return decorator_rename_arguments


def _check_agg_specs_validity(agg_specs, agg_col, module):
    if "aggr" not in agg_specs:
        raise KeyError(
            f"""`aggr` key is missing for aggregation column {agg_col} in module
             {module}."""
        )
    if agg_specs["aggr"] != "count":
        if "source_col" not in agg_specs:
            raise KeyError(
                f"""`source_col` key is missing for aggregation column {agg_col} in
                 module {module}."""
            )


def _annotations_for_aggregation(
    aggregation_type: str,
    source_col: str,
    qualified_name_source_col: str,
    qualified_names_to_functions_dict: dict[str, PolicyFunction],
):
    """Create annotations for derived aggregation functions."""

    annotations = {}

    if aggregation_type == "count":
        annotations["return"] = int
    else:
        if (
            qualified_name_source_col in qualified_names_to_functions_dict
            and "return"
            in qualified_names_to_functions_dict[
                qualified_name_source_col
            ].__annotations__
        ):
            # Find out source col type to infer return type
            annotations[source_col] = qualified_names_to_functions_dict[
                qualified_name_source_col
            ].__annotations__["return"]

            # Find out return type
            annotations["return"] = _select_return_type(
                aggregation_type, annotations[source_col]
            )
        elif source_col in TYPES_INPUT_VARIABLES:
            annotations[source_col] = TYPES_INPUT_VARIABLES[source_col]

            # Find out return type
            annotations["return"] = _select_return_type(
                aggregation_type, annotations[source_col]
            )
        else:
            # TODO(@hmgaudecker): Think about how type annotations of aggregations of
            #     user-provided input variables are handled
            # https://github.com/iza-institute-of-labor-economics/gettsim/issues/604
            pass
    return annotations


def _select_return_type(aggr, source_col_type):
    # Find out return type
    if (source_col_type == int) and (aggr in ["any", "all"]):
        return_type = bool
    elif (source_col_type == bool) and (aggr in ["sum"]):
        return_type = int
    else:
        return_type = source_col_type

    return return_type


def _create_one_aggregate_by_group_func(  # noqa: PLR0912
    module_path: list[str],
    new_function_name: str,
    agg_specs: dict[str, str],
    functions_tree: dict[str, PolicyFunction],
) -> DerivedFunction:
    """Create an aggregation function based on aggregation specification.

    Parameters
    ----------
    module_path : list
        List of strings representing the path to the module in the functions tree.
    new_function_name : str
        Name of the new function.
    agg_specs : dict
        Dictionary of aggregation specifications. Must contain the aggregation type
        ("aggr") and the column to aggregate ("source_col").
    functions_tree: dict
        Functions tree.

    Returns
    -------
    aggregate_by_group_func : The aggregation func with the expected signature

    """
    qualified_names_to_functions_dict = tree_to_dict_with_qualified_name(functions_tree)
    aggregation_type = agg_specs["aggr"]
    source_col = agg_specs["source_col"]
    qualified_name_source_col = "__".join([*module_path, source_col])

    # Identify grouping level
    group_id = None
    for g in SUPPORTED_GROUPINGS:
        if new_function_name.endswith(f"_{g}"):
            group_id = f"{g}_id"
    if not group_id:
        raise ValueError(
            "Name of aggregated column needs to have a suffix "
            "indicating the group over which it is aggregated. "
            f"The name {new_function_name} does not do so."
        )

    annotations = _annotations_for_aggregation(
        aggregation_type=aggregation_type,
        source_col=source_col,
        qualified_name_source_col=qualified_name_source_col,
        qualified_names_to_functions_dict=qualified_names_to_functions_dict,
    )

    if aggregation_type == "count":
        # TODO(@MImmesberger): Use qualified name of group_id here once namespace
        # changes
        @rename_arguments(mapper={"group_id": group_id}, annotations=annotations)
        def aggregate_by_group_func(group_id):
            return grouped_count(group_id)

    else:
        # TODO(@MImmesberger): Use qualified name of group_id here once namespace
        # changes
        mapper = {"source_col": qualified_name_source_col, "group_id": group_id}
        if aggregation_type == "sum":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_sum(source_col, group_id)

        elif aggregation_type == "mean":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_mean(source_col, group_id)

        elif aggregation_type == "max":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_max(source_col, group_id)

        elif aggregation_type == "min":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_min(source_col, group_id)

        elif aggregation_type == "any":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_any(source_col, group_id)

        elif aggregation_type == "all":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_all(source_col, group_id)

        else:
            raise ValueError(f"Aggr {aggregation_type} is not implemented.")

    if aggregation_type == "count":
        derived_from = group_id
    else:
        derived_from = (qualified_name_source_col, group_id)

    return DerivedFunction(
        aggregate_by_group_func,
        function_name=new_function_name,
        derived_from=derived_from,
    )


def _create_aggregate_by_p_id_functions(
    functions_tree: dict[str, Any],
    aggregate_by_p_id_specs: dict[str, Any],
) -> dict[str, Any]:
    """Create function dict with functions that link variables across persons."""

    aggregation_dicts = _get_aggregation_dicts(aggregate_by_p_id_specs)

    derived_functions = {}

    for module_name, module_aggregation_dicts in aggregation_dicts.items():
        for func_name, aggregation_dict in module_aggregation_dicts.items():
            module_path = module_name.split("__")
            path = [*module_path, func_name]
            derived_func = _create_one_aggregate_by_p_id_func(
                module_path=module_path,
                new_function_name=func_name,
                agg_specs=aggregation_dict,
                functions_tree=functions_tree,
            )
            derived_functions = tree_update(derived_functions, path, derived_func)

    return derived_functions


def _get_aggregation_dicts(aggregate_by_p_id_specs: dict[str, Any]) -> dict[str, dict]:
    """Get aggregation dictionaries from the specs.

    Reduces the tree to a dict with qualified module names as keys and the aggregation
    dict as values.

    Example:
    {"module1": {"module2": {"func": {"source_col": "col", "p_id_to_aggregate_by":
    "xx_id"}}},
    Result: {"module1__module2": {"func": {
    "source_col": "col", "p_id_to_aggregate_by": "xx_id"}}}
    """

    out = {}
    paths, leafs, _ = tree_flatten_with_path(aggregate_by_p_id_specs)
    for path, leaf in zip(paths, leafs):
        qualified_name = "__".join(path[:-2])
        aggregation_func_name = path[-2]
        aggregation_spec_key = path[-1]
        keys = [qualified_name, aggregation_func_name, aggregation_spec_key]
        out = tree_update(out, keys, leaf)

    return out


def _create_one_aggregate_by_p_id_func(
    module_path: list[str],
    new_function_name: str,
    agg_specs: dict[str, str],
    functions_tree: dict[str, PolicyFunction],
) -> DerivedFunction:
    """Create one function that links variables across persons.

    Parameters
    ----------
    module_path : list
        List of strings representing the path to the module in the functions tree.
    new_function_name : str
        Name of the new function.
    agg_specs : dict
        Dictionary of aggregation specifications. Must contain the aggregation type
        ("aggr") and the column to aggregate ("source_col").
    functions_tree: dict
        Functions tree.

    Returns
    -------
    aggregate_by_p_id_func : The aggregation func with the expected signature

    """
    qualified_names_to_functions_dict = tree_to_dict_with_qualified_name(functions_tree)
    aggregation_type = agg_specs["aggr"]
    source_col = agg_specs["source_col"]
    p_id_to_aggregate_by = agg_specs["p_id_to_aggregate_by"]
    qualified_name_source_col = "__".join([*module_path, source_col])

    annotations = _annotations_for_aggregation(
        aggregation_type=aggregation_type,
        source_col=source_col,
        qualified_name_source_col=qualified_name_source_col,
        qualified_names_to_functions_dict=qualified_names_to_functions_dict,
    )

    # Define aggregation func
    if aggregation_type == "count":
        # TODO(@MImmesberger): Use qualified name of p_id and p_id_to_aggregate_by here
        # once namespace changes
        @rename_arguments(
            mapper={
                "p_id_to_aggregate_by": p_id_to_aggregate_by,
                "p_id_to_store_by": "p_id",
            },
            annotations=annotations,
        )
        def aggregate_by_p_id_func(p_id_to_aggregate_by, p_id_to_store_by):
            return count_by_p_id(p_id_to_aggregate_by, p_id_to_store_by)

    else:
        # TODO(@MImmesberger): Use qualified name of p_id and p_id_to_aggregate_by here
        # once namespace changes
        mapper = {
            "p_id_to_aggregate_by": p_id_to_aggregate_by,
            "p_id_to_store_by": "p_id",
            "column": qualified_name_source_col,
        }

        if aggregation_type == "sum":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return sum_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_type == "mean":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return mean_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_type == "max":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return max_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_type == "min":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return min_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_type == "any":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return any_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif aggregation_type == "all":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return all_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        else:
            raise ValueError(f"Aggr {aggregation_type} is not implemented.")

    # TODO(@MImmesberger): Use qualified name of p_id_to_aggregate_by here once
    # namespace changes
    if aggregation_type == "count":
        derived_from = p_id_to_aggregate_by
    else:
        derived_from = (qualified_name_source_col, p_id_to_aggregate_by)

    return DerivedFunction(
        aggregate_by_p_id_func,
        function_name=new_function_name,
        derived_from=derived_from,
    )


def _vectorize_func(func):
    # If the function is already vectorized, return it as is
    if hasattr(func, "__info__") and func.__info__.get("skip_vectorization", False):
        return func

    if isinstance(func, PolicyFunction):
        return func

    # What should work once that Jax backend is fully supported
    signature = inspect.signature(func)
    func_vec = numpy.vectorize(func)

    @functools.wraps(func)
    def wrapper_vectorize_func(*args, **kwargs):
        return func_vec(*args, **kwargs)

    wrapper_vectorize_func.__signature__ = signature

    return wrapper_vectorize_func


def _fail_if_targets_are_not_among_functions(
    functions: dict[str, Any], targets: dict[str, Any]
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
    qualified_names_targets, _, _ = tree_flatten_with_qualified_name(targets)
    qualified_names_functions, _, _ = tree_flatten_with_qualified_name(functions)

    targets_not_in_functions = set(qualified_names_targets) - set(
        qualified_names_functions
    )
    if targets_not_in_functions:
        formatted = format_list_linewise(targets_not_in_functions)
        raise ValueError(
            f"The following targets have no corresponding function:\n{formatted}"
        )
