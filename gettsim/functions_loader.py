import importlib
import inspect
from pathlib import Path

from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.config import ROOT_DIR


def load_user_and_internal_functions(functions):
    functions = [] if functions is None else functions

    custom_functions = _load_functions(functions)
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    internal_functions = _load_functions(imports)

    return custom_functions, internal_functions


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


def _load_functions(sources, allow_imported_members=False):
    """Load functions.

    Parameters
    ----------
    sources : str, pathlib.Path, function, module, imports statements
        Sources from where to load functions.
    allow_imported_members : bool
        Should imported members also be collected from a module?

    Returns
    -------
    functions : dict
        A dictionary where keys are names of variables and values are functions which
        produce the variables.

    """
    sources = sources if isinstance(sources, list) else [sources]
    sources = _convert_some_strings_to_paths(sources)
    sources = _search_directories_recursively_for_python_files(sources)
    sources = _convert_paths_and_strings_to_dicts_of_functions(
        sources, allow_imported_members
    )

    functions = {}
    for source in sources:
        if callable(source):
            source = {source.__name__: source}

        if isinstance(source, dict) and all(
            inspect.isfunction(i) for i in source.values()
        ):
            # Test whether there are duplicate functions.
            duplicated_functions = set(source) & set(functions)
            if duplicated_functions and not allow_imported_members:
                formatted = _format_duplicated_functions(
                    duplicated_functions, functions, source
                )
                raise ValueError(
                    f"The following functions are defined multiple times:\n{formatted}"
                )

            functions = {**functions, **source}

        else:
            raise NotImplementedError(
                f"Source {source} has invalid type {type(source)}."
            )

    return functions


def _convert_some_strings_to_paths(sources):
    """Handle strings in sources.

    Strings are evaluated by :func:`importlib.utils.find_spec` to see whether it is a
    module import. If an error occurs or it returns None, the string is converted to a
    path.

    """
    new_sources = []
    for source in sources:
        if isinstance(source, str):
            try:
                out = importlib.util.find_spec(source)
            except ValueError:
                out = Path(source)
            else:
                out = Path(source) if out is None else source
        else:
            out = source

        new_sources.append(source)

    return new_sources


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


def _convert_paths_and_strings_to_dicts_of_functions(sources, allow_imported_members):
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
                if allow_imported_members
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
