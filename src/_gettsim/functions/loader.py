import datetime
import importlib.util
import inspect
import itertools
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, TypeAlias

from _gettsim.aggregation import AggregationSpec
from _gettsim.config import (
    PATHS_TO_INTERNAL_FUNCTIONS,
    QUALIFIED_NAME_SEPARATOR,
    RESOURCE_DIR,
)
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.gettsim_typing import NestedFunctionDict
from _gettsim.shared import tree_update


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

        # Remove recurring branch names in last two branches of path
        # This is done to avoid namespaces like arbeitslosengeld__arbeitslosengeld if
        # the file structure looks like this:
        # arbeitslosengeld
        #           |- arbeitslosengeld.py
        #           |- ...

        if len(path) >= 2:
            qualified_name_path = path[:-1] if path[-1] == path[-2] else path
        else:
            qualified_name_path = path

        tree = tree_update(
            tree=tree,
            path=qualified_name_path,
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
        A dictionary of active PolicyFunctions with their leaf names as keys.
    """
    module = _load_module(module_path, package_root)
    module_name = _convert_path_to_qualified_module_name(module_path, package_root)

    all_functions = inspect.getmembers(module)

    policy_functions = get_policy_functions(
        module_name=module_name,
        all_functions=all_functions,
    )

    return {
        func.leaf_name: func
        for func in policy_functions
        if func.is_active_at_date(date)
    }


def get_policy_functions(
    module_name: str,
    all_functions: list[Callable | PolicyFunction],
) -> list[PolicyFunction]:
    """Extract all PolicyFunctions from a module.

    Parameters
    ----------
    module_name : str
        The name of the module from which to extract the PolicyFunctions.
    all_functions : list[Union[callable | PolicyFunction]]
        List of all functions in the module.

    Returns
    -------
    list[PolicyFunction]
        A list of PolicyFunctions.
    """
    policy_functions = []

    for _, func in all_functions:
        if isinstance(func, PolicyFunction):
            func.set_qualified_name(
                module_name + QUALIFIED_NAME_SEPARATOR + func.leaf_name
            )
            policy_functions.append(func)

    # Check that qualified names are unique on the module level; else, there must be
    # overlapping start and end dates for time-dependent functions.
    _fail_if_dates_active_overlap(policy_functions, module_name)

    return policy_functions


def _fail_if_dates_active_overlap(
    functions: list[PolicyFunction],
    module_name: str,
) -> None:
    """Raises an ConflictingTimeDependentFunctionsError if multiple functions with the
    same leaf name are active at the same time.

    Parameters
    ----------
    functions : list[PolicyFunction]
        List of functions to check for conflicts.

    Raises
    ------
    ConflictingTimeDependentFunctionsError
        If multiple functions with the same name are active at the same time.
    """
    leaf_names_to_funcs = {}
    for func in functions:
        if func.leaf_name in leaf_names_to_funcs:
            leaf_names_to_funcs[func.leaf_name].append(func)
        else:
            leaf_names_to_funcs[func.leaf_name] = [func]

    for leaf_name, funcs in leaf_names_to_funcs.items():
        dates_active = [(f.start_date, f.end_date) for f in funcs]
        for (start1, end1), (start2, end2) in itertools.combinations(dates_active, 2):
            if start1 <= end2 and start2 <= end1:
                raise ConflictingTimeDependentFunctionsError(
                    functions=funcs,
                    leaf_name=leaf_name,
                    module_name=module_name,
                    overlap_start=max(start1, start2),
                    overlap_end=min(end1, end2),
                )


class ConflictingTimeDependentFunctionsError(Exception):
    def __init__(
        self,
        functions: list[PolicyFunction],
        leaf_name: str,
        module_name: str,
        overlap_start: datetime.date,
        overlap_end: datetime.date,
    ):
        self.functions = functions
        self.leaf_name = leaf_name
        self.module_name = module_name
        self.overlap_start = overlap_start
        self.overlap_end = overlap_end

    def __str__(self):
        overlapping_functions = [func.original_function_name for func in self.functions]
        return f"""
        Functions with leaf name {self.leaf_name} in module {self.module_name} have
        overlapping start and end dates. The following functions are affected: \n\n
        {", ".join(overlapping_functions)} \n Overlapping
        from {self.overlap_start} to {self.overlap_end}."""


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


def load_internal_aggregation_tree(variant: _AggregationVariant) -> dict[str, Any]:
    """
    Load the aggregation tree.

    The aggregation pytree is a dictionary that specifies how to aggregate the results
    of functions. It is used to derive new functions from existing ones.

    Parameters
    ----------
    variant:
        The variant of the aggregation tree to load. Can be either 'aggregate_by_group'
        or 'aggregate_by_p_id'.

    Returns
    -------
    dict:
        The aggregation tree.
    """
    return _build_aggregations_tree(PATHS_TO_INTERNAL_FUNCTIONS, RESOURCE_DIR, variant)


def _build_aggregations_tree(
    roots: list[Path], package_root: Path, variant: _AggregationVariant
) -> dict[str, Any]:
    """
    Build the aggregation tree.

    Parameters
    ----------
    roots:
        The roots from which to start the search for dictionaries.
    package_root:
        The root of the package that contains the functions. This is required to assign
        qualified names to the functions. It must contain all roots.
    variant:
        The variant of the aggregation tree to load. Can be either 'aggregate_by_group'
        or 'aggregate_by_p_id'.

    Returns
    -------
    dict:
        The aggregation tree.
    """
    roots = roots if isinstance(roots, list) else [roots]
    paths = _find_python_files_recursively(roots)

    tree = {}

    for path in paths:
        derived_function_specs = _load_functions_to_derive(
            path, package_root, f"{variant}_"
        )

        # Remove recurring branch names in last two branches of path
        # This is done to avoid namespaces like arbeitslosengeld__arbeitslosengeld if
        # the file structure looks like this:
        # arbeitslosengeld
        #           |- arbeitslosengeld.py
        #           |- ...

        if len(path) >= 2:
            qualified_name_path = path[:-1] if path[-1] == path[-2] else path
        else:
            qualified_name_path = path

        tree = tree_update(
            tree=tree,
            path=qualified_name_path,
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

    return (
        {
            name: AggregationSpec(aggregation_specs=spec, target_name=name)
            for name, spec in dicts_in_module[0].items()
        }
        if dicts_in_module
        else {}
    )


def _fail_if_more_than_one_dict_loaded(dicts: list[dict], module_name: str) -> None:
    if len(dicts) > 1:
        raise ValueError(
            "More than one dictionary found in the module:\n\n" f"{module_name}\n\n"
        )
