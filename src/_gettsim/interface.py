import copy
import functools
import inspect
import warnings
from typing import Any, Literal, get_args

import dags
import networkx as nx
import optree
import pandas as pd

from _gettsim.combine_functions_in_tree import (
    combine_policy_functions_and_derived_functions,
)
from _gettsim.config import (
    DEFAULT_TARGETS,
    FOREIGN_KEYS,
    QUALIFIED_NAME_SEPARATOR,
    SUPPORTED_GROUPINGS,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.config import numpy_or_jax as np
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.gettsim_typing import (
    NestedArrayDict,
    NestedDataDict,
    NestedFunctionDict,
    NestedInputStructureDict,
    NestedSeriesDict,
    NestedTargetDict,
    check_series_has_expected_type,
    convert_series_to_internal_type,
)
from _gettsim.policy_environment import PolicyEnvironment
from _gettsim.shared import (
    KeyErrorMessage,
    assert_valid_gettsim_pytree,
    format_errors_and_warnings,
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    partition_tree_by_reference_tree,
    tree_structure_from_paths,
    upsert_path_and_value,
    upsert_tree,
)


def compute_taxes_and_transfers(
    data_tree: NestedDataDict,
    environment: PolicyEnvironment,
    targets_tree: NestedTargetDict | None = None,
    rounding: bool = True,
    debug: bool = False,
) -> NestedDataDict:
    """Compute taxes and transfers.

    Parameters
    ----------
    data_tree : NestedDataDict
        Data provided by the user.
    environment: PolicyEnvironment
        The policy environment which contains all necessary functions and parameters.
    targets_tree : NestedTargetDict | None
        The targets tree. By default, ``targets_tree`` is ``None`` and all key outputs
        as defined by `gettsim.config.DEFAULT_TARGETS` are returned.
    rounding : bool, default True
        Indicator for whether rounding should be applied as specified in the law.
    debug : bool
        The debug mode does the following:
            1. All necessary inputs and all computed variables are returned.
            2. If an exception occurs while computing one variable, the exception is
                skipped.

    Returns
    -------
    results : NestedDataDict
        The computed variables as a tree.

    """
    # Check user inputs
    _fail_if_targets_tree_not_valid(targets_tree)
    _fail_if_data_tree_not_valid(data_tree)
    _fail_if_environment_not_valid(environment)

    # Use default targets if no targets are provided.
    targets_tree = targets_tree if targets_tree else DEFAULT_TARGETS

    # Add derived functions to the functions tree.
    functions_tree = combine_policy_functions_and_derived_functions(
        environment=environment,
        targets_tree=targets_tree,
        data_tree=data_tree,
    )

    (
        functions_tree_overridden,
        functions_tree_not_overridden,
    ) = partition_tree_by_reference_tree(
        tree_to_partition=functions_tree,
        reference_tree=data_tree,
    )

    _warn_if_functions_overridden_by_data(functions_tree_overridden)
    data_tree_with_correct_types = _convert_data_to_correct_types(
        data_tree=data_tree,
        functions_tree_overridden=functions_tree_overridden,
    )

    functions_tree_with_partialled_parameters = (
        _round_and_partial_parameters_to_functions(
            functions_tree=functions_tree_not_overridden,
            params=environment.params,
            rounding=rounding,
        )
    )

    input_structure = dags.create_input_structure_tree(
        functions_tree_not_overridden,
    )

    # Remove unnecessary elements from user-provided data.
    input_data_tree = _create_input_data_for_concatenated_function(
        data_tree=data_tree_with_correct_types,
        functions_tree=functions_tree_with_partialled_parameters,
        targets_tree=targets_tree,
        input_structure=input_structure,
    )

    _fail_if_group_variables_not_constant_within_groups(input_data_tree)
    _fail_if_foreign_keys_are_invalid(
        data_tree=input_data_tree,
        p_ids=data_tree_with_correct_types.get("groupings", {}).get("p_id", {}),
    )

    tax_transfer_function = dags.concatenate_functions_tree(
        functions=functions_tree_with_partialled_parameters,
        targets=targets_tree,
        input_structure=input_structure,
        name_clashes="raise",
    )

    results = tax_transfer_function(input_data_tree)

    if debug:
        results = upsert_tree(
            base=results,
            to_upsert=data_tree_with_correct_types,
        )

    return results


def _convert_data_to_correct_types(
    data_tree: NestedDataDict, functions_tree_overridden: NestedFunctionDict
) -> NestedDataDict:
    """Convert all leafs of the data tree to the type that is expected by GETTSIM.

    Parameters
    ----------
    data_tree
        Data provided by the user.
    functions_tree_overridden
        Functions that are overridden by data.

    Returns
    -------
    Data with correct types.

    """
    collected_errors = ["The data types of the following columns are invalid:\n"]
    collected_conversions = [
        "The data types of the following input variables have been converted:"
    ]
    general_warning = (
        "Note that the automatic conversion of data types is unsafe and that"
        " its correctness cannot be guaranteed."
        " The best solution is to convert all columns to the expected data"
        " types yourself."
    )

    data_tree_paths = optree.tree_accessors(data_tree)
    data_tree_with_correct_types = {}

    for accessor in data_tree_paths:
        qualified_column_name = QUALIFIED_NAME_SEPARATOR.join(accessor.path)
        data_leaf = accessor(data_tree)
        internal_type = None

        # Look for column in TYPES_INPUT_VARIABLES
        try:  # noqa: SIM105ga
            internal_type = accessor(TYPES_INPUT_VARIABLES)
        except KeyError:
            pass

        # Look for column in functions_tree_overridden
        try:
            func = accessor(functions_tree_overridden)
            if hasattr(func, "__annotations__") and func.skip_vectorization:
                # Assumes that things are annotated with numpy.ndarray([dtype]), might
                # require a change if using proper numpy.typing. Not changing for now
                # as we will likely switch to JAX completely.
                internal_type = get_args(func.__annotations__["return"])[0]
            else:
                internal_type = func.__annotations__["return"]
        except KeyError:
            pass

        # Make conversion if necessary
        if internal_type and not check_series_has_expected_type(
            series=data_leaf, internal_type=internal_type
        ):
            try:
                converted_leaf = convert_series_to_internal_type(
                    series=data_leaf, internal_type=internal_type
                )
                data_tree_with_correct_types = upsert_path_and_value(
                    base=data_tree_with_correct_types,
                    path_to_upsert=accessor.path,
                    value_to_upsert=converted_leaf,
                )
                collected_conversions.append(
                    f" - {qualified_column_name} from {data_leaf.dtype} "
                    f"to {internal_type.__name__}"
                )
            except ValueError as e:
                collected_errors.append(f"\n - {qualified_column_name}: {e}")
        else:
            data_tree_with_correct_types = upsert_path_and_value(
                base=data_tree_with_correct_types,
                path_to_upsert=accessor.path,
                value_to_upsert=data_leaf,
            )

    # If any error occured raise Error
    if len(collected_errors) > 1:
        msg = """
            Note that conversion from floating point to integers or Booleans inherently
            suffers from approximation error. It might well be that your data seemingly
            obey the restrictions when scrolling through them, but in fact they do not
            (for example, because 1e-15 is displayed as 0.0). \n The best solution is to
            convert all columns to the expected data types yourself.
            """
        collected_errors = "\n".join(collected_errors)
        raise ValueError(format_errors_and_warnings(collected_errors + msg))

    # Otherwise raise warning which lists all successful conversions
    elif len(collected_conversions) > 1:
        collected_conversions = format_list_linewise(collected_conversions)
        warnings.warn(
            collected_conversions + "\n" + "\n" + general_warning,
            stacklevel=2,
        )

    return data_tree_with_correct_types


def _create_input_data_for_concatenated_function(
    data_tree: NestedSeriesDict,
    functions_tree: NestedFunctionDict,
    targets_tree: NestedTargetDict,
    input_structure: NestedInputStructureDict,
) -> NestedArrayDict:
    """Create input data for the concatenated function.

    1. Check that all root nodes are present in the user-provided data tree.
    2. Get only part of the data tree that is needed for the concatenated function.
    3. Convert pandas.Series to numpy.array.

    Parameters
    ----------
    data_tree
        Data provided by the user.
    functions_tree
        Nested function dictionary.
    targets_tree
        Targets provided by the user.
    input_structure
        Tree representing the input structure.

    Returns
    -------
    Data which can be used to calculate taxes and transfers.

    """
    # Create dag using processed functions
    dag = dags.dag_tree.create_dag_tree(
        functions=functions_tree,
        targets=targets_tree,
        input_structure=input_structure,
        name_clashes="raise",
    )

    # Create root nodes tree
    root_nodes_view = nx.subgraph_view(dag, filter_node=lambda n: dag.in_degree(n) == 0)
    root_nodes_tree = tree_structure_from_paths(
        [tuple(node.split(QUALIFIED_NAME_SEPARATOR)) for node in root_nodes_view.nodes]
    )

    _fail_if_root_nodes_are_missing(
        functions_tree=functions_tree,
        data_tree=data_tree,
        root_nodes_tree=root_nodes_tree,
    )

    # Get only part of the data tree that is needed
    input_data_tree = partition_tree_by_reference_tree(
        tree_to_partition=data_tree,
        reference_tree=root_nodes_tree,
    )[0]

    # Convert to numpy.ndarray
    return optree.tree_map(lambda x: x.to_numpy(), input_data_tree)


def _round_and_partial_parameters_to_functions(
    functions_tree: NestedFunctionDict,
    params: dict[str, Any],
    rounding: bool,
) -> NestedFunctionDict:
    """Round and partial parameters into functions.

    Parameters
    ----------
    functions_tree
        The functions tree.
    params
        Dictionary of parameters.
    rounding
        Indicator for whether rounding should be applied as specified in the law.

    Returns
    -------
    Dictionary of rounded functions with parameters.

    """
    # Add rounding to functions.
    if rounding:
        functions_tree = optree.tree_map_with_path(
            lambda path, x: _add_rounding_to_function(x, params, path),
            functions_tree,
        )

    # Partial parameters to functions such that they disappear in the DAG.
    # Note: Needs to be done after rounding such that dags recognizes partialled
    # parameters.
    function_leafs, tree_spec = optree.tree_flatten(functions_tree)
    processed_functions = []
    for function in function_leafs:
        arguments = get_names_of_arguments_without_defaults(function)
        partial_params = {
            i: params[i[:-7]]
            for i in arguments
            if i.endswith("_params") and i[:-7] in params
        }
        if partial_params:
            processed_functions.append(functools.partial(function, **partial_params))
        else:
            processed_functions.append(function)

    return optree.tree_unflatten(tree_spec, processed_functions)


def _add_rounding_to_function(
    input_function: PolicyFunction,
    params: dict[str, Any],
    path: set[str],
) -> PolicyFunction:
    """Add appropriate rounding of outputs to function.

    Parameters
    ----------
    input_function : PolicyFunction
        Function to which rounding should be added.
    params : dict
        Dictionary of parameters

    Returns
    -------
    Function with rounding added.

    """
    func = copy.deepcopy(input_function)
    qualified_name = ".".join(path)
    leaf_name = path[-1]

    if input_function.params_key_for_rounding:
        params_key = func.params_key_for_rounding
        # Check if there are any rounding specifications.
        if not (
            params_key in params
            and "rounding" in params[params_key]
            and leaf_name in params[params_key]["rounding"]
        ):
            raise KeyError(
                KeyErrorMessage(
                    f"""
                    Rounding specifications for function {qualified_name} are expected
                    in the parameter dictionary at:\n
                    [{params_key!r}]['rounding'][{leaf_name!r}].\n
                    These nested keys do not exist. If this function should not be
                    rounded, remove the respective decorator.
                    """
                )
            )
        rounding_spec = params[params_key]["rounding"][leaf_name]
        # Check if expected parameters are present in rounding specifications.
        if not ("base" in rounding_spec and "direction" in rounding_spec):
            raise KeyError(
                KeyErrorMessage(
                    "Both 'base' and 'direction' are expected as rounding "
                    "parameters in the parameter dictionary. \n "
                    "At least one of them is missing at:\n"
                    f"[{params_key!r}]['rounding'][{leaf_name!r}]."
                )
            )
        # Add rounding.
        func = _apply_rounding_spec(
            base=rounding_spec["base"],
            direction=rounding_spec["direction"],
            to_add_after_rounding=rounding_spec.get("to_add_after_rounding", 0),
            path=path,
        )(func)

    return func


def _apply_rounding_spec(
    base: float,
    direction: Literal["up", "down", "nearest"],
    to_add_after_rounding: float,
    path: set[str],
) -> callable:
    """Decorator to round the output of a function.

    Parameters
    ----------
    base
        Precision of rounding (e.g. 0.1 to round to the first decimal place)
    direction
        Whether the series should be rounded up, down or to the nearest number
    to_add_after_rounding
        Number to be added after the rounding step
    path:
        Path to the function to be rounded.

    Returns
    -------
    Series with (potentially) rounded numbers

    """
    qualified_name = ".".join(path)

    def inner(func):
        # Make sure that signature is preserved.
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            out = func(*args, **kwargs)

            # Check inputs.
            if type(base) not in [int, float]:
                raise ValueError(
                    f"base needs to be a number, got {base!r} for " f"{qualified_name}"
                )
            if type(to_add_after_rounding) not in [int, float]:
                raise ValueError(
                    f"Additive part needs to be a number, got"
                    f" {to_add_after_rounding!r} for {qualified_name}"
                )

            if direction == "up":
                rounded_out = base * np.ceil(out / base)
            elif direction == "down":
                rounded_out = base * np.floor(out / base)
            elif direction == "nearest":
                rounded_out = base * (out / base).round()
            else:
                raise ValueError(
                    "direction must be one of 'up', 'down', or 'nearest'"
                    f", got {direction!r} for {qualified_name}"
                )

            rounded_out += to_add_after_rounding
            return rounded_out

        return wrapper

    return inner


def _fail_if_environment_not_valid(environment: Any) -> None:
    """
    Validate that the environment is a PolicyEnvironment.
    """
    if not isinstance(environment, PolicyEnvironment):
        raise TypeError(
            "The environment must be a PolicyEnvironment, got" f" {type(environment)}."
        )


def _fail_if_targets_tree_not_valid(targets_tree: NestedTargetDict) -> None:
    """
    Validate that the targets tree is a dictionary with string keys and None leaves.
    """
    assert_valid_gettsim_pytree(
        tree=targets_tree,
        leaf_checker=lambda leaf: leaf is None,
        tree_name="targets_tree",
    )


def _fail_if_data_tree_not_valid(data_tree: NestedDataDict) -> None:
    """
    Validate that the data tree is a dictionary with string keys and pd.Series or
    np.ndarray leaves.
    """
    assert_valid_gettsim_pytree(
        tree=data_tree,
        leaf_checker=lambda leaf: isinstance(leaf, pd.Series | np.ndarray),
        tree_name="data_tree",
    )
    _fail_if_pid_is_non_unique(data_tree)


def _fail_if_group_variables_not_constant_within_groups(
    data_tree: NestedDataDict,
) -> None:
    """
    Check that group variables are constant within each group.

    If the user provides a supported grouping ID (see SUPPORTED_GROUPINGS in config.py),
    the function checks that the corresponding data is constant within each group.

    Parameters
    ----------
    data_tree
        Nested dictionary with pandas.Series as leaf nodes.
    """
    # Extract group IDs from the 'groupings' branch.
    grouping_ids_in_data_tree = data_tree.get("groupings", {})

    def faulty_leaf(path, leaf):
        leaf_name = path[-1]
        for grouping in SUPPORTED_GROUPINGS:
            id_name = f"{grouping}_id"
            if leaf_name.endswith(grouping) and id_name in grouping_ids_in_data_tree:
                # Retrieve the corresponding group ID series from the data tree.
                group_id_series = grouping_ids_in_data_tree.get(id_name)
                # Group the leaf's series by the group ID and count unique values.
                unique_counts = leaf.groupby(group_id_series).nunique(dropna=False)
                if not (unique_counts == 1).all():
                    return True
                # No further check is needed for this leaf.
                break
        return False

    faulty_leaves_tree = optree.tree_map_with_path(faulty_leaf, data_tree)
    if optree.tree_any(faulty_leaves_tree):
        paths, leaves = optree.tree_flatten_with_path(faulty_leaves_tree)
        faulty = "\n".join(
            f"{'.'.join(paths[i])}" for i, leaf in enumerate(leaves) if leaf
        )
        msg = format_errors_and_warnings(
            f"""The following data inputs do not have a unique value within
                each group defined by the provided grouping IDs:\n
                {faulty}
                To fix this error, assign the same value to each group.
                """
        )
        raise ValueError(msg)


def _fail_if_pid_is_non_unique(data_tree: NestedDataDict) -> None:
    """Check that pid is unique."""
    p_id_col = data_tree.get("groupings", {}).get("p_id", None)
    if p_id_col is None:
        raise ValueError("The input data must contain the p_id.")

    # Check for non-unique p_ids
    p_id_counts = {}
    for p_id in p_id_col:
        if p_id in p_id_counts:
            p_id_counts[p_id] += 1
        else:
            p_id_counts[p_id] = 1

    non_unique_p_ids = [p_id for p_id, count in p_id_counts.items() if count > 1]

    if non_unique_p_ids:
        message = (
            "The following p_ids are non-unique in the input data:"
            f"{non_unique_p_ids}"
        )
        raise ValueError(message)


def _fail_if_foreign_keys_are_invalid(
    data_tree: NestedDataDict,
    p_ids: pd.Series,
) -> None:
    """
    Check that all foreign keys are valid.

    Foreign keys must point to an existing `p_id` in the input data and must not refer
    to the `p_id` of the same row.
    """
    grouping_ids = data_tree.get("groupings", {})
    valid_ids = set(p_ids) | {-1}

    def faulty_leaf(path, leaf):
        leaf_name = path[-1]
        foreign_key_col = leaf_name in FOREIGN_KEYS
        if not foreign_key_col:
            return leaf

        # Referenced `p_id` must exist in the input data
        if not all(i in valid_ids for i in leaf):
            message = format_errors_and_warnings(
                f"""
                The following {".".join(path)}s are not a valid p_id in the input
                data: {[i for i in leaf if i not in valid_ids]}.
                """
            )
            raise ValueError(message)

        # Referenced `p_id` must not be the same as the `p_id` of the same row
        equal_to_pid_in_same_row = [i for i, j in zip(leaf, p_ids) if i == j]
        if any(equal_to_pid_in_same_row):
            message = format_errors_and_warnings(
                f"""
                The following {".".join(path)}s are equal to the p_id in the same
                row: {[i for i, j in zip(leaf, p_ids) if i == j]}.
                """
            )
            raise ValueError(message)

    optree.tree_map_with_path(faulty_leaf, grouping_ids)


def _warn_if_functions_overridden_by_data(
    functions_tree_overridden: NestedFunctionDict,
) -> None:
    """Warn if functions are overridden by data."""
    tree_paths = optree.tree_paths(functions_tree_overridden)
    formatted_list = format_list_linewise(
        [QUALIFIED_NAME_SEPARATOR.join(path) for path in tree_paths]
    )
    if len(formatted_list) > 0:
        warnings.warn(
            FunctionsAndColumnsOverlapWarning(formatted_list),
            stacklevel=3,
        )


class FunctionsAndColumnsOverlapWarning(UserWarning):
    """
    Warning that functions which compute columns overlap with existing columns.

    Parameters
    ----------
    columns_overriding_functions : set[str]
        Names of columns in the data that override hard-coded functions.
    """

    def __init__(self, columns_overriding_functions: set[str]) -> None:
        n_cols = len(columns_overriding_functions)
        if n_cols == 1:
            first_part = format_errors_and_warnings("Your data provides the column:")
            second_part = format_errors_and_warnings(
                """
                This is already present among the hard-coded functions of the taxes and
                transfers system. If you want this data column to be used instead of
                calculating it within GETTSIM you need not do anything. If you want this
                data column to be calculated by hard-coded functions, remove it from the
                *data* you pass to GETTSIM. You need to pick one option for each column
                that appears in the list above.
                """
            )
        else:
            first_part = format_errors_and_warnings("Your data provides the columns:")
            second_part = format_errors_and_warnings(
                """
                These are already present among the hard-coded functions of the taxes
                and transfers system. If you want a data column to be used instead of
                calculating it within GETTSIM you do not need to do anything. If you
                want data columns to be calculated by hard-coded functions, remove them
                from the *data* you pass to GETTSIM. You need to pick one option for
                each column that appears in the list above.
                """
            )
        formatted = format_list_linewise(list(columns_overriding_functions))
        how_to_ignore = format_errors_and_warnings(
            """
            If you want to ignore this warning, add the following code to your script
            before calling GETTSIM:

                import warnings
                from gettsim import FunctionsAndColumnsOverlapWarning

                warnings.filterwarnings(
                    "ignore",
                    category=FunctionsAndColumnsOverlapWarning
                )
            """
        )
        super().__init__(f"{first_part}\n{formatted}\n{second_part}\n{how_to_ignore}")


def _fail_if_root_nodes_are_missing(
    functions_tree: NestedFunctionDict,
    root_nodes_tree: NestedTargetDict,
    data_tree: NestedDataDict,
) -> None:
    """Fail if root nodes are missing.

    Fails if there are root nodes in the DAG (i.e. nodes without predecessors that do
    not depend on parameters only) that are not present in the data tree.

    Parameters
    ----------
    functions_tree
        Dictionary of functions.
    root_nodes_tree
        Dictionary of root nodes.
    data_tree
        Dictionary of data.

    Raises
    ------
    ValueError
        If root nodes are missing.
    """
    root_nodes_accessors = optree.tree_accessors(root_nodes_tree, none_is_leaf=True)
    data_paths = optree.tree_paths(data_tree)
    functions = optree.tree_paths(functions_tree)
    missing_nodes = []

    for accessor in root_nodes_accessors:
        if accessor.path in functions:
            func = accessor(functions_tree)
            if _func_depends_on_parameters_only(func):
                # Function depends on parameters only, so it does not have to be present
                # in the data tree.
                continue

        if accessor.path in data_paths:
            # Root node is present in the data tree.
            continue

        qualified_name = QUALIFIED_NAME_SEPARATOR.join(accessor.path)
        missing_nodes.append(qualified_name)

    if missing_nodes:
        formatted = format_list_linewise(missing_nodes)
        raise ValueError(f"The following data columns are missing.\n{formatted}")


def _func_depends_on_parameters_only(func: PolicyFunction) -> bool:
    """Check if a function depends on parameters only."""
    return (
        len(
            [a for a in inspect.signature(func).parameters if not a.endswith("_params")]
        )
        == 0
    )
