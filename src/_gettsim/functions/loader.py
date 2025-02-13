import datetime
import importlib.util
import inspect
import itertools
import sys
from pathlib import Path
from types import ModuleType

from _gettsim.aggregation import AggregateByGroupSpec, AggregateByPIDSpec
from _gettsim.config import (
    PATHS_TO_INTERNAL_FUNCTIONS,
    RESOURCE_DIR,
)
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.gettsim_typing import NestedAggregationSpecDict, NestedFunctionDict
from _gettsim.shared import format_errors_and_warnings, upsert_path_and_value


def load_policy_functions_tree_for_date(date: datetime.date) -> NestedFunctionDict:
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

    policy_functions_tree = {}

    for system_path in system_paths_to_policy_functions:
        active_functions_dict = get_active_policy_functions_from_module(
            system_path=system_path, date=date, package_root=RESOURCE_DIR
        )

        tree_path = _convert_system_path_to_tree_path(
            system_path=system_path, package_root=RESOURCE_DIR
        )

        policy_functions_tree = upsert_path_and_value(
            tree=policy_functions_tree,
            tree_path=tree_path,
            value=active_functions_dict,
        )

    return policy_functions_tree


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

    _fail_if_leaf_name_is_module_name(policy_functions, module_name)
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


def _load_module(system_path: Path, package_root: Path) -> ModuleType:
    module_name = _convert_path_to_importable_module_name(system_path, package_root)
    spec = importlib.util.spec_from_file_location(module_name, system_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def _convert_path_to_importable_module_name(
    system_path: Path, package_root: Path
) -> str:
    """
    Convert an absolute path to a Python module name.

    Examples
    --------
    >>> _convert_path_to_importable_module_name(RESOURCE_DIR / "taxes" / "functions.py")
    "taxes.functions"
    """
    return (
        system_path.relative_to(package_root.parent)
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
    # TODO(@MImmesberger): Delete removeprefix calls after changing directory structure
    # https://github.com/iza-institute-of-labor-economics/gettsim/pull/805
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


def load_aggregations_tree() -> NestedAggregationSpecDict:
    """
    Load the aggregation tree.

    This function loads the aggregation tree from the internal functions by searching
    and loading all aggregation specifications from GETTSIM's modules.

    Returns
    -------
    NestedAggregationSpecDict:
        The aggregation tree.
    """
    system_paths_to_aggregation_specs = _find_python_files_recursively(
        PATHS_TO_INTERNAL_FUNCTIONS
    )

    aggregations_tree = {}

    for system_path in system_paths_to_aggregation_specs:
        derived_function_specs = _load_aggregation_specs_from_module(
            system_path=system_path,
            package_root=RESOURCE_DIR,
        )

        tree_path = _convert_system_path_to_tree_path(
            system_path=system_path, package_root=RESOURCE_DIR
        )

        aggregations_tree = upsert_path_and_value(
            tree=aggregations_tree,
            tree_path=tree_path,
            value=derived_function_specs,
        )

    return aggregations_tree


def _load_aggregation_specs_from_module(
    system_path: Path,
    package_root: Path,
) -> dict[str, AggregateByGroupSpec | AggregateByPIDSpec]:
    """
    Load aggregation specifications from one module.

    Returns a dictionary with the name of the aggregation target as keys and the
    aggregation specifications as values.

    Parameters
    ----------
    path:
        The path to the module in which to search for dictionaries.

    Returns
    -------
    dictionaries:
        Loaded dictionaries.
    """
    # TODO(@MImmesberger): Temporary solution. Dataclasses will be applied to all
    # modules in the renaming PR. Then, 'aggregation_specs_in_module' will be a list of
    # dictionaries.
    # https://github.com/iza-institute-of-labor-economics/gettsim/pull/805
    module = _load_module(system_path, package_root)
    aggregation_specs_in_module = {  # Will become a list in renamings PR
        name: member
        for name, member in inspect.getmembers(module)
        if isinstance(member, dict)
        and name.startswith(("aggregate_by_group_", "aggregate_by_p_id_"))
    }

    aggregations_from_module = {}

    # Temporary solution.
    for type_name, specs_for_type in aggregation_specs_in_module.items():
        for name, spec in specs_for_type.items():
            aggregations_from_module[name] = (
                AggregateByGroupSpec(**spec)
                if type_name.startswith("aggregate_by_group_")
                else AggregateByPIDSpec(**spec)
            )

    return aggregations_from_module


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


def _fail_if_leaf_name_is_module_name(
    policy_functions: list[PolicyFunction],
    module_name: str,
) -> None:
    """No PolicyFunction should have the same leaf name as its module name."""
    leaf_names = [func.leaf_name for func in policy_functions]
    if module_name in leaf_names:
        msg = format_errors_and_warnings(
            f"PolicyFunctions in module {module_name} have the same leaf name as their "
            "module name."
        )
        raise ValueError(msg)
