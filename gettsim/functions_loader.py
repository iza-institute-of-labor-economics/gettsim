import importlib
import inspect
from pathlib import Path

from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.config import ROOT_DIR


def load_user_and_internal_functions(functions):
    functions = [] if functions is None else functions

    user_functions = _load_functions(functions)
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    internal_functions = _load_functions(imports)

    return user_functions, internal_functions


def load_aggregation_dict():
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    sources = _search_directories_recursively_for_python_files(imports)
    aggregation_dict = _load_aggregation_combined_dict_from_strings(sources)
    return aggregation_dict


def _convert_paths_to_import_strings(paths):
    """Convert paths to modules for gettsim's internal functions to imports.

    Example
    -------
    >>> path = ROOT_DIR / "demographic_vars.py"
    >>> _convert_paths_to_import_strings(path)
    ['gettsim.demographic_vars']

    """
    paths = paths if isinstance(paths, list) else [paths]
    ps = _search_directories_recursively_for_python_files(paths)
    ps = [Path("gettsim") / p.relative_to(ROOT_DIR) for p in ps]
    import_strings = [p.with_suffix("").as_posix().replace("/", ".") for p in ps]

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
        A dictionary mapping variable names to functions producing them.

    """
    sources = sources if isinstance(sources, list) else [sources]
    sources = _search_directories_recursively_for_python_files(sources)
    sources = _convert_paths_and_strings_to_dicts_of_functions(
        sources, include_imported_functions
    )

    functions = {}
    for source in sources:
        if callable(source):
            source = {source.__name__: source}

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
        lines.append(f"'{name}' is defined in")
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
