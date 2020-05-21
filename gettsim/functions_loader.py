import importlib
import inspect
from pathlib import Path


def load_functions(sources):
    """Load functions.

    Parameters
    ----------
    sources : List of path_like, function, module, dictionary of functions

    Returns
    -------
    functions : dict
        A dictionary where keys are names of variables and values are functions which
        produce the variables.

    """
    sources = sources if isinstance(sources, list) else [sources]
    sources = _handle_paths(sources)

    functions = {}
    for source in sources:
        if callable(source):
            functions[source.__name__] = source

        elif isinstance(source, dict):
            functions = {**functions, **source}

        elif isinstance(source, Path) or inspect.ismodule(source):
            if isinstance(source, Path):
                spec = importlib.util.spec_from_file_location(
                    source.name, source.as_posix()
                )
                source = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(source)

            functions_defined_in_module = {
                name: func
                for name, func in inspect.getmembers(source)
                if _is_function_defined_in_module(func, source.__name__)
            }

            # overlapping_functions = set(functions_defined_in_module) - set(functions)
            # if overlapping_functions:
            #     warnings.warn(
            #         "The following functions are already defined: "
            #         f"{overlapping_functions}."
            #     )

            functions = {**functions, **functions_defined_in_module}

        else:
            raise NotImplementedError

    return functions


def _is_function_defined_in_module(func, module):
    return inspect.isfunction(func) and func.__module__ == module


def _handle_paths(sources):
    """Handle paths to load modules.

    1. Convert strings to paths.
    2. If a path is a directory, collect all modules in the directory.

    """
    new_sources = []
    for source in sources:
        if isinstance(source, str):
            source = Path(source)

        if isinstance(source, Path) and source.is_dir():
            modules = list(source.rglob("*.py"))
            new_sources.extend(modules)

        else:
            new_sources.append(source)

    return new_sources
