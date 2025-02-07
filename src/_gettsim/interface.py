import copy
import functools
import inspect
import warnings
from typing import Any, Literal, get_args

import dags
import networkx
import optree
import pandas as pd

from _gettsim.combine_functions_in_tree import (
    combine_policy_functions_and_derived_functions,
)
from _gettsim.config import (
    DEFAULT_TARGETS,
    FOREIGN_KEYS,
    SUPPORTED_GROUPINGS,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.config import numpy_or_jax as np
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.gettsim_typing import (
    NestedDataDict,
    NestedFunctionDict,
    NestedInputStructureDict,
    NestedTargetDict,
    check_series_has_expected_type,
    convert_series_to_internal_type,
)
from _gettsim.groupings import create_groupings
from _gettsim.policy_environment import PolicyEnvironment
from _gettsim.shared import (
    KeyErrorMessage,
    assert_valid_pytree,
    create_tree_from_list_of_qualified_names,
    format_errors_and_warnings,
    format_list_linewise,
    get_by_path,
    get_names_of_arguments_without_defaults,
    get_path_from_qualified_name,
    merge_nested_dicts,
    partition_tree_by_reference_tree,
    tree_to_dict_with_qualified_name,
    tree_update,
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

    all_functions = combine_policy_functions_and_derived_functions(
        environment=environment,
        targets_tree=targets_tree,
        data_tree=data_tree,
    )

    functions_not_overridden, functions_overridden = partition_tree_by_reference_tree(
        target_tree=all_functions,
        reference_tree=data,
    )
    data = _convert_data_to_correct_types(data, functions_overridden)

    # Warn if columns override functions.
    names_of_columns_overriding_functions = set(
        tree_to_dict_with_qualified_name(functions_overridden).keys()
    )
    if len(names_of_columns_overriding_functions) > 0:
        warnings.warn(
            FunctionsAndColumnsOverlapWarning(names_of_columns_overriding_functions),
            stacklevel=2,
        )

    # Create parameter input structure.
    input_structure = dags.dag_tree.create_input_structure_tree(
        functions=functions_not_overridden,
        targets=None,  # None because no functions should be filtered out
    )

    # Select necessary nodes by creating a preliminary DAG.
    preliminary_dag = set_up_dag(
        all_functions=functions_not_overridden,
        targets=targets,
        names_of_columns_overriding_functions=names_of_columns_overriding_functions,
        input_structure=input_structure,
    )
    nodes = create_tree_from_list_of_qualified_names(preliminary_dag.nodes)
    # Round and partial parameters into functions that are nodes in the DAG.
    processed_functions = _round_and_partial_parameters_to_functions(
        partition_tree_by_reference_tree(functions_not_overridden, nodes)[1],
        environment.params,
        rounding,
    )

    # Input structure for final DAG.
    input_structure = dags.dag_tree.create_input_structure_tree(
        functions=processed_functions,
        targets=targets,
    )

    # Calculate results.
    tax_transfer_function = dags.concatenate_functions_tree(
        functions=processed_functions,
        targets=targets,
        input_structure=input_structure,
        name_clashes="raise",
    )

    # Create input data.
    input_data = _create_input_data(
        data=data,
        processed_functions=processed_functions,
        targets=targets,
        names_of_columns_overriding_functions=names_of_columns_overriding_functions,
        input_structure=input_structure,
    )

    results = tax_transfer_function(input_data)
    # Prepare results.
    prepared_results = _prepare_results(
        results, data, debug, return_dataframe=return_dataframe
    )

    return prepared_results


def build_targets_tree(targets: NestedTargetDict | list[str] | str) -> NestedTargetDict:
    """Build a tree from a list or dictionary of targets.

    Parameters
    ----------
    targets : dict[str, Any] | list[str] | str
        Targets provided by the user.

    Returns
    -------
    targets_tree : dict[str, Any]
        Dictionary representing the tree.

    """
    if isinstance(targets, str):
        targets = [targets]

    flattened_targets = optree.tree_flatten(targets)[0]
    all_leafs_none = all(el is None for el in flattened_targets)
    all_leafs_str_or_list = all(isinstance(el, str | list) for el in flattened_targets)

    if isinstance(targets, list):
        # Build targets tree from list of strings
        targets_tree = create_tree_from_list_of_qualified_names(targets)
    elif isinstance(targets, dict) and all_leafs_none:
        # Input is already the correct targets tree
        targets_tree = targets
    elif isinstance(targets, dict) and all_leafs_str_or_list:
        # Build targets tree if leafs are strings or lists of strings
        targets_tree = _build_targets_tree_from_dict(targets)
    else:
        raise NotImplementedError(
            "Targets must be either a list of strings or a dictionary."
        )

    return targets_tree


def _build_targets_tree_from_dict(targets: dict[str, dict | str]) -> NestedTargetDict:
    """Build a tree from a dictionary of targets.

    The dictionary follows the tree structure but the leafs are strings or lists, not
    None. This function is used to convert the dictionary to the correct tree structure.

    Parameters
    ----------
    targets : dict[str, Union[dict, str]]
        Dictionary of targets.
        Example: {"a": {"b": {"c": ["d", "e"]}}}

    Returns
    -------
    tree : NestedTargetDict
        Dictionary representing the tree.
        Example: {"a": {"b": {"c": {"d": None, "e": None}}}}

    """
    for k, v in targets.items():
        if isinstance(v, dict):
            targets[k] = _build_targets_tree_from_dict(v)
        elif isinstance(v, str):
            targets[k] = {v: None}
        elif isinstance(v, list):
            targets[k] = create_tree_from_list_of_qualified_names(v)

    return targets


def build_data_tree(data: NestedDataDict | pd.DataFrame) -> NestedDataDict:
    """Build a tree from a dictionary or DataFrame of data.

    Parameters
    ----------
    data : NestedDataDict | pd.DataFrame
        Data provided by the user.

    Returns
    -------
    data_tree : NestedDataDict
        Dictionary representing the tree.

    """
    _fail_if_data_not_dict_with_sequence_leafs_or_dataframe(data)

    if isinstance(data, pd.DataFrame):
        _fail_if_duplicates_in_columns(data)
        data_tree = _build_data_tree_from_df(data)
    else:
        data_tree = _use_correct_series_names(data)

    return data_tree


def _build_data_tree_from_df(data: pd.DataFrame) -> NestedDataDict:
    """Build a tree from a DataFrame of data.

    Parameters
    ----------
    data : pd.DataFrame
        Data provided by the user.

    Returns
    -------
    tree : dict
        Dictionary representing the tree.

    """
    tree = {}
    cols_to_paths = [get_path_from_qualified_name(cols) for cols in data.columns]
    for path, column in zip(cols_to_paths, data.columns):
        series = data[column].copy()
        series.name = path[-1]
        tree = tree_update(
            tree,
            path,
            series,
        )

    return tree


def _use_correct_series_names(data: NestedDataDict) -> NestedDataDict:
    """Use correct series names for the tree.

    Parameters
    ----------
    data : NestedDataDict
        Data provided by the user.

    Returns
    -------
    tree : NestedDataDict
        Dictionary representing the tree.

    """
    return optree.tree_map_with_path(
        lambda path, x: x.rename(path[-1])
        if isinstance(x, pd.Series)
        else pd.Series(x, name=path[-1]),
        data,
    )


def set_up_dag(
    all_functions: NestedFunctionDict,
    targets: NestedTargetDict,
    input_structure: NestedInputStructureDict,
) -> networkx.DiGraph:
    """Set up the DAG. Partial functions before that and add rounding afterwards.

    Parameters
    ----------
    all_functions : dict
        All internal and user functions except the ones that are overridden by an input
        column.
    targets : dict
        Tree names of functions whose output is actually needed by the user as leafs. By
        default, ``targets`` contains all key outputs as defined by
        `gettsim.config.DEFAULT_TARGETS`.
    input_structure : dict
        Tree representing the input structure.

    Returns
    -------
    dag : networkx.DiGraph
        The DAG of the tax and transfer system.

    """
    # Create DAG and perform checks which depend on data which is not part of the DAG
    # interface.
    return dags.dag_tree.create_dag_tree(
        functions=all_functions,
        targets=targets,
        input_structure=input_structure,
        name_clashes="raise",
    )


def _convert_data_to_correct_types(
    data: NestedDataDict, functions_overridden: NestedFunctionDict
) -> NestedDataDict:
    """Convert all series of data to the type that is expected by GETTSIM.

    Parameters
    ----------
    data : dict tree with pandas.Series as leafs
        Data provided by the user.
    functions_overridden : dict tree with PolicyFunction as leafs
        Functions to be overridden.

    Returns
    -------
    data : dict tree with pandas.Series as leafs

    """
    collected_errors = ["The data types of the following columns are invalid: \n"]
    collected_conversions = [
        "The data types of the following input variables have been converted: \n"
    ]
    general_warning = (
        "Note that the automatic conversion of data types is unsafe and that"
        " its correctness cannot be guaranteed."
        " The best solution is to convert all columns to the expected data"
        " types yourself."
    )

    data_dict = tree_to_dict_with_qualified_name(data)
    names_to_functions_dict = tree_to_dict_with_qualified_name(functions_overridden)

    types_input_variables_with_qualified_names = tree_to_dict_with_qualified_name(
        TYPES_INPUT_VARIABLES
    )

    data_with_correct_types = []
    for column_name, series in data_dict.items():
        # Find out if internal_type is defined
        internal_type = None
        if column_name in types_input_variables_with_qualified_names:
            internal_type = types_input_variables_with_qualified_names[column_name]
        elif (
            column_name in names_to_functions_dict
            and "return" in names_to_functions_dict[column_name].__annotations__
        ):
            func = names_to_functions_dict[column_name]
            if hasattr(func, "__info__") and func.__info__["skip_vectorization"]:
                # Assumes that things are annotated with numpy.ndarray([dtype]), might
                # require a change if using proper numpy.typing. Not changing for now
                # as we will likely switch to JAX completely.
                internal_type = get_args(func.__annotations__["return"])[0]
            elif func in optree.tree_flatten(create_groupings())[0]:
                # Functions that create a grouping ID
                internal_type = get_args(func.__annotations__["return"])[0]
            else:
                internal_type = func.__annotations__["return"]

        # Make conversion if necessary
        if internal_type and not check_series_has_expected_type(series, internal_type):
            try:
                data_with_correct_types.append(
                    convert_series_to_internal_type(series, internal_type)
                )
                collected_conversions.append(
                    f" - {column_name} from {series.dtype} "
                    f"to {internal_type.__name__}"
                )
            except ValueError as e:
                collected_errors.append(f" - {column_name}: {e}")
        else:
            data_with_correct_types.append(series)

    # If any error occured raise Error
    if len(collected_errors) > 1:
        raise ValueError(
            "\n".join(collected_errors) + "\n" + "\n" + "Note that conversion"
            " from floating point to integers or Booleans inherently suffers from"
            " approximation error. It might well be that your data seemingly obey the"
            " restrictions when scrolling through them, but in fact they do not"
            " (for example, because 1e-15 is displayed as 0.0)."
            + "\n"
            + "The best solution is to convert all columns"
            " to the expected data types yourself."
        )

    # Otherwise raise warning which lists all successful conversions
    elif len(collected_conversions) > 1:
        warnings.warn(
            "\n".join(collected_conversions) + "\n" + "\n" + general_warning,
            stacklevel=2,
        )
    return data


def _create_input_data(
    processed_functions: NestedFunctionDict,
    data: NestedDataDict,
    targets: NestedTargetDict,
    names_of_columns_overriding_functions: list[str],
    input_structure: NestedInputStructureDict,
):
    """Create input data for use in the calculation of taxes and transfers by:

    - reducing to necessary data
    - convert pandas.Series to numpy.array

    Parameters
    ----------
    processed_functions : NestedFunctionDict
        Nested function dictionary.
    data : NestedDataDict
        Data provided by the user.
    targets : NestedTargetDict
        Targets provided by the user.
    names_of_columns_overriding_functions : list[str]
        Names of columns in the data that override hard-coded functions.
    input_structure : NestedInputStructureDict
        Tree representing the input structure.

    Returns
    -------
    input_data : NestedDataDict
        Data which can be used to calculate taxes and transfers.

    """
    # Create dag using processed functions
    dag = set_up_dag(
        all_functions=processed_functions,
        targets=targets,
        names_of_columns_overriding_functions=names_of_columns_overriding_functions,
        input_structure=input_structure,
    )
    root_nodes = {node for node in dag.nodes if list(dag.predecessors(node)) == []}
    data_cols = tree_to_dict_with_qualified_name(data).keys()
    _fail_if_root_nodes_are_missing(
        functions=processed_functions,
        root_nodes=root_nodes,
        data_cols=data_cols,
    )

    # Check that only necessary data is passed
    _, input_data = partition_tree_by_reference_tree(
        tree=data,
        qualified_names_list=root_nodes,
    )

    return tree_to_dict_with_qualified_name(
        optree.tree_map(lambda x: x.values, input_data)
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


def _round_and_partial_parameters_to_functions(
    functions: NestedFunctionDict,
    params: dict[str, Any],
    rounding: bool,
) -> NestedFunctionDict:
    """Round and partial parameters into functions.

    Parameters
    ----------
    functions: NestedFunctionDict
        Dictionary of functions which are either internal or user provided functions.
    params: dict[str, Any]
        Dictionary of parameters.
    rounding: bool
        Indicator for whether rounding should be applied as specified in the law.

    Returns
    -------
    processed_functions : NestedFunctionDict
        Dictionary of rounded functions with parameters.

    """
    # Add rounding to functions.
    if rounding:
        functions = optree.tree_map(
            lambda x: _add_rounding_to_function(x, params),
            functions,
        )

    # Partial parameters to functions such that they disappear in the DAG.
    # Note: Needs to be done after rounding such that dags recognizes partialled
    # parameters.
    function_leafs, tree_spec = optree.tree_flatten(functions)
    processed_functions = []
    for function in function_leafs:
        arguments = get_names_of_arguments_without_defaults(function)
        partial_params = {
            i: params[i[:-7]]
            for i in arguments
            if i.endswith("_params") and i[:-7] in params
        }
        if partial_params:
            # Partial parameters into function.
            partial_func = functools.partial(function, **partial_params)

            # Make sure any GETTSIM metadata is transferred to partial
            # function. Otherwise, this information would get lost.
            if hasattr(function, "__info__"):
                partial_func.__info__ = function.__info__

            processed_functions.append(partial_func)
        else:
            processed_functions.append(function)

    return optree.tree_unflatten(tree_spec, processed_functions)


def _add_rounding_to_function(
    input_function: PolicyFunction,
    params: dict[str, Any],
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
    functions_new : PolicyFunction
        Function with rounding added.

    """
    func = copy.deepcopy(input_function)

    if input_function.params_key_for_rounding:
        params_key = func.params_key_for_rounding
        qualified_name = func.qualified_name
        # Check if there are any rounding specifications.
        if not (
            params_key in params
            and "rounding" in params[params_key]
            and qualified_name in params[params_key]["rounding"]
        ):
            raise KeyError(
                KeyErrorMessage(
                    f"""
                    Rounding specifications for function {qualified_name} are expected
                    in the parameter dictionary \n at
                    [{params_key!r}]['rounding'][{qualified_name!r}]. These nested keys
                    do not exist. \n If this function should not be rounded, remove the
                    respective decorator.
                    """
                )
            )
        rounding_spec = params[params_key]["rounding"][qualified_name]
        # Check if expected parameters are present in rounding specifications.
        if not ("base" in rounding_spec and "direction" in rounding_spec):
            raise KeyError(
                KeyErrorMessage(
                    "Both 'base' and 'direction' are expected as rounding "
                    "parameters in the parameter dictionary. \n "
                    "At least one of them "
                    f"is missing at [{params_key!r}]['rounding'][{qualified_name!r}]."
                )
            )
        # Add rounding.
        func = _apply_rounding_spec(
            base=rounding_spec["base"],
            direction=rounding_spec["direction"],
            to_add_after_rounding=rounding_spec.get("to_add_after_rounding", 0),
        )(func)

    return func


def _apply_rounding_spec(
    base: float,
    direction: Literal["up", "down", "nearest"],
    to_add_after_rounding: float,
) -> callable:
    """Decorator to round the output of a function.

    Parameters
    ----------
    base : float
        Precision of rounding (e.g. 0.1 to round to the first decimal place)
    direction : str
        Whether the series should be rounded up, down or to the nearest number
    to_add_after_rounding : float
        Number to be added after the rounding step

    Returns
    -------
    results : pandas.Series
        Series with (potentially) rounded numbers

    """

    def inner(func):
        # Make sure that signature is preserved.
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            out = func(*args, **kwargs)

            # Check inputs.
            if type(base) not in [int, float]:
                raise ValueError(
                    f"base needs to be a number, got {base!r} for "
                    f"{func.qualified_name!r}"
                )
            if type(to_add_after_rounding) not in [int, float]:
                raise ValueError(
                    f"Additive part needs to be a number, got"
                    f" {to_add_after_rounding!r} for {func.qualified_name!r}"
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
                    f", got {direction!r} for {func.qualified_name!r}"
                )

            rounded_out += to_add_after_rounding
            return rounded_out

        return wrapper

    return inner


def _prepare_results(
    results: NestedDataDict,
    data: NestedDataDict,
    debug: bool,
    return_dataframe: bool = False,
) -> pd.DataFrame | NestedDataDict:
    """Prepare results after DAG was executed.

    Parameters
    ----------
    results : NestedDataDict
        Nested dictionary of results.
    data : NestedDataDict
        Nested dictionary of data.
    debug : bool
        Indicates debug mode.
    return_dataframe : bool, default False
        Indicates whether the results should be returned as a DataFrame.

    Returns
    -------
    results : pandas.DataFrame
        Nicely formatted DataFrame of the results.

    """
    if debug:
        out = merge_nested_dicts(data, results)
    else:
        out = results

    if return_dataframe:
        out = pd.DataFrame(tree_to_dict_with_qualified_name(out))
        out = _reorder_columns(out)

    return out


def _reorder_columns(results):
    order_ids = {f"{g}_id": i for i, g in enumerate(SUPPORTED_GROUPINGS)}
    order_ids["groupings__p_id"] = len(order_ids)
    ids_in_data = order_ids.keys() & set(results.columns)
    sorted_ids = sorted(ids_in_data, key=lambda x: order_ids[x])
    remaining_columns = [i for i in results if i not in sorted_ids]

    return results[sorted_ids + remaining_columns]


def _fail_if_environment_not_valid(environment: PolicyEnvironment) -> None:
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
    assert_valid_pytree(targets_tree, lambda leaf: leaf is None, "targets_tree")


def _fail_if_data_tree_not_valid(data_tree: NestedDataDict) -> None:
    """
    Validate that the data tree is a dictionary with string keys and pd.Series leaves.
    """
    assert_valid_pytree(
        data_tree, lambda leaf: isinstance(leaf, pd.Series), "data_tree"
    )
    _fail_if_pid_is_non_unique(data_tree)
    _fail_if_group_variables_not_constant_within_groups(data_tree)
    _fail_if_foreign_keys_are_invalid(data_tree)


def _fail_if_duplicates_in_columns(data: pd.DataFrame) -> None:
    """Check that all column names are unique."""
    if any(data.columns.duplicated()):
        raise ValueError(
            "The following columns are non-unique in the input data:\n\n"
            f"{data.columns[data.columns.duplicated()]}"
        )


def _fail_if_group_variables_not_constant_within_groups(
    data_tree: NestedDataDict,
) -> None:
    """Check whether group variables have the same value within each group.

    Parameters
    ----------
    data_tree :
        Data tree provided by the user.

    """
    names_leafs_dict = tree_to_dict_with_qualified_name(data_tree)

    grouped_data_cols = {
        name: col
        for name, col in names_leafs_dict.items()
        if any(name.endswith(grouping) for grouping in SUPPORTED_GROUPINGS)
    }
    group_ids_in_data = {
        name: col
        for name, col in names_leafs_dict.items()
        if name.endswith("_id") and name.split("_")[-2] in SUPPORTED_GROUPINGS
    }

    for name, col in grouped_data_cols.items():
        group_id_name = f"groupings__{name.split('_')[-1]}_id"

        try:
            group_id_array = group_ids_in_data[group_id_name]
        except KeyError:
            continue

        max_value = col.groupby(group_id_array).transform("max")
        if not (max_value == col).all():
            message = format_errors_and_warnings(
                f"""
                Data input {name!r} has not one unique value per group defined by
                {group_id_name!r}.

                To fix the error, assign the same value to each group.
                """
            )
            raise ValueError(message)


def _fail_if_group_variables_not_constant_within_groups(
    data_tree: NestedDataDict,
) -> None:
    """
    Check that group variables are constant within each group.

    If the user provides a supported grouping ID (see SUPPORTED_GROUPINGS in config.py),
    the function checks that the corresponding data is constant within each group.

    Parameters
    ----------
    data_tree :
        Nested dictionary with pandas.Series as leaf nodes.
    """
    # Extract group IDs from the 'groupings' branch.
    grouping_ids_in_data_tree = data_tree.get("groupings", {})

    def check_leaf(path, leaf):
        leaf_name = path[-1]
        for grouping in SUPPORTED_GROUPINGS:
            id_name = f"{grouping}_id"
            if leaf_name.endswith(grouping) and id_name in grouping_ids_in_data_tree:
                # Retrieve the corresponding group ID series from the data tree.
                group_id_series = grouping_ids_in_data_tree.get(id_name)
                # Group the leaf's series by the group ID and count unique values.
                unique_counts = leaf.groupby(group_id_series).nunique(dropna=False)
                if not (unique_counts == 1).all():
                    msg = format_errors_and_warnings(
                        f"""Data input {leaf_name!r} does not have a unique value within
                        each group defined by grouping '{grouping}'.

                        To fix this error, assign the same value to each group.
                        """
                    )
                    raise ValueError(msg)
                # No further check is needed for this leaf.
                break
        return leaf

    # Traverse the complete tree with optree; check_leaf is called for every leaf.
    optree.tree_map_with_path(check_leaf, data_tree)


def _fail_if_pid_is_non_unique(data: NestedDataDict) -> None:
    """Check that pid is unique."""
    try:
        p_id_col = get_by_path(data, ["groupings", "p_id"])
    except KeyError as e:
        message = "The input data must contain the p_id."
        raise ValueError(message) from e

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


def _fail_if_foreign_keys_are_invalid(data_tree: NestedDataDict) -> None:
    """
    Check that all foreign keys are valid.

    Foreign keys must point to an existing `p_id` in the input data and must not refer
    to the `p_id` of the same row.
    """
    p_id_col = get_by_path(data_tree, ["groupings", "p_id"])
    valid_ids = set(p_id_col) | {-1}
    grouping_ids = data_tree.get("groupings", {})

    def check_leaf(path, leaf):
        leaf_name = path[-1]
        foreign_key_col = leaf_name in FOREIGN_KEYS
        if not foreign_key_col:
            return leaf

        # Referenced `p_id` must exist in the input data
        if not all(i in valid_ids for i in leaf):
            message = format_errors_and_warnings(
                f"""
                The following {leaf_name}s are not a valid p_id in the input
                data: {[i for i in leaf if i not in valid_ids]}.
                """
            )
            raise ValueError(message)

        # Referenced `p_id` must not be the same as the `p_id` of the same row
        equal_to_pid_in_same_row = [i for i, j in zip(leaf, p_id_col) if i == j]
        if any(equal_to_pid_in_same_row):
            message = format_errors_and_warnings(
                f"""
                The following {leaf_name}s are equal to the p_id in the same
                row: {[i for i, j in zip(leaf, p_id_col) if i == j]}.
                """
            )
            raise ValueError(message)

    optree.tree_map_with_path(check_leaf, grouping_ids)


def _fail_if_root_nodes_are_missing(
    functions: NestedFunctionDict,
    root_nodes: list[str],
    data_cols: list[str],
) -> None:
    # Identify functions that are part of the DAG, but do not depend
    # on any other function
    names_to_functions_dict = tree_to_dict_with_qualified_name(functions)
    funcs_based_on_params_only = [
        func_name
        for func_name, func in names_to_functions_dict.items()
        if len(
            [a for a in inspect.signature(func).parameters if not a.endswith("_params")]
        )
        == 0
    ]

    missing_nodes = [
        c
        for c in root_nodes
        if (c not in data_cols and c not in funcs_based_on_params_only)
    ]
    if missing_nodes:
        formatted = format_list_linewise(missing_nodes)
        raise ValueError(f"The following data columns are missing.\n{formatted}")


def _fail_if_data_not_dict_with_sequence_leafs_or_dataframe(data: Any) -> None:
    """Fail if data is not a tree with sequence leaves or a DataFrame."""
    not_df = not isinstance(data, pd.DataFrame)
    not_dict = not isinstance(data, dict)
    not_sequence_leafs = any(
        not isinstance(el, pd.Series | np.ndarray | list)
        for el in optree.tree_flatten(data)[0]
    )

    if not_df and (not_dict or not_sequence_leafs):
        raise TypeError(
            """
            Data must be provided as a tree with sequence leaves (pd.Series, np.ndarray,
            or list) or as a DataFrame.
            """
        )
