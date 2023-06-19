import copy
import functools
import inspect
import warnings

import dags
import pandas as pd

from _gettsim.config import DEFAULT_TARGETS, SUPPORTED_GROUPINGS, TYPES_INPUT_VARIABLES
from _gettsim.config import numpy_or_jax as np
from _gettsim.functions_loader import load_and_check_functions
from _gettsim.gettsim_typing import (
    check_series_has_expected_type,
    convert_series_to_internal_type,
)
from _gettsim.shared import (
    KeyErrorMessage,
    format_errors_and_warnings,
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    parse_to_list_of_strings,
)


def compute_taxes_and_transfers(  # noqa: PLR0913
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
        see the documentation of the :ref:`params_files`.
    functions : str, pathlib.Path, callable, module, imports statements, dict
        Functions from the policy environment. Functions can be anything of the
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

    targets = DEFAULT_TARGETS if targets is None else targets
    targets = parse_to_list_of_strings(targets, "targets")
    columns_overriding_functions = parse_to_list_of_strings(
        columns_overriding_functions, "columns_overriding_functions"
    )
    params = {} if params is None else params
    aggregation_specs = {} if aggregation_specs is None else aggregation_specs

    # Process data and load dictionaries with functions.
    data = _process_and_check_data(
        data=data, columns_overriding_functions=columns_overriding_functions
    )
    functions_not_overridden, functions_overridden = load_and_check_functions(
        user_functions_raw=functions,
        columns_overriding_functions=columns_overriding_functions,
        targets=targets,
        data_cols=list(data),
        aggregation_specs=aggregation_specs,
    )
    data = _convert_data_to_correct_types(data, functions_overridden)

    # Select necessary nodes by creating a preliminary DAG.
    nodes = set_up_dag(
        all_functions=functions_not_overridden,
        targets=targets,
        columns_overriding_functions=columns_overriding_functions,
        check_minimal_specification=check_minimal_specification,
    ).nodes
    necessary_functions = {
        f_name: f for f_name, f in functions_not_overridden.items() if (f_name in nodes)
    }

    processed_functions = _round_and_partial_parameters_to_functions(
        necessary_functions, params, rounding
    )

    # Create input data.
    input_data = _create_input_data(
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

    if "unterhalt" in params:
        if (
            "mindestunterhalt" not in params["unterhalt"]
            and "unterhaltsvors_m" in processed_functions
        ):
            raise NotImplementedError(
                """
Unterhaltsvorschuss is not implemented yet prior to 2016, see
https://github.com/iza-institute-of-labor-economics/gettsim/issues/479.

        """
            )

    results = tax_transfer_function(**input_data)

    # Prepare results.
    prepared_results = _prepare_results(results, data, debug)

    return prepared_results


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

    # Check that tu_id and hh_id are matching. As long as we have not fixed the
    # Günstigerprüfung between Kinderzuschlag (calculated on tax unit level) and
    # Wohngeld/ALG 2 (calculated on hh level), we do not allow for more than one tax
    # unit within a household.
    # ToDo: Remove check once Günstigerprüfung ist taken care of.
    if ("tu_id" in data) and ("hh_id" in data):
        assert (
            not data["tu_id"].groupby(data["hh_id"]).std().max() > 0
        ), "We currently allow for only one tax unit within each household"

    _fail_if_columns_overriding_functions_are_not_in_data(
        list(data), columns_overriding_functions
    )
    _fail_if_pid_is_non_unique(data)

    return data


def _convert_data_to_correct_types(data, functions_overridden):
    """Convert all series of data to the type that is expected by GETTSIM.

    Parameters
    ----------
    data : pandas.Series or pandas.DataFrame or dict of pandas.Series
        Data provided by the user.
    functions_overridden : dict of callable
        Functions to be overridden.

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
            column_name in functions_overridden
            and "return" in functions_overridden[column_name].__annotations__
        ):
            internal_type = functions_overridden[column_name].__annotations__["return"]

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

    # Otherwise raise warning which lists all successful conversions
    elif len(collected_conversions) > 1:
        warnings.warn(
            "\n".join(collected_conversions) + "\n" + "\n" + general_warning,
            stacklevel=2,
        )
    return data


def _create_input_data(
    data,
    processed_functions,
    targets,
    columns_overriding_functions,
    check_minimal_specification="ignore",
):
    """Create input data for use in the calculation of taxes and transfers by:

    - reducing to necessary data
    - convert pandas.Series to numpy.array

    Parameters
    ----------
    data : Dict of pandas.Series
        Data provided by the user.
    processed_functions : dict of callable
        Dictionary mapping function names to callables.
    targets : list of str
        List of strings with names of functions whose output is actually needed by the
        user.
    columns_overriding_functions : str list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    check_minimal_specification : {"ignore", "warn", "raise"}, default "ignore"
        Indicator for whether checks which ensure the most minimal configuration should
        be silenced, emitted as warnings or errors.

    Returns
    -------
    input_data : Dict of numpy.array
        Data which can be used to calculate taxes and transfers.

    """
    # Create dag using processed functions
    dag = set_up_dag(
        all_functions=processed_functions,
        targets=targets,
        columns_overriding_functions=columns_overriding_functions,
        check_minimal_specification=check_minimal_specification,
    )
    root_nodes = {n for n in dag.nodes if list(dag.predecessors(n)) == []}
    _fail_if_root_nodes_are_missing(root_nodes, data, processed_functions)
    data = _reduce_to_necessary_data(root_nodes, data, check_minimal_specification)

    # Convert series to numpy arrays
    data = {key: series.values for key, series in data.items()}

    # Restrict to root nodes
    input_data = {k: v for k, v in data.items() if k in root_nodes}
    return input_data


def _fail_if_duplicates_in_columns(data):
    """Check that all column names are unique."""
    if any(data.columns.duplicated()):
        raise ValueError(
            "The following columns are non-unique in the input data:\n\n"
            f"{data.columns[data.columns.duplicated()]}"
        )


def _fail_if_group_variables_not_constant_within_groups(data):
    """Check whether group variables have the same value within each group.

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
                    message = format_errors_and_warnings(
                        f"""
                        Column {name!r} has not one unique value per group defined by
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
        first_part = format_errors_and_warnings(
            f"You passed the following user {column_sg_pl}:"
        )
        list_ = format_list_linewise(unused_columns_overriding_functions)

        second_part = format_errors_and_warnings(
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
        raise ValueError(f"{first_part}\n{list_}\n{second_part}")


def _fail_if_pid_is_non_unique(data):
    """Check that pid is unique."""
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
        warnings.warn(message, stacklevel=2)
    elif unnecessary_data and check_minimal_specification == "raise":
        raise ValueError(message)

    return {k: v for k, v in data.items() if k not in unnecessary_data}


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

            # Make sure any GETTSIM metadata is transferred to partial
            # function. Otherwise, this information would get lost.
            if hasattr(function, "__info__"):
                partial_func.__info__ = function.__info__

            processed_functions[name] = partial_func
        else:
            processed_functions[name] = function

    return processed_functions


def _add_rounding_to_functions(functions, params):
    """Add appropriate rounding of outputs to functions.

    Parameters
    ----------
    functions : dict of callable
        Dictionary of functions which are either internal or user provided functions.
    params : dict
        Dictionary of parameters

    Returns
    -------
    functions_new : dict of callable
        Dictionary of rounded functions.

    """
    functions_new = copy.deepcopy(functions)

    for func_name, func in functions.items():
        # If function has rounding params attribute, look for rounding specs in
        # params dict.
        if hasattr(func, "__info__") and "rounding_params_key" in func.__info__:
            params_key = func.__info__["rounding_params_key"]

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
                        f" at [{params_key!r}]['rounding'][{func_name!r}]. These nested"
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
                        f"is missing at [{params_key!r}]['rounding'][{func_name!r}]."
                    )
                )

            # Add rounding.
            functions_new[func_name] = _add_rounding_to_one_function(
                base=rounding_spec["base"],
                direction=rounding_spec["direction"],
            )(func)

    return functions_new


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
            if type(base) not in [int, float]:
                raise ValueError(
                    f"base needs to be a number, got {base!r} for {func.__name__!r}"
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
                    f", got {direction!r} for {func.__name__!r}"
                )
            return rounded_out

        return wrapper

    return inner


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
            f"The following 'columns_overriding_functions' are unused:\n{formatted}",
            stacklevel=2,
        )
    elif unused_columns and check_minimal_specification == "raise":
        raise ValueError(
            f"The following 'columns_overriding_functions' are unused:\n{formatted}"
        )


def _prepare_results(results, data, debug):
    """Prepare results after DAG was executed.

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


def _reorder_columns(results):
    order_ids = {f"{g}_id": i for i, g in enumerate(SUPPORTED_GROUPINGS)}
    order_ids["p_id"] = len(order_ids)
    ids_in_data = order_ids.keys() & set(results.columns)
    sorted_ids = sorted(ids_in_data, key=lambda x: order_ids[x])
    remaining_columns = [i for i in results if i not in sorted_ids]

    return results[sorted_ids + remaining_columns]
