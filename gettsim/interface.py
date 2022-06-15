import copy
import functools
import inspect
import textwrap
import warnings

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
from gettsim.config import ORDER_OF_IDS
from gettsim.config import TYPES_INPUT_VARIABLES
from gettsim.config import USE_JAX
from gettsim.dag import _fail_if_targets_not_in_functions_or_override_columns
from gettsim.dag import create_dag
from gettsim.dag import execute_dag
from gettsim.functions_loader import load_aggregation_dict
from gettsim.functions_loader import load_user_and_internal_functions
from gettsim.shared import format_list_linewise
from gettsim.shared import get_names_of_arguments_without_defaults
from gettsim.shared import parse_to_list_of_strings
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
           printed, but not raised. The computation of all dependent variables is
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

    # Load functions.
    user_functions, internal_functions = load_user_and_internal_functions(functions)

    # Perform several checks on functions and data. Merge internal and user functions.
    data = copy.deepcopy(data)
    data = _process_data(data)
    all_functions = check_data_check_functions_and_merge_functions(
        user_functions,
        internal_functions,
        columns_overriding_functions,
        targets,
        data,
        aggregation_specs,
    )

    # Set up dag.
    dag = prepare_functions_and_set_up_dag(
        all_functions=all_functions,
        targets=targets,
        params=params,
        columns_overriding_functions=columns_overriding_functions,
        check_minimal_specification=check_minimal_specification,
        rounding=rounding,
    )

    # Do some checks.
    _fail_if_root_nodes_are_missing(dag, data)
    _fail_if_pid_is_non_unique(data)
    data = _reduce_to_necessary_data(dag, data, check_minimal_specification)

    # Convert series to numpy arrays
    data = {key: series.values for key, series in data.items()}

    # Execute DAG.
    results = execute_dag(dag, data, targets, debug)

    # Prepare results.
    results = prepare_results(results, data, debug)

    return results


def check_data_check_functions_and_merge_functions(
    user_functions,
    internal_functions,
    columns_overriding_functions,
    targets,
    data,
    aggregation_specs,
):
    """Make some checks on input data and on interal and user functions. Merge internal
    and user functions and afterwards perform some more checks.

    Parameters
    ----------
    user_functions : dict
        A dictionary mapping variable names to policy functions by the user.
    internal_functions : dict
        A dictionary mapping variable names to all internal policy functions.
    columns_overriding_functions : str list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    targets : list of str
        List of strings with names of functions whose output is actually
        needed by the user.
    data : dict of pandas.Series
        Data provided by the user.
    aggregation_specs : dict
        A dictionary which contains specs for functions which aggregate variables on
        the tax unit or household level. The syntax is the same as for aggregation
        specs in the code base and as specified in
        [GEP 4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html)

    Returns
    -------
    all_functions : dict
        All internal and user functions except the ones that are overridden by an input
        column.
    """
    data_cols = list(data.keys())
    _fail_if_columns_overriding_functions_are_not_in_data(
        data_cols, columns_overriding_functions
    )

    data_cols_excl_overriding = [
        c for c in data_cols if c not in columns_overriding_functions
    ]

    # Create one dictionary of functions and perform check.
    user_and_internal_functions = {**internal_functions, **user_functions}

    # Vectorize functions
    user_and_internal_functions = {
        fn: vectorize_func(f) for fn, f in user_and_internal_functions.items()
    }

    # Create and add aggregation functions
    aggregation_funcs = _create_aggregation_functions(
        user_and_internal_functions, targets, data_cols, aggregation_specs
    )

    for funcs, name in zip(
        [internal_functions, user_functions, aggregation_funcs],
        ["internal", "user", "aggregation"],
    ):
        _fail_if_functions_and_columns_overlap(data_cols_excl_overriding, funcs, name)

    all_functions = {**user_and_internal_functions, **aggregation_funcs}

    _fail_if_columns_overriding_functions_are_not_in_functions(
        columns_overriding_functions, all_functions
    )
    data = _convert_data_to_correct_types(
        data, columns_overriding_functions, all_functions
    )

    # Remove functions that are overridden
    all_functions = {
        k: v for k, v in all_functions.items() if k not in columns_overriding_functions
    }

    return all_functions


def prepare_functions_and_set_up_dag(
    all_functions,
    targets,
    params,
    columns_overriding_functions,
    check_minimal_specification,
    rounding,
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
    params : dict
        A dictionary with parameters from the policy environment. For more
        information see the documentation of the :ref:`param_files`.
    columns_overriding_functions : list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    check_minimal_specification : {"ignore", "warn", "raise"}, default "ignore"
        Indicator for whether checks which ensure the most minimal configuration should
        be silenced, emitted as warnings or errors.
    rounding : bool, default True
        Indicator for whether rounding should be applied as specified in the law.

    Returns
    -------
    dag : networkx.DiGraph
        The DAG of the tax and transfer system.
    """
    _fail_if_targets_not_in_functions_or_override_columns(
        all_functions, targets, columns_overriding_functions
    )

    # Partial parameters to functions such that they disappear in the DAG.
    partialed_functions = _partial_parameters_to_functions(all_functions, params)

    # Create DAG and perform checks which depend on data which is not part of the DAG
    # interface.
    dag = create_dag(
        functions=partialed_functions,
        targets=targets,
        columns_overriding_functions=columns_overriding_functions,
        check_minimal_specification=check_minimal_specification,
    )

    # Add rounding to functions.
    if rounding:
        dag = _add_rounding_to_functions_in_dag(dag, params)

    return dag


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


def _convert_data_to_correct_types(data, columns_overriding_functions, functions):
    """Convert all series of data to the type that is expected by GETTSIM.

    Parameters
    ----------
    data : pandas.Series or pandas.DataFrame or dict of pandas.Series
        Data provided by the user.
    columns_overriding_functions : str list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    functions : dict of callable
        A dictionary of functions.

    Returns
    -------
    data : dict of pandas.Series with correct type

    """
    collected_errors = ["The data types of the following columns are invalid: \n"]
    for column_name, series in data.items():
        if column_name in TYPES_INPUT_VARIABLES:
            internal_type = TYPES_INPUT_VARIABLES[column_name]
            try:
                data[column_name] = convert_series_to_internal_type(
                    series, internal_type
                )
            except ValueError as e:
                collected_errors.append(f" - {column_name}: {e}")
        elif (
            column_name in columns_overriding_functions
            and "return" in functions[column_name].__annotations__
        ):
            internal_type = functions[column_name].__annotations__["return"]
            data[column_name] = convert_series_to_internal_type(series, internal_type)

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
    return data


def _process_data(data):
    """Process data.

    Parameters
    ----------
    data : pandas.Series or pandas.DataFrame or dict of pandas.Series
        Data provided by the user.

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

    # Check that group variables (e.g. ending with "_hh") are constant within groups
    _fail_if_group_variables_not_constant_within_groups(data)
    return data


def _fail_if_group_variables_not_constant_within_groups(data):
    """Check whether group variables (ending with `"_tu"` or `"_hh"`) have the same
    value within each group. Possible groups are households or tax units.

    Parameters
    ----------
    data : dict of pandas.Series
        Dictionary containing a series for each column.

    """
    for name, col in data.items():
        for level in ["hh", "tu"]:
            if name.endswith(f"_{level}"):
                max_value = col.groupby(data[f"{level}_id"]).transform("max")
                if not (max_value == col).all():
                    message = _format_text_for_cmdline(
                        f"""
                        Column '{name}' has not one unique value per group defined by
                        `{level}_id`.

                        This is expected if the variable name ends with '_hh' or '_tu'.

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
        if (col not in functions) and (rchop(rchop(col, "_tu"), "_hh") not in functions)
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
        if (name in functions) or (rchop(rchop(name, "_tu"), "_hh") in functions)
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
    ids_in_data = {"hh_id", "p_id", "tu_id"} & set(results.columns)
    sorted_ids = sorted(ids_in_data, key=lambda x: ORDER_OF_IDS[x])
    remaining_columns = [i for i in results if i not in sorted_ids]

    return results[sorted_ids + remaining_columns]


def _fail_if_root_nodes_are_missing(dag, data):
    missing_nodes = []
    for node in _root_nodes(dag):
        if node not in data and "function" not in dag.nodes[node]:
            missing_nodes.append(node)

    if missing_nodes:
        formatted = format_list_linewise(missing_nodes)
        raise ValueError(f"The following data columns are missing.\n{formatted}")


def _reduce_to_necessary_data(dag, data, check_minimal_specification):

    # Produce warning or fail if more than necessary data is given.
    root_nodes = set(_root_nodes(dag))
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


def _add_rounding_to_functions_in_dag(dag_raw, params):
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
    dag = copy.deepcopy(dag_raw)

    for task in dag:
        if "function" in dag.nodes[task]:
            func = dag.nodes[task]["function"]

            # If function has rounding params attribute, look for rounding specs in
            # params dict.
            if hasattr(func, "__rounding_params_key__"):
                params_key = func.__rounding_params_key__

                # Check if there are any rounding specifications.
                if not (
                    params_key in params
                    and "rounding" in params[params_key]
                    and task in params[params_key]["rounding"]
                ):
                    raise KeyError(
                        KeyErrorMessage(
                            f"Rounding specifications for function {task} are expected"
                            " in the parameter dictionary \n"
                            f" at ['{params_key}']['rounding']['{task}']. These nested"
                            " keys do not exist. \n"
                            " If this function should not be rounded,"
                            " remove the respective decorator."
                        )
                    )

                rounding_spec = params[params_key]["rounding"][task]

                # Check if expected parameters are present in rounding specifications.
                if not ("base" in rounding_spec and "direction" in rounding_spec):
                    raise KeyError(
                        KeyErrorMessage(
                            "Both 'base' and 'direction' are expected as rounding "
                            "parameters in the parameter dictionary. \n "
                            "At least one of them "
                            f"is missing at ['{params_key}']['rounding']['{task}']."
                        )
                    )
                # Add rounding.
                dag.nodes[task]["function"] = _add_rounding_to_one_function(
                    base=rounding_spec["base"],
                    direction=rounding_spec["direction"],
                )(dag.nodes[task]["function"])
    return dag


def _partial_parameters_to_functions(functions, params):
    """Create a dictionary of all functions that are available.

    Parameters
    ----------
    functions : dict of callable
        Dictionary of functions which are either internal or user provided functions.
    params : dict
        Dictionary of parameters which is partialed to the function such that `params`
        are invisible to the DAG.

    Returns
    -------
    partialed_functions : dict of callable
        Dictionary mapping function names to callables with partialed parameters.

    """
    partialed_functions = {}
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

            partialed_functions[name] = partial_func
        else:
            partialed_functions[name] = function

    return partialed_functions


def rchop(s, suffix):
    # ToDO: Replace by removesuffix when only python >= 3.9 is supported
    if suffix and s.endswith(suffix):
        return s[: -len(suffix)]
    return s


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
        and (col.endswith("_tu") or col.endswith("_hh"))
        and (rchop(rchop(col, "_tu"), "_hh") in potential_source_cols)
    ]
    automated_sum_aggregation_specs = {
        agg_col: {"aggr": "sum", "source_col": rchop(rchop(agg_col, "_tu"), "_hh")}
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
    if agg_col.endswith("_tu"):
        group_id = "tu_id"
    elif agg_col.endswith("_hh"):
        group_id = "hh_id"
    else:
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
