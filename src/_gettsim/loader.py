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
from _gettsim.function_types import GroupByFunction, PolicyFunction
from _gettsim.gettsim_typing import NestedAggregationSpecDict, NestedFunctionDict
from _gettsim.shared import (
    create_tree_from_path_and_value,
    insert_path_and_value,
    merge_trees,
)


def load_functions_tree_for_date(date: datetime.date) -> NestedFunctionDict:
    """
    Load the functions tree for a given date.

    This function takes the list of root paths and searches for all modules containing
    PolicyFunctions. Then it loads all PolicyFunctions that are active at the given date
    and constructs the functions tree.

    Namespaces are at the directory level.

    Parameters
    ----------
    date:
        The date for which policy functions should be loaded.

    Returns
    -------
    A tree of active PolicyFunctions.
    """
    paths_to_functions = _find_python_files_recursively(PATHS_TO_INTERNAL_FUNCTIONS)

    functions_tree = {}

    for path in paths_to_functions:
        new_functions_tree = get_active_functions_tree_from_module(
            path=path, date=date, package_root=RESOURCE_DIR
        )

        functions_tree = merge_trees(
            left=functions_tree,
            right=new_functions_tree,
        )

    return functions_tree


def get_active_functions_tree_from_module(
    path: Path,
    package_root: Path,
    date: datetime.date,
) -> dict[str, PolicyFunction | GroupByFunction]:
    """Extract all active PolicyFunctions and GroupByFunctions from a module.

    Parameters
    ----------
    path
        The path to the module from which to extract the active functions.
    package_root
        The root of the package that contains the functions.
    date
        The date for which to extract the active functions.

    Returns
    -------
    A nested dictionary of active PolicyFunctions and GroupByFunctions with their
    leaf names as keys.
    """
    module = _load_module(path, package_root)
    module_name = _convert_path_to_importable_module_name(path, package_root)

    all_functions_in_module = inspect.getmembers(module)

    policy_functions = [
        func for _, func in all_functions_in_module if isinstance(func, PolicyFunction)
    ]

    _fail_if_multiple_policy_functions_are_active_at_the_same_time(
        policy_functions, module_name
    )

    active_policy_functions = {
        func.leaf_name: func
        for _, func in all_functions_in_module
        if isinstance(func, PolicyFunction) and func.is_active(date)
    }

    group_by_functions = {
        func.leaf_name: func
        for _, func in all_functions_in_module
        if isinstance(func, GroupByFunction)
    }

    return create_tree_from_path_and_value(
        path=_convert_path_to_tree_path(path=path, package_root=RESOURCE_DIR),
        value={**active_policy_functions, **group_by_functions},
    )


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
    Absolute paths to all discovered Python files.
    """
    result = []

    for root in roots:
        if root.is_dir():
            modules = [
                file for file in root.rglob("*.py") if file.name != "__init__.py"
            ]
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
    >>> _convert_path_to_importable_module_name(
        path=Path("/usr/gettsim/src/_gettsim/taxes/functions.py"),
        package_root=Path("/usr/gettsim/src/_gettsim"),
    )
    "taxes.functions"
    """
    return path.relative_to(package_root).with_suffix("").as_posix().replace("/", ".")


def _convert_path_to_tree_path(path: Path, package_root: Path) -> tuple[str, ...]:
    """
    Convert the path from the package root to a tree path.

    Removes the package root and module name from the path.

    Parameters
    ----------
    path:
        The path to a Python module.
    package_root:
        GETTSIM's package root.

    Returns
    -------
    The tree path, to be used as a key in the functions tree.

    Examples
    --------
    >>> _convert_path_to_tree_path(
    ...     path=RESOURCE_DIR / "taxes" / "dir" / "functions.py",
    ...     package_root=RESOURCE_DIR,
    ... )
    ("dir")
    """
    parts = path.relative_to(package_root.parent / "_gettsim").parts

    # TODO(@MImmesberger): Remove the subsequent line after changing directory structure
    # https://github.com/iza-institute-of-labor-economics/gettsim/pull/805
    parts = parts[1:] if parts[0] in {"taxes", "transfers"} else parts

    return parts[:-1]


def load_aggregation_specs_tree() -> NestedAggregationSpecDict:
    """
    Load the tree with aggregation specifications.

    This function loads the tree with aggregation specifications from the internal
    functions by searching and loading all aggregation specifications from GETTSIM's
    modules.

    Returns
    -------
    The aggregation tree.
    """
    paths_to_aggregation_specs = _find_python_files_recursively(
        PATHS_TO_INTERNAL_FUNCTIONS
    )

    aggregation_specs_tree = {}

    for path in paths_to_aggregation_specs:
        aggregation_specs = _load_aggregation_specs_from_module(
            path=path,
            package_root=RESOURCE_DIR,
        )

        tree_path = _convert_path_to_tree_path(path=path, package_root=RESOURCE_DIR)

        aggregation_specs_tree = insert_path_and_value(
            base=aggregation_specs_tree,
            path_to_insert=tree_path,
            value_to_insert=aggregation_specs,
        )

    return aggregation_specs_tree


def _load_aggregation_specs_from_module(
    path: Path,
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
    Loaded dictionaries.
    """
    module = _load_module(path, package_root)
    return getattr(module, "aggregation_specs", {})
