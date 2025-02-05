import datetime
import importlib.util
import inspect
import itertools
import sys
from pathlib import Path
from types import ModuleType
from typing import Literal, TypeAlias

from _gettsim.aggregation import AggregateByGroupSpec, AggregateByPIDSpec
from _gettsim.config import (
    PATHS_TO_INTERNAL_FUNCTIONS,
    RESOURCE_DIR,
)
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.gettsim_typing import NestedAggregationDict, NestedFunctionDict
from _gettsim.shared import tree_update


def load_functions_tree_for_date(date: datetime.date) -> NestedFunctionDict:
    """
    Load the functions tree for a given date.

    This function takes the list of root paths and searches for all modules containing
    PolicyFunctions. Then it loads all PolicyFunctions that are active at the given date
    and parses them into the functions tree.

    Parameters
    ----------
    date:
        The date for which policy functions should be loaded.

    Returns
    -------
    NestedFunctionDict:
        A tree of active PolicyFunctions.
    """
    system_paths_to_policy_functions = _find_python_files_recursively(
        PATHS_TO_INTERNAL_FUNCTIONS
    )

    functions_tree = {}

    for system_path in system_paths_to_policy_functions:
        active_functions_dict = get_active_policy_functions_from_module(
            system_path=system_path, date=date, package_root=RESOURCE_DIR
        )

        tree_path = _convert_system_path_to_tree_path(
            system_path=system_path, package_root=RESOURCE_DIR
        )

        functions_tree = tree_update(
            tree=functions_tree,
            path=tree_path,
            value=active_functions_dict,
        )

    return functions_tree


def get_active_policy_functions_from_module(
    system_path: Path,
    package_root: Path,
    date: datetime.date,
) -> dict[str, PolicyFunction]:
    """Extract all active PolicyFunctions from a module.

    Parameters
    ----------
    system_path
        The path to the module from which to extract the active functions.
    package_root
        The root of the package that contains the functions.
    date
        The date for which to extract the active functions.

    Returns
    -------
    dict[str, PolicyFunction]
        A dictionary of active PolicyFunctions with their leaf names as keys.
    """
    module = _load_module(system_path, package_root)
    module_name = _convert_path_to_importable_module_name(system_path, package_root)

    all_functions_in_module = inspect.getmembers(module)

    policy_functions = [
        func for _, func in all_functions_in_module if isinstance(func, PolicyFunction)
    ]

    _fail_if_multiple_policy_functions_are_active_at_the_same_time(
        policy_functions, module_name
    )

    return {
        func.leaf_name: func
        for func in policy_functions
        if func.is_active_at_date(date)
    }


def _fail_if_multiple_policy_functions_are_active_at_the_same_time(
    policy_functions: list[PolicyFunction],
    module_name: str,
) -> None:
    """Raises an ConflictingTimeDependentFunctionsError if multiple functions with the
    same leaf name are active at the same time.

    Parameters
    ----------
    policy_functions
        List of PolicyFunctions to check for conflicts.
    module_name
        The name of the module from which the PolicyFunctions are extracted.

    Raises
    ------
    ConflictingTimeDependentFunctionsError
        If multiple functions with the same name are active at the same time.
    """
    # Create mapping from leaf names to functions.
    leaf_names_to_funcs = {}
    for func in policy_functions:
        if func.leaf_name in leaf_names_to_funcs:
            leaf_names_to_funcs[func.leaf_name].append(func)
        else:
            leaf_names_to_funcs[func.leaf_name] = [func]

    # Check for overlapping start and end dates for time-dependent functions.
    for leaf_name, funcs in leaf_names_to_funcs.items():
        dates_active = [(f.start_date, f.end_date) for f in funcs]
        for (start1, end1), (start2, end2) in itertools.combinations(dates_active, 2):
            if start1 <= end2 and start2 <= end1:
                raise ConflictingTimeDependentFunctionsError(
                    affected_policy_functions=funcs,
                    leaf_name=leaf_name,
                    module_name=module_name,
                    overlap_start=max(start1, start2),
                    overlap_end=min(end1, end2),
                )


class ConflictingTimeDependentFunctionsError(Exception):
    def __init__(
        self,
        affected_policy_functions: list[PolicyFunction],
        leaf_name: str,
        module_name: str,
        overlap_start: datetime.date,
        overlap_end: datetime.date,
    ):
        self.affected_policy_functions = affected_policy_functions
        self.leaf_name = leaf_name
        self.module_name = module_name
        self.overlap_start = overlap_start
        self.overlap_end = overlap_end

    def __str__(self):
        overlapping_functions = [
            func.original_function_name for func in self.affected_policy_functions
        ]
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
    list[Path]
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


def _convert_system_path_to_tree_path(
    system_path: Path, package_root: Path
) -> tuple[str, ...]:
    """
    Convert a system path to a tree path.

    The system path is the path to the python module on the user's system. The tree path
    are the branches of the tree.

    Parameters
    ----------
    system_path:
        The path to the python module on the user's system.
    package_root:
        The root of the package that contains the functions.

    Returns
    -------
    tuple[str, ...]:
        The tree path.

    Examples
    --------
    >>> _convert_system_path_to_tree_path(RESOURCE_DIR / "taxes" / "dir"
        / "functions.py")
    ("dir", "functions")
    """
    # TODO(@MImmesberger): Remove the removeprefix calls once directory structure is
    #  changed.
    branches = tuple(
        system_path.relative_to(package_root.parent)
        .with_suffix("")
        .as_posix()
        .removeprefix("_gettsim/")
        .removeprefix("taxes/")
        .removeprefix("transfers/")
        .split("/")
    )
    return _simplify_tree_path_when_module_name_equals_dir_name(branches)


_AggregationVariant: TypeAlias = Literal["aggregate_by_group", "aggregate_by_p_id"]


def load_internal_aggregation_tree(
    variant: _AggregationVariant,
) -> NestedAggregationDict:
    """
    Load the aggregation tree.

    This function loads the aggregation tree from the internal functions by searching
    and loading all aggregation specifications from GETTSIM's modules.

    Parameters
    ----------
    variant:
        The variant of the aggregation tree to load. Can be either 'aggregate_by_group'
        or 'aggregate_by_p_id'.

    Returns
    -------
    NestedAggregationDict:
        The aggregation tree.
    """
    system_paths_to_aggregation_specs = _find_python_files_recursively(
        PATHS_TO_INTERNAL_FUNCTIONS
    )

    aggregation_tree = {}

    for system_path in system_paths_to_aggregation_specs:
        derived_function_specs = _load_aggregation_specs_from_module(
            path=system_path, package_root=RESOURCE_DIR, prefix_filter=f"{variant}_"
        )

        tree_path = _convert_system_path_to_tree_path(
            system_path=system_path, package_root=RESOURCE_DIR
        )

        aggregation_tree = tree_update(
            tree=aggregation_tree,
            path=tree_path,
            value=derived_function_specs,
        )

    return aggregation_tree


def _load_aggregation_specs_from_module(
    path: Path,
    package_root: Path,
    prefix_filter: str,
) -> dict:
    """
    Load aggregation specifications from one module.

    Returns a dictionary with the name of the aggregation target as keys and the
    aggregation specifications as values.

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
    aggregation_specs_in_module = [
        member
        for name, member in inspect.getmembers(module)
        if isinstance(member, dict) and name.startswith(prefix_filter)
    ]

    _fail_if_more_than_one_dict_loaded(aggregation_specs_in_module, module_name)

    return (
        {
            # TODO(@MImmesberger): Temporary solution. Dataclasses will be applied to
            # all modules in the renaming PR.
            # https://github.com/iza-institute-of-labor-economics/gettsim/pull/805
            name: AggregateByGroupSpec(**spec)
            if prefix_filter == "aggregate_by_group_"
            else AggregateByPIDSpec(**spec)
            for name, spec in aggregation_specs_in_module[0].items()
        }
        if aggregation_specs_in_module
        else {}
    )


def _simplify_tree_path_when_module_name_equals_dir_name(
    tree_path: tuple[str, ...],
) -> tuple[str, ...]:
    """
    Shorten path when a module lives a directory named the same way.

    This is done to avoid namespaces like arbeitslosengeld__arbeitslosengeld if the
    file structure looks like:
    arbeitslosengeld
    |           |- arbeitslosengeld.py
    |           |- ...
    """
    if len(tree_path) >= 2:
        out = tree_path[:-1] if tree_path[-1] == tree_path[-2] else tree_path
    else:
        out = tree_path

    return out


def _fail_if_more_than_one_dict_loaded(dicts: list[dict], module_name: str) -> None:
    if len(dicts) > 1:
        raise ValueError(
            "More than one dictionary found in the module:\n\n" f"{module_name}\n\n"
        )
