import datetime
import importlib.util
import inspect
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, TypeAlias

from _gettsim.config import (
    PATHS_TO_INTERNAL_FUNCTIONS,
    QUALIFIED_NAME_SEPARATOR,
    RESOURCE_DIR,
)
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.gettsim_typing import NestedFunctionDict
from _gettsim.shared import (
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
        date=date, package_root=RESOURCE_DIR, roots=PATHS_TO_INTERNAL_FUNCTIONS
    )


def _build_functions_tree(
    date: datetime.date, package_root: Path, roots: list[Path]
) -> NestedFunctionDict:
    """
    Build the function tree.

    Takes the list of root paths and searches for all modules containing
    PolicyFunctions. Then it loads all PolicyFunctions that are active at the given date
    and parses them into the functions tree.

    Parameters
    ----------
    date:
        The date for which policy functions should be loaded.
    package_root:
        The root of the package that contains the functions. This is required to assign
        qualified names to the functions. It must contain all roots.
    roots:
        The roots from which to start the search for policy functions.

    Returns
    -------
    NestedFunctionDict:
        A tree of PolicyFunctions.
    """
    tree = {}
    paths = _find_python_files_recursively(roots)

    for path in paths:
        active_functions_dict = get_active_functions_from_module(
            module_path=path, date=date, package_root=package_root
        )
        module_name = _convert_path_to_qualified_module_name(path, package_root)
        tree = tree_update(
            tree=tree,
            path=module_name.split(QUALIFIED_NAME_SEPARATOR),
            value=active_functions_dict,
        )

    return tree


def get_active_functions_from_module(
    module_path: Path,
    package_root: Path,
    date: datetime.date,
) -> NestedFunctionDict:
    """Extract all active PolicyFunctions from a module.

    Parameters
    ----------
    module_path : Path
        The path to the module from which to extract the active functions.
    package_root : Path
        The root of the package that contains the functions.
    date : datetime.date
        The date for which to extract the active functions.

    Returns
    -------
    NestedFunctionDict
        A dictionary of PolicyFunctions with their leaf names as keys.
    """
    module = _load_module(module_path, package_root)
    module_name = _convert_path_to_qualified_module_name(module_path, package_root)

    all_functions = inspect.getmembers(module)

    active_policy_functions = get_active_policy_functions(
        all_functions=all_functions,
        module_name=module_name,
        date=date,
    )

    _fail_if_multiple_active_functions_with_same_qualified_name(active_policy_functions)

    return {func.leaf_name: func for func in active_policy_functions}


def get_active_policy_functions(
    all_functions: list[Callable | PolicyFunction],
    module_name: str,
    date: datetime.date,
) -> list[PolicyFunction]:
    """Extract all active PolicyFunctions from a module.

    Parameters
    ----------
    all_functions : list[Union[callable | PolicyFunction]]
        List of all functions in the module.
    module_name : str
        The name of the module.
    date : datetime.date
        The date for which to extract the active functions.

    Returns
    -------
    list[PolicyFunction]
        A list of active PolicyFunctions.
    """
    active_policy_functions = []

    for _, func in all_functions:
        if isinstance(func, PolicyFunction) and func.is_active_at_date(date):
            func.set_qualified_name(module_name + func.leaf_name)
            active_policy_functions.append(func)

    return active_policy_functions


def _fail_if_multiple_active_functions_with_same_qualified_name(
    functions: list[PolicyFunction],
) -> None:
    qualified_names = []

    for func in functions:
        if func.qualified_name in qualified_names:
            raise ConflictingTimeDependentFunctionsError(functions, func.qualified_name)
        qualified_names.append(func.qualified_name)


class ConflictingTimeDependentFunctionsError(Exception):
    """Error raised when multiple functions with the same qualified name are active at
    the same time."""

    def __init__(self, functions: list[PolicyFunction], qualified_name: str):
        self.functions = functions
        self.qualified_name = qualified_name

    def __str__(self):
        overlapping_functions = [
            func
            for func in self.functions
            if func.qualified_name == self.qualified_name
        ]
        return f"""
        Some functions with the same qualified name have overlapping start and end
        dates. The following functions are affected: \n\n
        {"; ".join([func.leaf_name for func in overlapping_functions])} \n
        Overlapping from {min([func.start_date for func in overlapping_functions])}
        to {max([func.end_date for func in overlapping_functions])}."""


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


def _load_module(path: Path, package_root: Path) -> ModuleType:
    module_name = _convert_path_to_importable_module_name(path, package_root)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def _convert_path_to_importable_module_name(path: Path, package_root: Path) -> str:
    """
    Convert an absolute path to a Python module name.

    Examples
    --------
    >>> _convert_path_to_importable_module_name(RESOURCE_DIR / "taxes" / "functions.py")
    "taxes.functions"
    """
    return (
        path.relative_to(package_root.parent)
        .with_suffix("")
        .as_posix()
        .replace("/", ".")
    )


def _convert_path_to_qualified_module_name(path: Path, package_root: Path) -> str:
    """
    Convert an absolute path to a qualified module name.

    Examples
    --------
    >>> _convert_path_to_qualified_module_name(RESOURCE_DIR / "taxes" / "dir"
        / "functions.py")
    "dir__functions"
    """
    # TODO(@MImmesberger): Remove the removeprefix calls once directory structure is
    #  changed.
    return (
        path.relative_to(package_root.parent)
        .with_suffix("")
        .as_posix()
        .removeprefix("_gettsim/")
        .removeprefix("taxes/")
        .removeprefix("transfers/")
        .replace("/", QUALIFIED_NAME_SEPARATOR)
    )


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
        module_name = _convert_path_to_qualified_module_name(path, package_root)
        derived_function_specs = _load_functions_to_derive(
            path, package_root, f"{variant}_"
        )
        tree = tree_update(
            tree=tree,
            path=module_name.split(QUALIFIED_NAME_SEPARATOR),
            value=derived_function_specs,
        )

    return tree


def _load_functions_to_derive(
    path: Path,
    package_root: Path,
    prefix_filter: str,
) -> dict:
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
    module_name = _convert_path_to_importable_module_name(path, package_root)
    dicts_in_module = [
        member
        for name, member in inspect.getmembers(module)
        if isinstance(member, dict) and name.startswith(prefix_filter)
    ]

    _fail_if_more_than_one_dict_loaded(dicts_in_module, module_name)
    return dicts_in_module[0]


def _fail_if_more_than_one_dict_loaded(dicts: list[dict], module_name: str) -> None:
    if len(dicts) > 1:
        raise ValueError(
            "More than one dictionary found in the module:\n\n" f"{module_name}\n\n"
        )
