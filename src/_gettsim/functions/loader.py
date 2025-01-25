import datetime
import importlib.util
import inspect
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, TypeAlias

from _gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS, RESOURCE_DIR
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.gettsim_typing import NestedFunctionDict
from _gettsim.shared import (
    get_path_from_qualified_name,
    tree_update,
)


def load_functions_tree_for_date(date: datetime.date) -> NestedFunctionDict:
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
    return _build_functions_tree(
        [f for f in _load_internal_functions() if f.is_active_at_date(date)]
    )


def _load_internal_functions() -> list[PolicyFunction]:
    """
    Load all internal policy functions.

    Returns
    -------
    functions:
        All internal policy functions.
    """
    return _load_functions(PATHS_TO_INTERNAL_FUNCTIONS, RESOURCE_DIR)


def _load_functions(
    roots: Path | list[Path],
    package_root: Path,
    include_imported_functions=False,
) -> list[PolicyFunction]:
    """
    Load policy functions reachable from the given roots.

    Parameters
    ----------
    roots:
        The roots from which to start the search for policy functions.
    package_root:
        The root of the package that contains the functions. This is required to assign
        qualified names to the functions. It must contain all roots.
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
        result.extend(
            _load_functions_in_module(path, package_root, include_imported_functions)
        )

    return result


def _build_functions_tree(functions: list[PolicyFunction]) -> NestedFunctionDict:
    """Build the function tree.

    Takes the list of active policy functions and builds a tree using the module names.

    Parameters
    ----------
    functions:
        A list of PolicyFunctions.

    Returns
    -------
    tree:
        A tree of PolicyFunctions.
    """
    # Build module_name - functions dictionary
    tree = {}
    for function in functions:
        tree_keys = [
            *get_path_from_qualified_name(function.module_name),
            function.leaf_name,
        ]
        tree = tree_update(tree, tree_keys, function)
    return tree


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


def _load_functions_in_module(
    path: Path,
    package_root: Path,
    include_imported_functions: bool,
) -> list[PolicyFunction]:
    """
    Load policy functions defined in a module.

    Parameters
    ----------
    path:
        The path to the module in which to search for policy functions.
    include_imported_functions:
        Whether to load functions that are imported into the modules passed via
        sources.

    Returns
    -------
    functions:
        Loaded policy functions.
    """
    module = _load_module(path, package_root)

    result = [
        _policy_function_from_decorated_callable(function, module.__name__)
        for name, function in inspect.getmembers(module, inspect.isfunction)
        if include_imported_functions
        or _is_function_defined_in_module(function, module)
    ]

    return result


def _load_module(path: Path, package_root: Path) -> ModuleType:
    module_name = _convert_path_to_module_name(path, package_root)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def _convert_path_to_module_name(path: Path, package_root: Path) -> str:
    """
    Convert an absolute path to a Python module name.

    Examples
    --------
    >>> _convert_path_to_module_name(RESOURCE_DIR / "taxes" / "functions.py")
    "taxes.functions"
    """
    return (
        path.relative_to(package_root.parent)
        .with_suffix("")
        .as_posix()
        .replace("/", "__")
    )


def _policy_function_from_decorated_callable(
    function: Callable,
    module_name: str,
) -> PolicyFunction:
    """
    Create a policy function from a callable with a `@policy_function` decorator.

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
    # TODO(@MImmesberger): Remove the removeprefix calls once the directory
    # structure is cleaned up
    clean_module_name = (
        module_name.removeprefix("_gettsim__")
        .removeprefix("taxes__")
        .removeprefix("transfers__")
    )

    return PolicyFunction(
        function=function,
        module_name=clean_module_name,
    )


def _is_function_defined_in_module(function: Callable, module: ModuleType) -> bool:
    """Check if a function is defined in a specific module or only imported."""
    return function.__module__ == module.__name__


_AggregationVariant: TypeAlias = Literal["aggregate_by_group", "aggregate_by_p_id"]


def load_internal_aggregation_dict(variant: _AggregationVariant) -> dict[str, Any]:
    """
    Load a dictionary with all aggregations by group or person that are defined for
    internal functions.
    """
    return _load_aggregation_dict(PATHS_TO_INTERNAL_FUNCTIONS, RESOURCE_DIR, variant)


def _load_aggregation_dict(
    roots: list[Path], package_root: Path, variant: _AggregationVariant
) -> dict[str, Any]:
    """
    Load a dictionary with all aggregations by group or person reachable from the given
    roots.
    """
    roots = roots if isinstance(roots, list) else [roots]
    paths = _find_python_files_recursively(roots)

    tree = {}

    for path in paths:
        module_name = _convert_path_to_module_name(path, package_root)
        # TODO(@MImmesberger): Remove the removeprefix calls once the directory
        # structure is cleaned up
        clean_module_name = (
            module_name.removeprefix("_gettsim__")
            .removeprefix("taxes__")
            .removeprefix("transfers__")
        )
        tree_keys = get_path_from_qualified_name(clean_module_name)
        derived_function_specs = load_functions_to_derive(
            path, package_root, f"{variant}_"
        )
        tree = tree_update(tree, tree_keys, *derived_function_specs)

    return tree


def load_functions_to_derive(
    path: Path,
    package_root: Path,
    prefix_filter: str,
) -> list[dict]:
    """
    Load the dictionary that specifies which functions to derive from the module.

    Returns one aggregation dictionary where keys are the names of the functions to
    derive and values are dictionaries with the aggregation specifications ('aggr',
    'source_col', 'p_id_to_aggregate_by').

    Parameters
    ----------
    path:
        The path to the module in which to search for dictionaries.
    prefix_filter:
        The prefix that the names of the dictionaries must have.

    Returns
    -------
    dictionaries:
        Loaded dictionaries.
    """
    module = _load_module(path, package_root)
    module_name = _convert_path_to_module_name(path, package_root)
    dicts_in_module = [
        member
        for name, member in inspect.getmembers(module)
        if isinstance(member, dict) and name.startswith(prefix_filter)
    ]

    _fail_if_more_than_one_dict_loaded(dicts_in_module, module_name)
    return dicts_in_module


def _fail_if_more_than_one_dict_loaded(dicts: list[dict], module_name: str) -> None:
    if len(dicts) > 1:
        raise ValueError(
            "More than one dictionary found in the module:\n\n" f"{module_name}\n\n"
        )
