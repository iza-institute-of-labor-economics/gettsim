import datetime
import importlib
import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Literal, TypeAlias

from _gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS, RESOURCE_DIR

from .policy_function import PolicyFunction

def load_functions_for_date(date: datetime.date) -> list[PolicyFunction]:
    """
    Load policy functions that are active at a specific date.

    Parameters
    ----------
    date:
        The date for which policy functions should be loaded.

    Returns
    -------
    functions:
        The policy functions that are active at the given date.
    """
    return [f for f in _load_internal_functions() if f.is_active_at_date(date)]


def _load_internal_functions() -> list[PolicyFunction]:
    """
    Load all internal policy functions.

    Returns
    -------
    functions:
        All internal policy functions.
    """
    return _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)


def _load_functions(
    roots: Path | list[Path],
    include_imported_functions=False,
) -> list[PolicyFunction]:
    """
    Load policy functions reachable from the given roots.

    Parameters
    ----------
    roots:
        The roots from which to start the search for policy functions.
    include_imported_functions:
        Whether to load functions that are imported into the modules passed via
        sources.

    Returns
    -------
    functions:
        Loaded policy functions.
    """
    roots = roots if isinstance(roots, list) else [roots]
    paths = _find_python_files_recursively(roots)

    result = []

    for path in paths:
        module_name = _convert_path_to_module_name(path)
        result.extend(
            _load_functions_in_module(module_name, include_imported_functions)
        )

    return result


def _find_python_files_recursively(roots: list[Path]) -> list[Path]:
    """
    Find all Python files reachable from the given roots.

    Parameters
    ----------
    roots:
        The roots from which to start the search for Python files.

    Returns
    -------
    absolute_paths:
        Absolute paths to all discovered Python files.
    """
    result = []

    for root in roots:
        if root.is_dir():
            modules = list(root.rglob("*.py"))
            result.extend(modules)

        else:
            result.append(root)

    return result


def _convert_path_to_module_name(absolute_path: Path) -> str:
    """
    Convert an absolute path to a Python module name.

    Examples
    --------
    >>> _convert_path_to_module_name(RESOURCE_DIR / "taxes" / "functions.py")
    "taxes.functions"
    """
    return (
        absolute_path.relative_to(RESOURCE_DIR.parent)
        .with_suffix("")
        .as_posix()
        .replace("/", ".")
    )


def _load_functions_in_module(
    module_name: str,
    include_imported_functions: bool,
) -> list[PolicyFunction]:
    """
    Load policy functions defined in a module.

    Parameters
    ----------
    module_name:
        The name of the module in which to search for policy functions.
    include_imported_functions:
        Whether to load functions that are imported into the modules passed via
        sources.

    Returns
    -------
    functions:
        Loaded policy functions.
    """
    module = importlib.import_module(module_name)
    return [
        _create_policy_function_from_decorated_callable(function, module_name)
        for name, function in inspect.getmembers(module, inspect.isfunction)
        if include_imported_functions
        or _is_function_defined_in_module(function, module_name)
    ]


def _create_policy_function_from_decorated_callable(
    function: Callable,
    module_name: str,
) -> PolicyFunction:
    """
    Create a policy function from a callable with a `@policy_info` decorator.

    Parameters
    ----------
    function:
        The callable to wrap.
    module_name:
        The name of the module in which the callable is defined.

    Returns
    -------
    policy_function:
        The policy function.
    """

    # Only needed until the directory structure is cleaned up
    clean_module_name = (
        module_name.removeprefix("_gettsim.")
        .removeprefix("taxes.")
        .removeprefix("transfers.")
    )

    return PolicyFunction(
        function=function,
        module_name=clean_module_name,
    )


def _is_function_defined_in_module(function: Callable, module_name: str) -> bool:
    """Check if a function is defined in a specific module or only imported."""
    return inspect.getmodule(function).__name__ == module_name


_AggregationVariant: TypeAlias = Literal["aggregate_by_group", "aggregate_by_p_id"]


def load_internal_aggregation_dict(variant: _AggregationVariant):
    """
    Load a dictionary with all aggregations by group or person that are defined for
    internal functions.
    """
    return _load_aggregation_dict(PATHS_TO_INTERNAL_FUNCTIONS, variant)


def _load_aggregation_dict(
    roots: list[Path],
    variant: _AggregationVariant
):
    """
    Load a dictionary with all aggregations by group or person reachable from the given
    roots.
    """
    roots = roots if isinstance(roots, list) else [roots]
    paths = _find_python_files_recursively(roots)

    # Load dictionaries
    dicts = []

    for path in paths:
        module_name = _convert_path_to_module_name(path)
        dicts.extend(
            _load_dicts_in_module(module_name, f"{variant}_")
        )

    # Check for duplicate keys
    all_keys = [k for dict_ in dicts for k in dict_.keys()]
    if len(all_keys) != len(set(all_keys)):
        duplicate_keys = list({x for x in all_keys if all_keys.count(x) > 1})
        raise ValueError(
            "The following column names are used more "
            f"than once in the {variant} dictionaries: {duplicate_keys}"
        )

    # Combine dictionaries
    return {k: v for dict_ in dicts for k, v in dict_.items()}


def _load_dicts_in_module(
    module_name: str,
    prefix_filter: str,
) -> list[dict]:
    """
    Load dictionaries defined in a module.

    Parameters
    ----------
    module_name:
        The name of the module in which to search for dictionaries.
    prefix_filter:
        The prefix that the names of the dictionaries must have.

    Returns
    -------
    dictionaries:
        Loaded dictionaries.
    """
    module = importlib.import_module(module_name)

    return [
        member
        for name, member in inspect.getmembers(module)
        if isinstance(member, dict) and name.startswith(prefix_filter)
    ]