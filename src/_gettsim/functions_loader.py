from __future__ import annotations

import functools
import importlib
import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import numpy

from _gettsim.aggregation import (
    all_by_p_id,
    any_by_p_id,
    count_by_p_id,
    grouped_all,
    grouped_any,
    grouped_count,
    grouped_cumsum,
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
    PATHS_TO_INTERNAL_FUNCTIONS,
    RESOURCE_DIR,
    SUPPORTED_GROUPINGS,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.groupings import create_groupings
from _gettsim.shared import (
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    remove_group_suffix,
)
from _gettsim.time_conversion import create_time_conversion_functions

if TYPE_CHECKING:
    from collections.abc import Callable


def load_and_check_functions(
    functions_raw, targets, data_cols, aggregate_by_group_specs, aggregate_by_p_id_specs
):
    """Create the dict with all functions that may become part of the DAG by:

    - vectorizing all functions
    - adding time conversion functions, aggregation functions, and combinations

    Check that:
    - all targets are in set of functions or in data_cols

    Parameters
    ----------
    functions_raw : dict
        A dictionary mapping column names to policy functions.
    targets : list of str
        List of strings with names of functions whose output is actually needed by the
        user.
    data_cols : list
        Data columns provided by the user.
    aggregate_by_group_specs : dict
        A dictionary which contains specs for functions which aggregate variables on
        the tax unit or household level. The syntax is the same as for aggregation
        specs in the code base and as specified in
        [GEP 4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html)
    aggregate_by_p_id_specs : dict
        A dictionary which contains specs for linking aggregating taxes and by another
        individual (for example, a parent). The syntax is the same as for aggregation
        specs in the code base and as specified in
        [GEP 4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html)

    Returns
    -------
    functions_not_overridden : dict
        All functions except the ones that are overridden by an input column.
    functions_overridden : dict
        Functions that are overridden by an input column.

    """

    # Load functions.
    functions_raw = [] if functions_raw is None else functions_raw
    functions = _load_functions(functions_raw)

    # Vectorize functions.
    vectorized_functions = {fn: _vectorize_func(f) for fn, f in functions.items()}

    # Create derived functions
    (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    ) = _create_derived_functions(
        vectorized_functions,
        targets,
        data_cols,
        aggregate_by_group_specs,
        aggregate_by_p_id_specs,
    )

    # Create groupings
    groupings = create_groupings()

    all_functions = {
        **aggregate_by_p_id_functions,
        **time_conversion_functions,
        **vectorized_functions,
        **aggregate_by_group_functions,
        **groupings,
    }

    _fail_if_targets_are_not_among_functions(all_functions, targets)

    # Separate all functions by whether they will be used or not.
    functions_overridden = {}
    functions_not_overridden = {}
    for k, v in all_functions.items():
        if k in data_cols:
            functions_overridden[k] = v
        else:
            functions_not_overridden[k] = v

    return functions_not_overridden, functions_overridden


def _create_derived_functions(
    user_and_internal_functions: dict[str, Callable],
    targets: list[str],
    data_cols: list[str],
    aggregate_by_group_specs: dict[str, dict[str, str]],
    aggregate_by_p_id_specs: dict[str, dict[str, str]],
) -> tuple[dict[str, Callable], dict[str, Callable]]:
    """
    Create functions that are derived from the user and internal functions.

    This includes:
    - functions for converting to different time units
    - aggregation functions
    - combinations of these
    """

    # Create parent-child relationships
    aggregate_by_p_id_functions = _create_aggregate_by_p_id_functions(
        user_and_internal_functions,
        aggregate_by_p_id_specs,
    )

    # Create functions for different time units
    time_conversion_functions = create_time_conversion_functions(
        {**user_and_internal_functions, **aggregate_by_p_id_functions}, data_cols
    )

    # Create aggregation functions
    aggregate_by_group_functions = _create_aggregate_by_group_functions(
        {
            **time_conversion_functions,
            **user_and_internal_functions,
            **aggregate_by_p_id_functions,
        },
        targets,
        data_cols,
        aggregate_by_group_specs,
    )

    return (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    )


def load_user_and_internal_functions(user_functions_raw):
    user_functions_raw = [] if user_functions_raw is None else user_functions_raw

    user_functions = _load_functions(user_functions_raw)
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    internal_functions = _load_functions(imports)

    return user_functions, internal_functions


def load_internal_functions():
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    internal_functions = _load_functions(imports)

    return internal_functions


def load_aggregation_dict(typ: Literal["aggregate_by_group", "aggregate_by_p_id"]):
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    sources = _search_directories_recursively_for_python_files(imports)
    return _load_aggregation_dicts_from_modules(sources, typ)


def _convert_paths_to_import_strings(paths):
    """Convert paths to modules for gettsim's internal functions to imports.

    Example
    -------
    >>> path = RESOURCE_DIR / "demographic_vars.py"
    >>> _convert_paths_to_import_strings(path)
    ['_gettsim.demographic_vars']

    """
    paths = paths if isinstance(paths, list) else [paths]
    abs_paths = _search_directories_recursively_for_python_files(paths)
    rel_paths = [p.relative_to(RESOURCE_DIR.parent) for p in abs_paths]
    import_strings = [p.with_suffix("").as_posix().replace("/", ".") for p in rel_paths]

    return import_strings


def _load_functions(sources, include_imported_functions=False):
    """Load functions.

    Parameters
    ----------
    sources : str, pathlib.Path, function, module, imports statements
        Sources from where to load functions.
    include_imported_functions : bool
        Whether to load functions that are imported into the module(s) passed via
        *sources*.

    Returns
    -------
    functions : dict
        A dictionary mapping column names to functions producing them.

    """
    all_sources = _search_directories_recursively_for_python_files(
        sources if isinstance(sources, list) else [sources]
    )
    all_sources = _convert_paths_and_strings_to_dicts_of_functions(
        all_sources, include_imported_functions
    )

    functions = {}
    for source in all_sources:
        if callable(source):
            source = {source.__name__: source}  # noqa: PLW2901

        if isinstance(source, dict) and all(
            inspect.isfunction(i) for i in source.values()
        ):
            functions = {**functions, **source}

        else:
            raise NotImplementedError(
                f"Source {source} has invalid type {type(source)}."
            )

    return functions


def _search_directories_recursively_for_python_files(sources):
    """Handle paths to load modules.

    If a path in `sources` points to a directory, search this directory recursively for
    Python files.

    """
    new_sources = []
    for source in sources:
        if isinstance(source, Path) and source.is_dir():
            modules = list(source.rglob("*.py"))
            new_sources.extend(modules)

        else:
            new_sources.append(source)

    return new_sources


def _convert_paths_and_strings_to_dicts_of_functions(
    sources, include_imported_functions
):
    """Convert paths and strings to dictionaries of functions.

    1. Paths point to modules which are loaded.
    2. Strings are import statements which can be imported as module.

    Then, all functions in the modules are collected and returned in a dictionary.

    """
    new_sources = []
    for source in sources:
        if isinstance(source, Path | str):
            if isinstance(source, Path):
                spec = importlib.util.spec_from_file_location(source.name, source)
                out = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(out)
            elif isinstance(source, str):
                out = importlib.import_module(source)

            functions_defined_in_module = {
                name: func
                for name, func in inspect.getmembers(
                    out, lambda x: inspect.isfunction(x)
                )
                if include_imported_functions
                or _is_function_defined_in_module(func, out.__name__)
            }
        else:
            functions_defined_in_module = source

        new_sources.append(functions_defined_in_module)

    return new_sources


def _is_function_defined_in_module(func, module):
    return func.__module__ == module


def _format_duplicated_functions(duplicated_functions, functions, source):
    """Format an error message showing duplicated functions and their sources."""
    lines = []
    for name in duplicated_functions:
        lines.append(f"{name!r} is defined in")
        lines.append("    " + inspect.getfile(functions[name]))
        lines.append("    " + inspect.getfile(source[name]))

    return "\n".join(lines)


def _load_aggregation_dicts_from_modules(
    sources: list[Path | str], typ: Literal["aggregate_by_group", "aggregate_by_p_id"]
):
    """Return a dictionary with all aggregations by group or person.

    Dictionaries are imported from *sources*, which point to modules:

    1. Paths point to modules which are loaded.
    2. Strings are import statements which can be imported as module.

    """
    new_sources = []
    for source in sources:
        if isinstance(source, Path | str):
            if isinstance(source, Path):
                spec = importlib.util.spec_from_file_location(source.name, source)
                out = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(out)
            elif isinstance(source, str):
                out = importlib.import_module(source)
            dicts_defined_in_module = [
                obj
                for name, obj in inspect.getmembers(out)
                if isinstance(obj, dict) and name.startswith(f"{typ}_")
            ]

        new_sources.append(dicts_defined_in_module)

    # Combine dictionaries
    list_of_dicts = [c for inner_list in new_sources for c in inner_list]
    all_keys = [c for inner_dict in list_of_dicts for c in inner_dict]
    if len(all_keys) != len(set(all_keys)):
        duplicate_keys = list({x for x in all_keys if all_keys.count(x) > 1})
        raise ValueError(
            "The following column names are used more "
            f"than once in the {typ} dictionaries: {duplicate_keys}"
        )
    return {k: v for inner_dict in list_of_dicts for k, v in inner_dict.items()}


def _create_aggregate_by_group_functions(
    user_and_internal_functions,
    targets,
    data_cols,
    user_provided_aggregate_by_group_specs,
):
    """Create aggregation functions."""
    aggregate_by_group_dict = load_aggregation_dict(typ="aggregate_by_group")

    # Make specs for automated sum aggregation
    potential_source_cols = list(user_and_internal_functions) + data_cols
    potential_agg_cols = set(
        [
            arg
            for func in user_and_internal_functions.values()
            for arg in get_names_of_arguments_without_defaults(func)
        ]
        + targets
    )

    automated_sum_aggregate_by_group_cols = [
        col
        for col in potential_agg_cols
        if (col not in user_and_internal_functions)
        and any(col.endswith(f"_{g}") for g in SUPPORTED_GROUPINGS)
        and (remove_group_suffix(col) in potential_source_cols)
    ]
    automated_sum_aggregate_by_group_specs = {
        agg_col: {"aggr": "sum", "source_col": remove_group_suffix(agg_col)}
        for agg_col in automated_sum_aggregate_by_group_cols
    }

    # Add automated aggregation specs.
    # Note: For duplicate keys, explicitly set specs are treated with higher priority
    # than automated specs.
    aggregate_by_group_dict = {
        **automated_sum_aggregate_by_group_specs,
        **aggregate_by_group_dict,
    }

    # Add user provided aggregation specs.
    # Note: For duplicate keys, user provided specs are treated with higher priority.
    aggregate_by_group_dict = {
        **aggregate_by_group_dict,
        **user_provided_aggregate_by_group_specs,
    }

    # Check validity of aggregation specs
    [
        _check_agg_specs_validity(agg_specs=v, agg_col=k)
        for k, v in aggregate_by_group_dict.items()
    ]

    # Create functions from specs
    aggregate_by_group_functions = {
        agg_col: _create_one_aggregate_by_group_func(
            agg_col, agg_spec, user_and_internal_functions
        )
        for agg_col, agg_spec in aggregate_by_group_dict.items()
    }
    return aggregate_by_group_functions


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


def _check_agg_specs_validity(agg_specs, agg_col):
    if "aggr" not in agg_specs:
        raise KeyError(
            f"No aggr keyword is specified for aggregation column {agg_col}."
        )

    if agg_specs["aggr"] != "count":
        if "source_col" not in agg_specs:
            raise KeyError(
                f"Source_col is not specified for aggregation column {agg_col}."
            )


def _annotations_for_aggregation(agg_specs, user_and_internal_functions):
    annotations = {}
    if agg_specs["aggr"] == "count":
        annotations["return"] = int
    else:
        source_col = agg_specs["source_col"]
        if (
            source_col in user_and_internal_functions
            and "return" in user_and_internal_functions[source_col].__annotations__
        ):
            annotations[source_col] = user_and_internal_functions[
                source_col
            ].__annotations__["return"]

            # Find out return type
            annotations["return"] = _select_return_type(
                agg_specs["aggr"], annotations[source_col]
            )
        elif source_col in TYPES_INPUT_VARIABLES:
            annotations[source_col] = TYPES_INPUT_VARIABLES[source_col]

            # Find out return type
            annotations["return"] = _select_return_type(
                agg_specs["aggr"], annotations[source_col]
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
    agg_col, agg_specs, user_and_internal_functions
):
    """Create an aggregation function based on aggregation specification.

    Parameters
    ----------
    agg_col : str
        Name of the aggregated column.
    agg_specs : dict
        Dictionary of aggregation specifications. Can contain the source column
        ("source_col") and the group ids ("group_id") Dictionary of aggregation
        specifications. Must contain the aggregation type ("aggr"). Unless
        `aggr == "count"`, it must contain the column to aggregate ("source_col").
    user_and_internal_functions: dict
        Dictionary of functions.


    Returns
    -------
    aggregate_by_group_func : The aggregation func with the expected signature

    """

    # Identify grouping level
    group_id = None
    for g in SUPPORTED_GROUPINGS:
        if agg_col.endswith(f"_{g}"):
            group_id = f"{g}_id"
    if not group_id:
        raise ValueError(
            "Name of aggregated column needs to have a suffix "
            "indicating the group over which it is aggregated. "
            f"The name {agg_col} does not do so."
        )

    annotations = _annotations_for_aggregation(
        agg_specs=agg_specs,
        user_and_internal_functions=user_and_internal_functions,
    )

    if agg_specs["aggr"] == "count":

        @rename_arguments(mapper={"group_id": group_id}, annotations=annotations)
        def aggregate_by_group_func(group_id):
            return grouped_count(group_id)

    else:
        mapper = {"source_col": agg_specs["source_col"], "group_id": group_id}
        if agg_specs["aggr"] == "sum":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_sum(source_col, group_id)

        elif agg_specs["aggr"] == "mean":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_mean(source_col, group_id)

        elif agg_specs["aggr"] == "max":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_max(source_col, group_id)

        elif agg_specs["aggr"] == "min":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_min(source_col, group_id)

        elif agg_specs["aggr"] == "any":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_any(source_col, group_id)

        elif agg_specs["aggr"] == "all":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_all(source_col, group_id)

        elif agg_specs["aggr"] == "cumsum":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_group_func(source_col, group_id):
                return grouped_cumsum(source_col, group_id)

        else:
            raise ValueError(f"Aggr {agg_specs['aggr']} is not implemented.")

    return aggregate_by_group_func


def _create_aggregate_by_p_id_functions(
    user_and_internal_functions: dict[str, Callable],
    user_provided_aggregate_by_p_id_specs: dict[str, dict[str, str]],
) -> dict[str, Callable]:
    """Create function dict with functions that link variables across persons."""

    aggregate_by_p_id_dict = load_aggregation_dict(typ="aggregate_by_p_id")

    aggregate_by_p_id_dict = {
        **aggregate_by_p_id_dict,
        **user_provided_aggregate_by_p_id_specs,
    }

    [
        _check_agg_specs_validity(agg_specs=v, agg_col=k)
        for k, v in aggregate_by_p_id_dict.items()
    ]

    aggregate_by_p_id_functions = {
        agg_by_p_id_col: _create_one_aggregate_by_p_id_func(
            agg_specs=agg_by_p_id_spec,
            user_and_internal_functions=user_and_internal_functions,
        )
        for agg_by_p_id_col, agg_by_p_id_spec in aggregate_by_p_id_dict.items()
        if agg_by_p_id_spec["source_col"] in user_and_internal_functions
    }

    return aggregate_by_p_id_functions


def _create_one_aggregate_by_p_id_func(
    agg_specs: dict[str, str],
    user_and_internal_functions: dict[str, Callable],
) -> Callable:
    """Create one function that links variables across persons.

    Parameters
    ----------
    agg_specs : dict
        Dictionary of aggregation specifications. Must contain the p_id by which to
        aggregate ("p_id_to_aggregate_by") and the aggregation type ("aggr"). Unless
        `aggr == "count"`, it must contain the column to aggregate ("source_col").
    user_and_internal_functions: dict
        Dictionary of functions.


    Returns
    -------
    aggregate_by_p_id_func : The aggregation func with the expected signature

    """

    annotations = _annotations_for_aggregation(
        agg_specs=agg_specs,
        user_and_internal_functions=user_and_internal_functions,
    )

    # Define aggregation func
    if agg_specs["aggr"] == "count":

        @rename_arguments(
            mapper={
                "p_id_to_aggregate_by": agg_specs["p_id_to_aggregate_by"],
                "p_id_to_store_by": "p_id",
            },
            annotations=annotations,
        )
        def aggregate_by_p_id_func(p_id_to_aggregate_by, p_id_to_store_by):
            return count_by_p_id(p_id_to_aggregate_by, p_id_to_store_by)

    else:
        mapper = {
            "p_id_to_aggregate_by": agg_specs["p_id_to_aggregate_by"],
            "p_id_to_store_by": "p_id",
            "column": agg_specs["source_col"],
        }

        if agg_specs["aggr"] == "sum":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return sum_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif agg_specs["aggr"] == "mean":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return mean_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif agg_specs["aggr"] == "max":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return max_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif agg_specs["aggr"] == "min":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return min_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif agg_specs["aggr"] == "any":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return any_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        elif agg_specs["aggr"] == "all":

            @rename_arguments(
                mapper=mapper,
                annotations=annotations,
            )
            def aggregate_by_p_id_func(column, p_id_to_aggregate_by, p_id_to_store_by):
                return all_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by)

        else:
            raise ValueError(f"Aggr {agg_specs['aggr']} is not implemented.")

    return aggregate_by_p_id_func


def _vectorize_func(func):
    # What should work once that Jax backend is fully supported
    signature = inspect.signature(func)
    func_vec = numpy.vectorize(func)

    @functools.wraps(func)
    def wrapper_vectorize_func(*args, **kwargs):
        return func_vec(*args, **kwargs)

    wrapper_vectorize_func.__signature__ = signature

    return wrapper_vectorize_func


def _fail_if_targets_are_not_among_functions(functions, targets):
    """Fail if some target is not among functions.

    Parameters
    ----------
    functions : dict of callable
        Dictionary containing functions to build the DAG.
    targets : list of str
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.

    Raises
    ------
    ValueError
        Raised if any member of `targets` is not among functions.

    """
    targets_not_in_functions = set(targets) - set(functions)
    if targets_not_in_functions:
        formatted = format_list_linewise(targets_not_in_functions)
        raise ValueError(
            f"The following targets have no corresponding function:\n{formatted}"
        )
