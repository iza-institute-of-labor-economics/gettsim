from __future__ import annotations

import functools
import importlib
import inspect
from pathlib import Path

import numpy

from _gettsim.aggregation import (
    grouped_all,
    grouped_any,
    grouped_count,
    grouped_cumsum,
    grouped_max,
    grouped_mean,
    grouped_min,
    grouped_sum,
)
from _gettsim.config import (
    PATHS_TO_INTERNAL_FUNCTIONS,
    RESOURCE_DIR,
    SUPPORTED_GROUPINGS,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.shared import (
    format_errors_and_warnings,
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    remove_group_suffix,
)


def load_and_check_functions(
    user_functions_raw,
    columns_overriding_functions,
    targets,
    data_cols,
    aggregation_specs,
):
    """Create the dict with all functions that may become part of the DAG by:

    - merging user and internal functions
    - vectorize all functions
    - adding aggregation functions

    Check that:
    - all targets are in set of functions or in columns_overriding_functions
    - columns_overriding_functions are in set of functions

    Parameters
    ----------
    user_functions_raw : dict
        A dictionary mapping column names to policy functions by the user.
    columns_overriding_functions : str list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    targets : list of str
        List of strings with names of functions whose output is actually needed by the
        user.
    data_cols : list
        Data columns provided by the user.
    aggregation_specs : dict
        A dictionary which contains specs for functions which aggregate variables on
        the tax unit or household level. The syntax is the same as for aggregation
        specs in the code base and as specified in
        [GEP 4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html)

    Returns
    -------
    functions_not_overridden : dict
        All functions except the ones that are overridden by an input column.
    functions_overridden : dict
        Functions that are overridden by an input column.

    """

    # Load user and internal functions.
    user_functions_raw = [] if user_functions_raw is None else user_functions_raw
    user_functions = _load_functions(user_functions_raw)
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    internal_functions = _load_functions(imports)

    # Vectorize functions.
    user_and_internal_functions = {
        fn: _vectorize_func(f)
        for fn, f in {**internal_functions, **user_functions}.items()
    }

    # Create and add aggregation functions.
    aggregation_functions = _create_aggregation_functions(
        user_and_internal_functions, targets, data_cols, aggregation_specs
    )

    # Check for implicit overlap of functions and data columns.
    data_cols_excl_overriding = [
        c for c in data_cols if c not in columns_overriding_functions
    ]
    for funcs, name in zip(
        [internal_functions, user_functions, aggregation_functions],
        ["internal", "user", "aggregation"],
    ):
        _fail_if_functions_and_columns_overlap(data_cols_excl_overriding, funcs, name)

    all_functions = {**user_and_internal_functions, **aggregation_functions}

    _fail_if_columns_overriding_functions_are_not_in_functions(
        columns_overriding_functions, all_functions
    )

    _fail_if_targets_are_not_in_functions_or_in_columns_overriding_functions(
        all_functions, targets, columns_overriding_functions
    )

    # Separate all functions by whether they will be used or not.
    functions_overridden = {}
    functions_not_overridden = {}
    for k, v in all_functions.items():
        if k in columns_overriding_functions:
            functions_overridden[k] = v
        else:
            functions_not_overridden[k] = v

    return functions_not_overridden, functions_overridden


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


def load_aggregation_dict():
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    sources = _search_directories_recursively_for_python_files(imports)
    aggregation_dict = _load_aggregation_combined_dict_from_strings(sources)
    return aggregation_dict


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
        if isinstance(source, (Path, str)):
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


def _load_aggregation_combined_dict_from_strings(sources):
    """Load aggregation dictionaries from paths and strings and combine them.

    1. Paths point to modules which are loaded.
    2. Strings are import statements which can be imported as module.

    """
    new_sources = []
    for source in sources:
        if isinstance(source, (Path, str)):
            if isinstance(source, Path):
                spec = importlib.util.spec_from_file_location(source.name, source)
                out = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(out)
            elif isinstance(source, str):
                out = importlib.import_module(source)
            aggregation_dicts_defined_in_module = [
                obj
                for name, obj in inspect.getmembers(out)
                if isinstance(obj, dict) and name.startswith("aggregation_")
                # if _is_function_defined_in_module(func, out.__name__)
            ]

        new_sources.append(aggregation_dicts_defined_in_module)

    # Combine dictionaries
    list_of_aggregation_dics = [c for inner_list in new_sources for c in inner_list]
    all_keys = [c for inner_dict in list_of_aggregation_dics for c in inner_dict]
    if len(all_keys) != len(set(all_keys)):
        duplicate_keys = list({x for x in all_keys if all_keys.count(x) > 1})
        raise ValueError(
            "The following column names are used more "
            f"than once in the aggregation_ dictionarys: {duplicate_keys}"
        )
    else:
        combined_dict = {
            k: v
            for inner_dict in list_of_aggregation_dics
            for k, v in inner_dict.items()
        }
    return combined_dict


def _create_aggregation_functions(
    user_and_internal_functions, targets, data_cols, user_provided_aggregation_specs
):
    """Create aggregation functions."""
    aggregation_dict = load_aggregation_dict()

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

    automated_sum_aggregation_cols = [
        col
        for col in potential_agg_cols
        if (col not in user_and_internal_functions)
        and any(col.endswith(f"_{g}") for g in SUPPORTED_GROUPINGS)
        and (remove_group_suffix(col) in potential_source_cols)
    ]
    automated_sum_aggregation_specs = {
        agg_col: {"aggr": "sum", "source_col": remove_group_suffix(agg_col)}
        for agg_col in automated_sum_aggregation_cols
    }

    # Add automated aggregation specs.
    # Note: For duplicate keys, explicitly set specs are treated with higher priority
    # than automated specs.
    aggregation_dict = {**automated_sum_aggregation_specs, **aggregation_dict}

    # Add user provided aggregation specs.
    # Note: For duplicate keys, user provided specs are treated with higher priority.
    aggregation_dict = {**aggregation_dict, **user_provided_aggregation_specs}

    # Create functions from specs
    aggregation_functions = {
        agg_col: _create_one_aggregation_func(
            agg_col, agg_spec, user_and_internal_functions
        )
        for agg_col, agg_spec in aggregation_dict.items()
    }
    return aggregation_functions


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


def _create_one_aggregation_func(  # noqa: PLR0912
    agg_col, agg_specs, user_and_internal_functions
):
    """Create an aggregation function based on aggregation specification.

    Parameters
    ----------
    agg_col : str
        Name of the aggregated column.
    agg_specs : dict
        Dictionary of aggregation specifications. Can contain the source column
        ("source_col") and the group ids ("group_id")
    user_and_internal_functions: dict
        Dictionary of functions.


    Returns
    -------
    aggregation_func : The aggregation func with the expected signature

    """
    # Read individual specification parameters and make sure nothing is missing
    try:
        aggr = agg_specs["aggr"]
    except KeyError as e:
        raise KeyError(
            f"No aggr keyword is specified for aggregation column {agg_col}."
        ) from e

    if aggr != "count":
        try:
            source_col = agg_specs["source_col"]
        except KeyError as e:
            raise KeyError(
                f"Source_col is not specified for aggregation column {agg_col}."
            ) from e

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

    # Build annotations
    annotations = {group_id: int}
    if aggr == "count":
        annotations["return"] = int
    else:
        if (
            source_col in user_and_internal_functions
            and "return" in user_and_internal_functions[source_col].__annotations__
        ):
            annotations[source_col] = user_and_internal_functions[
                source_col
            ].__annotations__["return"]

            # Find out return type
            annotations["return"] = _select_return_type(aggr, annotations[source_col])
        elif source_col in TYPES_INPUT_VARIABLES:
            annotations[source_col] = TYPES_INPUT_VARIABLES[source_col]

            # Find out return type
            annotations["return"] = _select_return_type(aggr, annotations[source_col])
        else:
            # ToDo: Think about how type annotations of aggregations of user-provided
            # ToDo: input variables are handled
            pass

    # Define aggregation func
    if aggr == "count":

        @rename_arguments(mapper={"group_id": group_id}, annotations=annotations)
        def aggregation_func(group_id):
            return grouped_count(group_id)

    elif aggr == "sum":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_sum(source_col, group_id)

    elif aggr == "mean":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_mean(source_col, group_id)

    elif aggr == "max":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_max(source_col, group_id)

    elif aggr == "min":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_min(source_col, group_id)

    elif aggr == "any":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_any(source_col, group_id)

    elif aggr == "all":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_all(source_col, group_id)

    elif aggr == "cumsum":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_cumsum(source_col, group_id)

    else:
        raise ValueError(f"Aggr {aggr} is not implemented, yet.")

    return aggregation_func


def _select_return_type(aggr, source_col_type):
    # Find out return type
    if (source_col_type == int) and (aggr in ["any", "all"]):
        return_type = bool
    elif (source_col_type == bool) and (aggr in ["sum"]):
        return_type = int
    else:
        return_type = source_col_type

    return return_type


def _vectorize_func(func):
    # What should work once that Jax backend is fully supported
    signature = inspect.signature(func)
    func_vec = numpy.vectorize(func)

    @functools.wraps(func)
    def wrapper_vectorize_func(*args, **kwargs):
        return func_vec(*args, **kwargs)

    wrapper_vectorize_func.__signature__ = signature

    return wrapper_vectorize_func


def _fail_if_functions_and_columns_overlap(columns, functions, type_):
    """Fail if functions which compute columns overlap with existing columns.

    Parameters
    ----------
    columns : list of str
        List of strings containing column names.
    functions : dict
        Dictionary of functions.
    type_ : {"internal", "user"}
        Source of the functions. "user" means functions passed by the user.

    Raises
    ------
    ValueError
        Fail if functions which compute columns overlap with existing columns.

    """
    if type_ == "internal":
        type_str = "internal "
    elif type_ == "aggregation":
        type_str = "internal aggregation "
    else:
        type_str = ""

    overlap = sorted(
        name
        for name in columns
        if (name in functions) or (remove_group_suffix(name) in functions)
    )

    if overlap:
        n_cols = len(overlap)
        first_part = format_errors_and_warnings(
            f"Your data provides the column{'' if n_cols == 1 else 's'}:"
        )
        formatted = format_list_linewise(overlap)
        second_part = format_errors_and_warnings(
            f"""
            {'This is' if n_cols == 1 else 'These are'} already present among the
            {type_str}functions of the taxes and transfers system.

            If you want {'this' if n_cols == 1 else 'a'} data column to be used
            instead of calculating it within GETTSIM, please specify it among the
            *columns_overriding_functions*{'.' if type_ == 'internal' else ''' or remove
            the function from *functions*.'''}

            If you want {'this' if n_cols == 1 else 'a'} data column to be calculated
            by {type_str}functions, remove it from the *data* you pass to GETTSIM.

            {'' if n_cols == 1 else '''You need to pick one option for each column that
            appears in the list above.'''}
            """
        )
        raise ValueError(f"{first_part}\n{formatted}\n{second_part}")


def _fail_if_columns_overriding_functions_are_not_in_functions(
    columns_overriding_functions, functions
):
    """Fail if ``columns_overriding_functions`` are not found in functions.

    Parameters
    ----------
    columns_overriding_functions : str list of str
        Names of columns which are preferred over function defined in the tax and
        transfer system.
    functions : dict of callable
        A dictionary of functions.

    Raises
    ------
    ValueError
        Fail if some ``columns_overriding_functions`` are not found in internal or user
        functions.

    """
    unnecessary_columns_overriding_functions = [
        col
        for col in columns_overriding_functions
        if (col not in functions) and (remove_group_suffix(col) not in functions)
    ]
    if unnecessary_columns_overriding_functions:
        n_cols = len(unnecessary_columns_overriding_functions)
        intro = format_errors_and_warnings(
            f"""
            You passed the following user column{'' if n_cols == 1 else 's'} which {'is'
            if n_cols == 1 else 'are'} unnecessary because no functions require them as
            inputs.
            """
        )
        list_ = format_list_linewise(unnecessary_columns_overriding_functions)
        raise ValueError(f"{intro}\n{list_}")


def _fail_if_targets_are_not_in_functions_or_in_columns_overriding_functions(
    functions, targets, columns_overriding_functions
):
    """Fail if targets are not in functions.

    Parameters
    ----------
    functions : dict of callable
        Dictionary containing functions to build the DAG.
    targets : list of str
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.
    columns_overriding_functions : list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.

    Raises
    ------
    ValueError
        Raised if ``targets`` are not in functions.

    """
    targets_not_in_functions = (
        set(targets) - set(functions) - set(columns_overriding_functions)
    )
    if targets_not_in_functions:
        formatted = format_list_linewise(targets_not_in_functions)
        raise ValueError(
            f"The following targets have no corresponding function:\n{formatted}"
        )
