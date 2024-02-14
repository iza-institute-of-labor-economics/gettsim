from __future__ import annotations

import functools
import importlib
import inspect
from pathlib import Path
from typing import TYPE_CHECKING

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
    sum_values_by_id,
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
    functions_raw, targets, data_cols, aggregation_specs, interpersonal_links_specs
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
    aggregation_specs : dict
        A dictionary which contains specs for functions which aggregate variables on
        the tax unit or household level. The syntax is the same as for aggregation
        specs in the code base and as specified in
        [GEP 4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html)
    interpersonal_links_specs : dict
        A dictionary which contains specs for linking (and aggregating) taxes and
        transfers across individuals. The syntax is the same as for interpersonal links
        in the code base.

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
        aggregation_functions,
        interpersonal_link_functions,
    ) = _create_derived_functions(
        vectorized_functions,
        targets,
        data_cols,
        aggregation_specs,
        interpersonal_links_specs,
    )

    # Create groupings
    groupings = create_groupings()

    all_functions = {
        **interpersonal_link_functions,
        **time_conversion_functions,
        **vectorized_functions,
        **aggregation_functions,
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
    aggregation_specs: dict[str, dict[str, str]],
    interpersonal_links_specs: dict[str, dict[str, str]],
) -> tuple[dict[str, Callable], dict[str, Callable]]:
    """
    Create functions that are derived from the user and internal functions.

    This includes:
    - functions for converting to different time units
    - aggregation functions
    - combinations of these
    """

    # Create parent-child relationships
    interpersonal_link_functions = _create_interpersonal_link_functions(
        user_and_internal_functions,
        data_cols,
        interpersonal_links_specs,
    )

    # Create functions for different time units
    time_conversion_functions = create_time_conversion_functions(
        {**user_and_internal_functions, **interpersonal_link_functions}, data_cols
    )

    # Create aggregation functions
    aggregation_functions = _create_aggregation_functions(
        {
            **time_conversion_functions,
            **user_and_internal_functions,
            **interpersonal_link_functions,
        },
        targets,
        data_cols,
        aggregation_specs,
    )

    return (
        time_conversion_functions,
        aggregation_functions,
        interpersonal_link_functions,
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


def load_aggregation_and_link_dict():
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    sources = _search_directories_recursively_for_python_files(imports)
    aggregation_dict, link_dict = _load_aggregation_and_link_dicts_from_modules(sources)
    return aggregation_dict, link_dict


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


def _load_aggregation_and_link_dicts_from_modules(sources):
    """Load aggregation dictionaries from paths and strings and combine them.

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
            aggregation_dicts_defined_in_module = [
                obj
                for name, obj in inspect.getmembers(out)
                if isinstance(obj, dict)
                and name.startswith(("aggregation_", "interpersonal_links_"))
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
        aggregation_dict = dict(
            filter(lambda k: "id_col" not in k[1], combined_dict.items())
        )
        link_dict = dict(filter(lambda k: "id_col" in k[1], combined_dict.items()))
    return aggregation_dict, link_dict


def _create_aggregation_functions(
    user_and_internal_functions, targets, data_cols, user_provided_aggregation_specs
):
    """Create aggregation functions."""
    aggregation_dict, _ = load_aggregation_and_link_dict()

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
            # TODO(@hmgaudecker): Think about how type annotations of aggregations of
            #     user-provided input variables are handled
            # https://github.com/iza-institute-of-labor-economics/gettsim/issues/604
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


def _create_interpersonal_link_functions(
    user_and_internal_functions: dict[str, Callable],
    data_cols: list[str],
    user_provided_interpersonal_links_specs: dict[str, dict[str, str]],
) -> dict[str, Callable]:
    """
    Create function dict with functions that link parent and child variables.
    """

    _, link_dict = load_aggregation_and_link_dict()

    link_dict = {**link_dict, **user_provided_interpersonal_links_specs}

    _fail_if_not_dict_of_dicts(link_dict)

    link_functions = {
        link_col: _create_one_link_func(
            link_spec,
            user_and_internal_functions,
            data_cols,
        )
        for link_col, link_spec in link_dict.items()
        if link_spec["source_col"] in user_and_internal_functions
    }

    return link_functions


def _create_one_link_func(
    link_spec: dict[str, str],
    user_and_internal_functions: dict[str, Callable],
    data_cols: list[str],
) -> Callable:
    """Create a function that links parent and child variables."""

    _fail_if_source_col_not_in_functions(
        link_spec, user_and_internal_functions, data_cols
    )

    annotations = {}

    if (
        link_spec["source_col"] in user_and_internal_functions
        and "return"
        in user_and_internal_functions[link_spec["source_col"]].__annotations__
    ):
        annotations["source_col"] = user_and_internal_functions[
            link_spec["source_col"]
        ].__annotations__["return"]
        annotations["return"] = (
            int if annotations["source_col"] in (int, bool) else float
        )
    else:
        pass

    # Single target
    if isinstance(link_spec["id_col"], str):
        # Create id annotations
        annotations["id_col"] = int
        # Create function
        mapper_args = {
            "id_col": link_spec["id_col"],
            "p_id": "p_id",
            "source_col": link_spec["source_col"],
        }

        @rename_arguments(mapper=mapper_args, annotations=annotations)
        def link_func(
            source_col: numpy.ndarray,
            id_col: numpy.ndarray,
            p_id: numpy.ndarray,
        ) -> numpy.ndarray:
            return sum_by_parent(source_col, id_col, p_id)

    # Multiple targets
    elif len(link_spec["id_col"]) == 2:
        # Create id annotations
        annotations.update({"id_col_1": int, "id_col_2": int})
        # Create function
        mapper_args = {
            "id_col_1": link_spec["id_col"][0],
            "id_col_2": link_spec["id_col"][1],
            "p_id": "p_id",
            "source_col": link_spec["source_col"],
        }

        @rename_arguments(mapper=mapper_args, annotations=annotations)
        def link_func(
            source_col: numpy.ndarray,
            id_col_1: numpy.ndarray,
            id_col_2: numpy.ndarray,
            p_id: numpy.ndarray,
        ) -> numpy.ndarray:
            return sum_by_parent_multiple_targets(source_col, id_col_1, id_col_2, p_id)

    else:
        raise NotImplementedError(
            """Parent-child links based on more
                                  than two ID columns currently not supported."""
        )

    return link_func


def sum_by_parent(
    source_col: numpy.ndarray,
    id_col: numpy.ndarray,
    p_id: numpy.ndarray,
) -> numpy.ndarray:
    return sum_values_by_id(source_col, id_col, p_id)


def sum_by_parent_multiple_targets(
    source_col: numpy.ndarray,
    id_col_1: numpy.ndarray,
    id_col_2: numpy.ndarray,
    p_id: numpy.ndarray,
) -> numpy.ndarray:
    return sum_values_by_id(source_col, id_col_1, p_id) + sum_values_by_id(
        source_col, id_col_2, p_id
    )


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


def _fail_if_not_dict_of_dicts(dict_to_check: dict) -> None:
    if not isinstance(dict_to_check, dict) or not all(
        isinstance(v, dict) for v in dict_to_check.values()
    ):
        raise ValueError(
            "Parent-child links must be specified as a dictionary of dictionaries."
        )


def _fail_if_source_col_not_in_functions(
    link_spec: dict[str, str],
    functions: dict[str, Callable],
    data_cols: list[str],
) -> None:
    if (
        link_spec["source_col"] not in functions
        and link_spec["source_col"] not in data_cols
    ):
        raise ValueError(
            f"""Source column specified in parent-child link specification
            ({link_spec['source_col']}) not found. Either choose an existing target
            or provide it yourself."""
        )
