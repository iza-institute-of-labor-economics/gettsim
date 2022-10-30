import copy
import functools
import inspect
import textwrap
import warnings

import dags
import numpy as np
import pandas as pd

from gettsim.aggregation import grouped_all
from gettsim.aggregation import grouped_any
from gettsim.aggregation import grouped_count
from gettsim.aggregation import grouped_cumsum
from gettsim.aggregation import grouped_max
from gettsim.aggregation import grouped_mean
from gettsim.aggregation import grouped_min
from gettsim.aggregation import grouped_sum
from gettsim.config import DEFAULT_TARGETS
from gettsim.config import SUPPORTED_GROUPINGS
from gettsim.config import TYPES_INPUT_VARIABLES
from gettsim.config import USE_JAX
from gettsim.functions_loader import load_aggregation_dict
from gettsim.functions_loader import load_user_and_internal_functions
from gettsim.shared import format_list_linewise
from gettsim.shared import get_names_of_arguments_without_defaults
from gettsim.shared import parse_to_list_of_strings
from gettsim.typing import check_series_has_expected_type
from gettsim.typing import convert_series_to_internal_type


class KeyErrorMessage(str):
    """Subclass str to allow for line breaks in KeyError messages"""

    def __repr__(self):
        return str(self)


def compute_taxes_and_transfers(
    data,
    params,
    functions,
    aggregation_specs=None,
    targets=None,
    columns_overriding_functions=None,
    check_minimal_specification="ignore",
    rounding=True,
    debug=False,
):
    """Compute taxes and transfers.

    Parameters
    ----------
    data : pandas.Series or pandas.DataFrame or dict of pandas.Series
        Data provided by the user.
    params : dict
        A dictionary with parameters from the policy environment. For more information
        see the documentation of the :ref:`param_files`.
    functions : str, pathlib.Path, callable, module, imports statements, dict
        Function from the policy environment. Functions can be anything of the
        specified types and a list of the same objects. If the object is a dictionary,
        the keys of the dictionary are used as a name instead of the function name. For
        all other objects, the name is inferred from the function name.
    aggregation_specs : dict, default None
        A dictionary which contains specs for functions which aggregate variables on
        the tax unit or household level. The syntax is the same as for aggregation
        specs in the code base and as specified in
        [GEP 4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html).
    targets : str, list of str, default None
        String or list of strings with names of functions whose output is actually
        needed by the user. By default, ``targets`` is ``None`` and all key outputs as
        defined by `gettsim.config.DEFAULT_TARGETS` are returned.
    columns_overriding_functions : str list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    check_minimal_specification : {"ignore", "warn", "raise"}, default "ignore"
        Indicator for whether checks which ensure the most minimal configuration should
        be silenced, emitted as warnings or errors.
    rounding : bool, default True
        Indicator for whether rounding should be applied as specified in the law.
    debug : bool
        The debug mode does the following:

        1. All necessary inputs and all computed variables are returned.
        2. If an exception occurs while computing one variable, the exception is
           skipped.

    Returns
    -------
    results : pandas.DataFrame
        DataFrame containing computed variables.

    """

    # Set defaults for some parameters.
    targets = DEFAULT_TARGETS if targets is None else targets
    targets = parse_to_list_of_strings(targets, "targets")

    columns_overriding_functions = parse_to_list_of_strings(
        columns_overriding_functions, "columns_overriding_functions"
    )
    params = {} if params is None else params
    aggregation_specs = {} if aggregation_specs is None else aggregation_specs

    # Perform several checks on data.
    data = _process_and_check_data(
        data=data, columns_overriding_functions=columns_overriding_functions
    )

    # Load functions.
    functions_not_overriden, functions_overriden = load_and_check_functions(
        user_functions_raw=functions,
        columns_overriding_functions=columns_overriding_functions,
        targets=targets,
        data_cols=list(data),
        aggregation_specs=aggregation_specs,
    )

    # Convert data to expected type.
    data = _convert_data_to_correct_types(data, functions_overriden)

    # Select necessary nodes by creating a preliminary DAG.
    nodes = set_up_dag(
        all_functions=functions_not_overriden,
        targets=targets,
        columns_overriding_functions=columns_overriding_functions,
        check_minimal_specification=check_minimal_specification,
    ).nodes
    necessary_functions = {
        f_name: f for f_name, f in functions_not_overriden.items() if (f_name in nodes)
    }

    # Round and partial all necessary functions.
    processed_functions = _round_and_partial_parameters_to_functions(
        necessary_functions, params, rounding
    )

    # Create input data.
    input_data = create_input_data(
        data=data,
        processed_functions=processed_functions,
        targets=targets,
        columns_overriding_functions=columns_overriding_functions,
        check_minimal_specification=check_minimal_specification,
    )

    # Calculate results.
    tax_transfer_function = dags.concatenate_functions(
        processed_functions,
        targets,
        return_type="dict",
        aggregator=None,
        enforce_signature=True,
    )
    results = tax_transfer_function(**input_data)

    # Prepare results.
    prepared_results = prepare_results(results, data, debug)

    return prepared_results


def create_input_data(
    data,
    processed_functions,
    targets,
    columns_overriding_functions,
    check_minimal_specification,
):
    # Create dag using processed functions
    dag = set_up_dag(
        all_functions=processed_functions,
        targets=targets,
        columns_overriding_functions=columns_overriding_functions,
        check_minimal_specification=check_minimal_specification,
    )
    root_nodes = set(_root_nodes(dag))
    _fail_if_root_nodes_are_missing(root_nodes, data, processed_functions)
    data = _reduce_to_necessary_data(root_nodes, data, check_minimal_specification)

    # Convert series to numpy arrays
    data = {key: series.values for key, series in data.items()}

    # Restrict to root nodes
    input_data = {k: v for k, v in data.items() if k in root_nodes}
    return input_data


def load_and_check_functions(
    user_functions_raw,
    columns_overriding_functions,
    targets,
    data_cols,
    aggregation_specs,
):
    """Load internal functions. Add aggregation functions and user functions. Perform
    some checks.

    Parameters
    ----------
    user_functions_raw : dict
        A dictionary mapping variable names to policy functions by the user.
    columns_overriding_functions : str list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    targets : list of str
        List of strings with names of functions whose output is actually needed by the
        user.
    data_cols : list
        Data columns provided by the user.
    aggregation_specs : dict
        A dictionary which contains specs for functions which aggregate variables on
        the tax unit or household level. The syntax is the same as for aggregation
        specs in the code base and as specified in
        [GEP 4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html)

    Returns
    -------
    functions_not_overriden : dict
        All functions except the ones that are overridden by an input column.
    functions_overriden : dict
        Functions that are overridden by an input column.
    """
    user_functions, internal_functions = load_user_and_internal_functions(
        user_functions_raw
    )

    # Vectorize functions.
    user_and_internal_functions = {
        fn: vectorize_func(f)
        for fn, f in {**internal_functions, **user_functions}.items()
    }

    # Create and add aggregation functions.
    aggregation_funcs = _create_aggregation_functions(
        user_and_internal_functions, targets, data_cols, aggregation_specs
    )

    # Check for overlap of functions and data columns.
    if data_cols:
        data_cols_excl_overriding = [
            c for c in data_cols if c not in columns_overriding_functions
        ]
        for funcs, name in zip(
            [internal_functions, user_functions, aggregation_funcs],
            ["internal", "user", "aggregation"],
        ):
            _fail_if_functions_and_columns_overlap(
                data_cols_excl_overriding, funcs, name
            )

    all_functions = {**user_and_internal_functions, **aggregation_funcs}

    _fail_if_columns_overriding_functions_are_not_in_functions(
        columns_overriding_functions, all_functions
    )

    _fail_if_targets_not_in_functions_or_override_columns(
        all_functions, targets, columns_overriding_functions
    )

    # Select/remove functions that are overridden.
    functions_not_overriden = {
        k: v for k, v in all_functions.items() if k not in columns_overriding_functions
    }
    functions_overriden = {
        k: v for k, v in all_functions.items() if k in columns_overriding_functions
    }
    return functions_not_overriden, functions_overriden


def set_up_dag(
    all_functions,
    targets,
    columns_overriding_functions,
    check_minimal_specification,
):
    """Set up the DAG. Partial functions before that and add rounding afterwards.

    Parameters
    ----------
    all_functions : dict
        All internal and user functions except the ones that are overridden by an input
        column.
    targets : list of str
        List of strings with names of functions whose output is actually
        needed by the user. By default, ``targets`` contains all key outputs as
        defined by `gettsim.config.DEFAULT_TARGETS`.
    columns_overriding_functions : list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    check_minimal_specification : {"ignore", "warn", "raise"}, default "ignore"
        Indicator for whether checks which ensure the most minimal configuration should
        be silenced, emitted as warnings or errors.

    Returns
    -------
    dag : networkx.DiGraph
        The DAG of the tax and transfer system.
    """
    # Create DAG and perform checks which depend on data which is not part of the DAG
    # interface.

    dag = dags.dag.create_dag(
        functions=all_functions,
        targets=targets,
    )
    _fail_if_columns_overriding_functions_are_not_in_dag(
        dag, columns_overriding_functions, check_minimal_specification
    )

    return dag


def _fail_if_columns_overriding_functions_are_not_in_dag(
    dag, columns_overriding_functions, check_minimal_specification
):
    """Fail if ``columns_overriding_functions`` are not in the DAG.

    Parameters
    ----------
    dag : networkx.DiGraph
        The DAG which is limited to targets and their ancestors.
    columns_overriding_functions : list of str
        The nodes which are provided by columns in the data and do not need to be
        computed. These columns limit the depth of the DAG.
    check_minimal_specification : {"ignore", "warn", "raise"}, default "ignore"
        Indicator for whether checks which ensure the most minimalistic configuration
        should be silenced, emitted as warnings or errors.

    Warnings
    --------
    UserWarning
        Warns if there are columns in 'columns_overriding_functions' which are not
        necessary and ``check_minimal_specification`` is set to "warn".
    Raises
    ------
    ValueError
        Raised if there are columns in 'columns_overriding_functions' which are not
        necessary and ``check_minimal_specification`` is set to "raise".

    """
    unused_columns = set(columns_overriding_functions) - set(dag.nodes)
    formatted = format_list_linewise(unused_columns)
    if unused_columns and check_minimal_specification == "warn":
        warnings.warn(
            f"The following 'columns_overriding_functions' are unused:\n{formatted}"
        )
    elif unused_columns and check_minimal_specification == "raise":
        raise ValueError(
            f"The following 'columns_overriding_functions' are unused:\n{formatted}"
        )


def prepare_results(results, data, debug):
    """Prepare results after DAG was executed

    Parameters
    ----------
    results : dict
        Dictionary of pd.Series with the results.
    data : dict
        Dictionary of pd.Series based on the input data provided by the user.
    debug : bool
        Indicates debug mode.

    Returns
    -------
    results : pandas.DataFrame
        Nicely formatted DataFrame of the results.

    """
    if debug:
        results = pd.DataFrame({**data, **results})
    else:
        results = pd.DataFrame(results)
    results = _reorder_columns(results)

    return results


def _convert_data_to_correct_types(data, functions_overriden):
    """Convert all series of data to the type that is expected by GETTSIM.

    Parameters
    ----------
    data : pandas.Series or pandas.DataFrame or dict of pandas.Series
        Data provided by the user.
    functions_overriden : dict of callable
        Functions to be overriden.

    Returns
    -------
    data : dict of pandas.Series with correct type

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
    for column_name, series in data.items():

        # Find out if internal_type is defined
        internal_type = None
        if column_name in TYPES_INPUT_VARIABLES:
            internal_type = TYPES_INPUT_VARIABLES[column_name]
        elif (
            column_name in functions_overriden
            and "return" in functions_overriden[column_name].__annotations__
        ):
            internal_type = functions_overriden[column_name].__annotations__["return"]

        # Make conversion if necessary
        if internal_type and not check_series_has_expected_type(series, internal_type):
            try:
                data[column_name] = convert_series_to_internal_type(
                    series, internal_type
                )
                collected_conversions.append(
                    f" - {column_name} from {series.dtype} "
                    f"to {internal_type.__name__}"
                )

            except ValueError as e:
                collected_errors.append(f" - {column_name}: {e}")

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

    # Otherwise raise warning which lists all sucessful conversions
    elif len(collected_conversions) > 1:
        warnings.warn("\n".join(collected_conversions) + "\n" + "\n" + general_warning)
    return data


def _process_and_check_data(data, columns_overriding_functions):
    """Process data and perform several checks.

    Parameters
    ----------
    data : pandas.Series or pandas.DataFrame or dict of pandas.Series
        Data provided by the user.
    columns_overriding_functions : str list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.

    Returns
    -------
    data : dict of pandas.Series

    """
    if isinstance(data, pd.DataFrame):
        _fail_if_duplicates_in_columns(data)
        data = dict(data)
    elif isinstance(data, pd.Series):
        data = {data.name: data}
    elif isinstance(data, dict) and all(
        isinstance(i, pd.Series) for i in data.values()
    ):
        pass
    else:
        raise NotImplementedError(
            "'data' is not a pd.DataFrame or a pd.Series or a dictionary of pd.Series."
        )
    # Check that group variables are constant within groups
    _fail_if_group_variables_not_constant_within_groups(data)

    _fail_if_columns_overriding_functions_are_not_in_data(
        list(data), columns_overriding_functions
    )
    _fail_if_pid_is_non_unique(data)

    return data


def _fail_if_group_variables_not_constant_within_groups(data):
    """Check whether group variables have the same
    value within each group. Possible groups are households or tax units.

    Parameters
    ----------
    data : dict of pandas.Series
        Dictionary containing a series for each column.

    """
    for name, col in data.items():
        for level in SUPPORTED_GROUPINGS:
            if name.endswith(f"_{level}"):
                max_value = col.groupby(data[f"{level}_id"]).transform("max")
                if not (max_value == col).all():
                    message = _format_text_for_cmdline(
                        f"""
                        Column '{name}' has not one unique value per group defined by
                        `{level}_id`.

                        This is expected if the variable name ends with '_{level}'.

                        To fix the error, assign the same value to each group or remove
                        the indicator from the variable name.
                        """
                    )
                    raise ValueError(message)
    return data


def _fail_if_columns_overriding_functions_are_not_in_data(data_cols, columns):
    """Fail if functions which compute columns overlap with existing columns.

    Parameters
    ----------
    data_cols : list
        Columns of the input data.
    columns : list of str
        List of column names.

    Raises
    ------
    ValueError
        Fail if functions which compute columns overlap with existing columns.

    """
    unused_columns_overriding_functions = sorted(
        c for c in set(columns) if c not in data_cols
    )
    n_cols = len(unused_columns_overriding_functions)

    column_sg_pl = "column" if n_cols == 1 else "columns"

    if unused_columns_overriding_functions:
        first_part = _format_text_for_cmdline(
            f"You passed the following user {column_sg_pl}:"
        )
        list_ = format_list_linewise(unused_columns_overriding_functions)

        second_part = _format_text_for_cmdline(
            f"""
            {'This' if n_cols == 1 else 'These'} {column_sg_pl} cannot be found in the
            data.

            If you want {'this' if n_cols == 1 else 'a'} data column to be used
            instead of calculating it within GETTSIM, please add it to *data*.

            If you want {'this' if n_cols == 1 else 'a'} data column to be calculated
            internally by GETTSIM, remove it from the *columns_overriding_functions* you
            pass to GETTSIM.

            {'' if n_cols == 1 else '''You need to pick one option for each column that
            appears in the list above.'''}
            """
        )
        raise ValueError("\n".join([first_part, list_, second_part]))


def _fail_if_columns_overriding_functions_are_not_in_functions(
    columns_overriding_functions, functions
):
    """Fail if ``columns_overriding_functions`` are not found in functions.

    Parameters
    ----------
    columns_overriding_functions : str list of str
        Names of columns which are preferred over function defined in the tax and
        transfer system.
    functions : dict of callable
        A dictionary of functions.

    Raises
    ------
    ValueError
        Fail if some ``columns_overriding_functions`` are not found in internal or user
        functions.

    """
    unnecessary_columns_overriding_functions = [
        col
        for col in columns_overriding_functions
        if (col not in functions) and (remove_group_suffix(col) not in functions)
    ]
    if unnecessary_columns_overriding_functions:
        n_cols = len(unnecessary_columns_overriding_functions)
        intro = _format_text_for_cmdline(
            f"""
            You passed the following user column{'' if n_cols == 1 else 's'} which {'is'
            if n_cols == 1 else 'are'} unnecessary because no functions require them as
            inputs.
            """
        )
        list_ = format_list_linewise(unnecessary_columns_overriding_functions)
        raise ValueError("\n".join([intro, list_]))


def _fail_if_functions_and_columns_overlap(columns, functions, type_):
    """Fail if functions which compute columns overlap with existing columns.

    Parameters
    ----------
    columns : list of str
        List of strings containing column names.
    functions : dict
        Dictionary of functions.
    type_ : {"internal", "user"}
        Source of the functions. "user" means functions passed by the user.

    Raises
    ------
    ValueError
        Fail if functions which compute columns overlap with existing columns.

    """
    if type_ == "internal":
        type_str = "internal "
    elif type_ == "aggregation":
        type_str = "internal aggregation "
    else:
        type_str = ""

    overlap = sorted(
        name
        for name in columns
        if (name in functions) or (remove_group_suffix(name) in functions)
    )

    if overlap:
        n_cols = len(overlap)
        first_part = _format_text_for_cmdline(
            f"Your data provides the column{'' if n_cols == 1 else 's'}:"
        )
        formatted = format_list_linewise(overlap)
        second_part = _format_text_for_cmdline(
            f"""
            {'This is' if n_cols == 1 else 'These are'} already present among the
            {type_str}functions of the taxes and transfers system.

            If you want {'this' if n_cols == 1 else 'a'} data column to be used
            instead of calculating it within GETTSIM, please specify it among the
            *columns_overriding_functions*{'.' if type_ == 'internal' else ''' or remove
            the function from *functions*.'''}

            If you want {'this' if n_cols == 1 else 'a'} data column to be calculated
            by {type_str}functions, remove it from the *data* you pass to GETTSIM.

            {'' if n_cols == 1 else '''You need to pick one option for each column that
            appears in the list above.'''}
            """
        )
        raise ValueError("\n".join([first_part, formatted, second_part]))


def _format_text_for_cmdline(text, width=79):
    """Format exception messages and warnings for the cmdline.

    Parameter
    ---------
    text : str
        The text which can include multiple paragraphs separated by two newlines.
    width : int
        The text will be wrapped by `width` characters.

    Returns
    -------
    formatted_text : str
        Correctly dedented, wrapped text.

    """
    text = text.lstrip("\n")
    paragraphs = text.split("\n\n")
    wrapped_paragraphs = []
    for paragraph in paragraphs:
        dedented_paragraph = textwrap.dedent(paragraph)
        wrapped_paragraph = textwrap.fill(dedented_paragraph, width=width)
        wrapped_paragraphs.append(wrapped_paragraph)

    formatted_text = "\n\n".join(wrapped_paragraphs)

    return formatted_text


def _reorder_columns(results):
    order_ids = {f"{g}_id": i for i, g in enumerate(SUPPORTED_GROUPINGS)}
    order_ids["p_id"] = len(order_ids)
    ids_in_data = order_ids.keys() & set(results.columns)
    sorted_ids = sorted(ids_in_data, key=lambda x: order_ids[x])
    remaining_columns = [i for i in results if i not in sorted_ids]

    return results[sorted_ids + remaining_columns]


def _fail_if_root_nodes_are_missing(root_nodes, data, functions):
    # Identify functions that are part of the DAG, but do not depend
    # on any other function
    funcs_based_on_params_only = [
        func_name
        for func_name, func in functions.items()
        if len(
            [a for a in inspect.signature(func).parameters if not a.endswith("_params")]
        )
        == 0
    ]
    # print(list(root_nodes))
    # print(data.keys())
    # print(funcs_based_on_params_only)

    missing_nodes = [
        c for c in root_nodes if c not in data and c not in funcs_based_on_params_only
    ]
    if missing_nodes:
        formatted = format_list_linewise(missing_nodes)
        raise ValueError(f"The following data columns are missing.\n{formatted}")


def _reduce_to_necessary_data(root_nodes, data, check_minimal_specification):

    # Produce warning or fail if more than necessary data is given.
    unnecessary_data = set(data) - root_nodes
    formatted = format_list_linewise(unnecessary_data)
    message = f"The following columns in 'data' are unused.\n\n{formatted}"
    if unnecessary_data and check_minimal_specification == "warn":
        warnings.warn(message)
    elif unnecessary_data and check_minimal_specification == "raise":
        raise ValueError(message)

    return {k: v for k, v in data.items() if k not in unnecessary_data}


def _fail_if_pid_is_non_unique(data):
    """Check that pid is unique"""

    if "p_id" not in data:
        message = "The input data must contain the column p_id"
        raise ValueError(message)
    elif not data["p_id"].is_unique:
        list_of_nunique_ids = list(data["p_id"].loc[data["p_id"].duplicated()])
        message = (
            "The following p_ids are non-unique in the input data:"
            f"{list_of_nunique_ids}"
        )
        raise ValueError(message)


def _fail_if_duplicates_in_columns(data):
    """Check that all column names are unique"""
    if any(data.columns.duplicated()):
        duplicated = list(data.columns[data.columns.duplicated()])
        raise ValueError(
            "The following columns are non-unique in the input data:" f"{duplicated}"
        )


def _fail_if_targets_not_in_functions_or_override_columns(
    functions, targets, columns_overriding_functions
):
    """Fail if targets are not in functions.

    Parameters
    ----------
    functions : dict of callable
        Dictionary containing functions to build the DAG.
    targets : list of str
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.
    columns_overriding_functions : list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.

    Raises
    ------
    ValueError
        Raised if ``targets`` are not in functions.

    """
    targets_not_in_functions = (
        set(targets) - set(functions) - set(columns_overriding_functions)
    )
    if targets_not_in_functions:
        formatted = format_list_linewise(targets_not_in_functions)
        raise ValueError(
            f"The following targets have no corresponding function:\n{formatted}"
        )


def _root_nodes(dag):
    for node in dag.nodes:
        has_no_parents = len(list(dag.predecessors(node))) == 0
        if has_no_parents:
            yield node


def _add_rounding_to_one_function(base, direction):
    """Decorator to round the output of a function.

    Parameters
    ----------
    base : float
        Precision of rounding (e.g. 0.1 to round to the first decimal place)
    round_d : bool
        Whether rounding should be applied
    direction : str
        Whether the series should be rounded up, down or to the nearest number

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
            if not (type(base) in [int, float]):
                raise ValueError(
                    f"base needs to be a number, got '{base}' for '{func.__name__}'"
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
                    f", got '{direction}' for '{func.__name__}'"
                )
            return rounded_out

        return wrapper

    return inner


def _add_rounding_to_functions(functions, params):
    """Add appropriate rounding of outputs to functions

    Parameters
    ----------
    dag : networkx.DiGraph
        The DAG of the tax and transfer system.
    params : dict
        Dictionary of parameters

    Returns
    -------
    dag : networkx.DiGraph
        The DAG of the tax and transfer system with rounding applied to the functions
        in the DAG.

    """
    functions_new = copy.deepcopy(functions)

    for func_name, func in functions.items():

        # If function has rounding params attribute, look for rounding specs in
        # params dict.
        if hasattr(func, "__rounding_params_key__"):
            params_key = func.__rounding_params_key__

            # Check if there are any rounding specifications.
            if not (
                params_key in params
                and "rounding" in params[params_key]
                and func_name in params[params_key]["rounding"]
            ):
                raise KeyError(
                    KeyErrorMessage(
                        f"Rounding specifications for function {func_name} are expected"
                        " in the parameter dictionary \n"
                        f" at ['{params_key}']['rounding']['{func_name}']. These nested"
                        " keys do not exist. \n"
                        " If this function should not be rounded,"
                        " remove the respective decorator."
                    )
                )

            rounding_spec = params[params_key]["rounding"][func_name]

            # Check if expected parameters are present in rounding specifications.
            if not ("base" in rounding_spec and "direction" in rounding_spec):
                raise KeyError(
                    KeyErrorMessage(
                        "Both 'base' and 'direction' are expected as rounding "
                        "parameters in the parameter dictionary. \n "
                        "At least one of them "
                        f"is missing at ['{params_key}']['rounding']['{func_name}']."
                    )
                )

            # Add rounding.
            functions_new[func_name] = _add_rounding_to_one_function(
                base=rounding_spec["base"],
                direction=rounding_spec["direction"],
            )(func)

    return functions_new


def _round_and_partial_parameters_to_functions(functions, params, rounding):
    """Create a dictionary of all functions that are available.

    Parameters
    ----------
    functions : dict of callable
        Dictionary of functions which are either internal or user provided functions.
    params : dict
        Dictionary of parameters which is partialed to the function such that `params`
        are invisible to the DAG.
    rounding : bool
        Indicator for whether rounding should be applied as specified in the law.

    Returns
    -------
    processed_functions : dict of callable
        Dictionary mapping function names to rounded callables with partialed
        parameters.

    """
    # Add rounding to functions.
    if rounding:
        functions = _add_rounding_to_functions(functions, params)

    # Partial parameters to functions such that they disappear in the DAG.
    # Note: Needs to be done after rounding such that dags recognizes partialled
    # parameters.
    processed_functions = {}
    for name, function in functions.items():

        arguments = get_names_of_arguments_without_defaults(function)
        partial_params = {
            i: params[i[:-7]]
            for i in arguments
            if i.endswith("_params") and i[:-7] in params
        }
        if partial_params:
            partial_func = functools.partial(function, **partial_params)

            # Make sure that rounding parameter attribute is transferred to partial
            # function. Otherwise, this information would get lost.
            if hasattr(function, "__rounding_params_key__"):
                partial_func.__rounding_params_key__ = function.__rounding_params_key__

            processed_functions[name] = partial_func
        else:
            processed_functions[name] = function

    return processed_functions


def rchop(s, suffix):
    # ToDO: Replace by removesuffix when only python >= 3.9 is supported
    if suffix and s.endswith(suffix):
        out = s[: -len(suffix)]
    else:
        out = s
    return out


def remove_group_suffix(col):

    # Set default result
    out = col

    # Remove suffix from result if applicable
    for g in SUPPORTED_GROUPINGS:
        if col.endswith(f"_{g}"):
            out = rchop(col, f"_{g}")

    return out


def _create_aggregation_functions(
    user_and_internal_functions, targets, data_cols, user_provided_aggregation_specs
):
    """Create aggregation functions"""
    aggregation_dict = load_aggregation_dict()

    # Make specs for automated sum aggregation
    potential_source_cols = list(user_and_internal_functions) + data_cols
    potential_agg_cols = set(
        [
            arg
            for func in user_and_internal_functions.values()
            for arg in get_names_of_arguments_without_defaults(func)
        ]
        + targets
    )

    automated_sum_aggregation_cols = [
        col
        for col in potential_agg_cols
        if (col not in user_and_internal_functions)
        and any(col.endswith(f"_{g}") for g in SUPPORTED_GROUPINGS)
        and (remove_group_suffix(col) in potential_source_cols)
    ]
    automated_sum_aggregation_specs = {
        agg_col: {"aggr": "sum", "source_col": remove_group_suffix(agg_col)}
        for agg_col in automated_sum_aggregation_cols
    }

    # Add automated aggregation specs.
    # Note: For duplicate keys, explicitly set specs are treated with higher priority
    # than automated specs.
    aggregation_dict = {**automated_sum_aggregation_specs, **aggregation_dict}

    # Add user provided aggregation specs.
    # Note: For duplicate keys, user provided specs are treated with higher priority.
    aggregation_dict = {**aggregation_dict, **user_provided_aggregation_specs}

    # Create functions from specs
    aggregation_funcs = {
        agg_col: _create_one_aggregation_func(
            agg_col, agg_spec, user_and_internal_functions
        )
        for agg_col, agg_spec in aggregation_dict.items()
    }
    return aggregation_funcs


def rename_arguments(func=None, mapper=None, annotations=None):
    if not annotations:
        annotations = {}

    def decorator_rename_arguments(func):

        old_parameters = dict(inspect.signature(func).parameters)
        parameters = []
        for name, param in old_parameters.items():
            if name in mapper:
                parameters.append(param.replace(name=mapper[name]))
            else:
                parameters.append(param)

        signature = inspect.Signature(parameters=parameters)

        reverse_mapper = {v: k for k, v in mapper.items()}

        @functools.wraps(func)
        def wrapper_rename_arguments(*args, **kwargs):
            internal_kwargs = {}
            for name, value in kwargs.items():
                if name in reverse_mapper:
                    internal_kwargs[reverse_mapper[name]] = value
                elif name not in mapper:
                    internal_kwargs[name] = value
            return func(*args, **internal_kwargs)

        wrapper_rename_arguments.__signature__ = signature
        wrapper_rename_arguments.__annotations__ = annotations

        return wrapper_rename_arguments

    if callable(func):
        return decorator_rename_arguments(func)
    else:
        return decorator_rename_arguments


def _create_one_aggregation_func(agg_col, agg_specs, user_and_internal_functions):
    """Create an aggregation function based on aggregation specification.

    Parameters
    ----------
    agg_col : str
        Name of the aggregated column.
    agg_specs : dict
        Dictionary of aggregation specifications. Can contain the source column
        ("source_col") and the group ids ("group_id")
    user_and_internal_functions: dict
        Dictionary of functions.


    Returns
    -------
    aggregation_func : The aggregation func with the expected signature

    """

    # Read individual specification parameters and make sure nothing is missing
    try:
        aggr = agg_specs["aggr"]
    except KeyError:
        raise KeyError(
            f"No aggr keyword is specified for aggregation column {agg_col}."
        )

    if aggr != "count":
        try:
            source_col = agg_specs["source_col"]
        except KeyError:
            raise KeyError(
                f"Source_col is not specified for aggregation column {agg_col}."
            )

    # Identify grouping level
    group_id = None
    for g in SUPPORTED_GROUPINGS:
        if agg_col.endswith(f"_{g}"):
            group_id = f"{g}_id"
    if not group_id:
        raise ValueError(
            "Name of aggregated column needs to have a suffix "
            "indicating the group over which it is aggregated. "
            f"The name {agg_col} does not do so."
        )

    # Build annotations
    annotations = {group_id: int}
    if aggr == "count":
        annotations["return"] = int
    else:

        if (
            source_col in user_and_internal_functions
            and "return" in user_and_internal_functions[source_col].__annotations__
        ):
            annotations[source_col] = user_and_internal_functions[
                source_col
            ].__annotations__["return"]

            # Find out return type
            annotations["return"] = select_return_type(aggr, annotations[source_col])
        elif source_col in TYPES_INPUT_VARIABLES:
            annotations[source_col] = TYPES_INPUT_VARIABLES[source_col]

            # Find out return type
            annotations["return"] = select_return_type(aggr, annotations[source_col])
        else:
            # ToDo: Think about how type annotations of aggregations of user-provided
            # ToDo: input variables are handled
            pass

    # Define aggregation func
    if aggr == "count":

        @rename_arguments(mapper={"group_id": group_id}, annotations=annotations)
        def aggregation_func(group_id):
            return grouped_count(group_id)

    elif aggr == "sum":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_sum(source_col, group_id)

    elif aggr == "mean":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_mean(source_col, group_id)

    elif aggr == "max":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_max(source_col, group_id)

    elif aggr == "min":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_min(source_col, group_id)

    elif aggr == "any":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_any(source_col, group_id)

    elif aggr == "all":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_all(source_col, group_id)

    elif aggr == "cumsum":

        @rename_arguments(
            mapper={"source_col": source_col, "group_id": group_id},
            annotations=annotations,
        )
        def aggregation_func(source_col, group_id):
            return grouped_cumsum(source_col, group_id)

    else:
        raise ValueError(f"Aggr {aggr} is not implemented, yet.")

    return aggregation_func


def select_return_type(aggr, source_col_type):
    # Find out return type
    if (source_col_type == int) and (aggr in ["any", "all"]):
        return_type = bool
    elif (source_col_type == bool) and (aggr in ["sum"]):
        return_type = int
    else:
        return_type = source_col_type

    return return_type


def vectorize_func(func):
    signature = inspect.signature(func)

    # Vectorize
    if USE_JAX:

        # ToDo: user jnp.vectorize once all functions are compatible with jax
        # func_vec = jnp.vectorize(func)
        func_vec = np.vectorize(func)

    else:
        func_vec = np.vectorize(func)

    @functools.wraps(func)
    def wrapper_vectorize_func(*args, **kwargs):
        return func_vec(*args, **kwargs)

    wrapper_vectorize_func.__signature__ = signature

    return wrapper_vectorize_func
