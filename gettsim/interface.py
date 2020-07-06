import functools
import textwrap
import warnings

import pandas as pd

from gettsim.config import DEFAULT_TARGETS
from gettsim.config import ORDER_OF_IDS
from gettsim.dag import _dict_subset
from gettsim.dag import _fail_if_targets_not_in_functions
from gettsim.dag import create_dag
from gettsim.dag import execute_dag
from gettsim.functions_loader import load_user_and_internal_functions
from gettsim.shared import format_list_linewise
from gettsim.shared import get_names_of_arguments_without_defaults
from gettsim.shared import parse_to_list_of_strings


def compute_taxes_and_transfers(
    data,
    params,
    functions,
    targets=None,
    columns_overriding_functions=None,
    check_minimal_specification="ignore",
    debug=False,
):
    """Compute taxes and transfers.

    Parameters
    ----------
    data : pandas.DataFrame
        The data provided by the user.
    params : dict
        A dictionary with parameters from the policy environment.
    functions : str, pathlib.Path, callable, module, imports statements, dict
        Function from the policy environment. Functions can be anything of the specified
        types and a list of the same objects. If the object is a dictionary, the keys of
        the dictionary are used as a name instead of the function name. For all other
        objects, the name is inferred from the function name.
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
    targets = DEFAULT_TARGETS if targets is None else targets
    targets = parse_to_list_of_strings(targets, "targets")
    columns_overriding_functions = parse_to_list_of_strings(
        columns_overriding_functions, "columns_overriding_functions"
    )
    params = {} if params is None else params

    _fail_if_columns_overriding_functions_are_not_in_data(
        data, columns_overriding_functions
    )

    # Load functions and perform checks.
    functions, internal_functions = load_user_and_internal_functions(functions)
    columns = set(data) - set(columns_overriding_functions)
    for funcs, name in zip([internal_functions, functions], ["internal", "user"]):
        _fail_if_functions_and_columns_overlap(columns, funcs, name)

    # Create one dictionary of functions and perform check.
    functions = {**internal_functions, **functions}
    functions = {
        k: v for k, v in functions.items() if k not in columns_overriding_functions
    }
    _fail_if_targets_not_in_functions(functions, targets)

    # Partial parameters to functions such that they disappear in the DAG.
    functions = _partial_parameters_to_functions(functions, params)

    # Create DAG and perform checks which depend on data which is not part of the DAG
    # interface.
    dag = create_dag(
        functions, targets, columns_overriding_functions, check_minimal_specification
    )
    _fail_if_root_nodes_are_missing(dag, data)
    _fail_if_more_than_necessary_data_is_passed(dag, data, check_minimal_specification)

    # We delay the data preparation as long as possible such that other checks can fail
    # before this.
    data = data.copy(deep=True)
    data = _process_data(data)
    data = _reduce_data(data)
    ids = _dict_subset(data, set(data) & {"hh_id", "tu_id"})

    results = execute_dag(dag, data, targets, debug)

    results = _expand_data(results, ids)
    results = pd.DataFrame(results)

    if not debug:
        results = results[targets]

    results = _reorder_columns(results)

    return results


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

    return data


def _reduce_data(data):
    """Reduce columns in data which are defined for tax units and households.

    Since the input data might be a `pandas.DataFrame` which can only be rectangular,
    some columns contain the same value for groups of individuals. Possible groups are
    households or tax units.

    gettsim uses reduced `pandas.Series` internally which have the tax unit or household
    id as the index. Here, we check whether all values in a group are the same and then
    reduce the series.

    The reduction is inferred from the variable name.

    - The variable name ends with `"_tu"` or `"_hh"`.
    - The variable name includes `"_tu_"` or `"_hh_"`. This will be deprecated soon.

    Parameters
    ----------
    data : dict of pandas.Series
        Dictionary containing a series for each column.

    Returns
    -------
    data : dict of pandas.Series
        Dictionary containing a series for each column where some columns are reduced.

    Warnings
    --------
    PendingDeprecationWarning
        The indicators `"_tu_"` and `"_hh_"` will be deprecated in a future release.

    """
    for name, s in data.items():
        for level in ["hh", "tu"]:
            if f"_{level}_" in name or name.endswith(f"_{level}"):
                groups = data[f"{level}_id"]
                reduced_s = _reduce_series_to_value_per_group(name, s, level, groups)
                data[name] = reduced_s

    return data


def _expand_data(data, ids):
    """Expand series in data.

    Take the reduced variable which has the group id as index. Then, use the series
    which assigns each individual a group id and index the reduced variable. This create
    a series which has the correct length and values, but the index is the group id.
    Thus, assign the correct index.

    """
    for name, s in data.items():
        for level, level_name in {"hh": "household", "tu": "tax unit"}.items():
            if f"_{level}_" in name or name.endswith(f"_{level}"):
                try:
                    expanded_s = s.loc[ids[f"{level}_id"]]
                except KeyError:
                    raise KeyError(
                        f"The variable name '{name}' implies that it is a variable\n"
                        f"varying at the level of a '{level_name}'. That is, there \n"
                        f"must be one value per unique '{level}_id'.\n\n"
                        f"This is not the case.\n\n"
                        f"You will need to do one of the following:\n\n"
                        f"    - In case the correct level of the variable '{name}'\n"
                        f"      is not the '{level}'. In this case, the\n"
                        f"      name must neither include '_{level}_' nor end with "
                        f"      '_{level}'\n\n"
                        f"    - In case that the correct level is the 'level_name',\n"
                        f"      change the function '{name}' so that it returns a\n."
                        f"      series indexed by '{level}'."
                    )
                expanded_s.index = ids[f"{level}_id"].index
                data[name] = expanded_s

    return data


def _reduce_series_to_value_per_group(name, s, level, groups):
    """Reduce a series which contains the same value per group.

    Parameters
    ----------
    name : str
        Name of variable.
    s : pandas.Series
        Series containing data of `variable`.
    level : {"tu", "hh"}
        Name of level to group by.
    groups : pandas.Series
        Series containing data of `level`.

    Returns
    -------
    pandas.Series
        Reduced series.

    """
    grouper = s.groupby(groups)
    max_value = grouper.transform("max")
    if not (max_value == s).all():
        message = _format_text_for_cmdline(
            f"""
            Column '{name}' has not one unique value per group defined by `{level}_id`
            which is necessary to reduce the variable.

            Variables are automatically reduced to one value per group if the variable
            name contains an indicator like '_hh_' or '_tu_' or ends with '_hh' or
            '_tu'.

            To fix the error, assign the same value to each group or remove the
            indicator from the variable name.
            """
        )
        raise ValueError(message)

    return grouper.max()


def _fail_if_columns_overriding_functions_are_not_in_data(data, columns):
    """Fail if functions which compute columns overlap with existing columns.

    Parameters
    ----------
    data : dict of pandas.Series
        Dictionary containing data columns as Series.
    columns : list of str
        List of column names.

    Raises
    ------
    ValueError
        Fail if functions which compute columns overlap with existing columns.

    """
    unused_columns_overriding_functions = sorted(set(columns) - set(data))
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
    unnecessary_columns_overriding_functions = set(columns_overriding_functions) - set(
        functions
    )
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
    columns_overriding_functions : list of str
        Columns provided by the user.

    Raises
    ------
    ValueError
        Fail if functions which compute columns overlap with existing columns.

    """
    type_str = "internal " if type_ == "internal" else ""
    overlap = sorted(name for name in functions if name in columns)
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
    remaining_columns = [i for i in results.columns if i not in sorted_ids]

    return results[sorted_ids + remaining_columns]


def _fail_if_root_nodes_are_missing(dag, data):
    missing_nodes = []
    for node in _root_nodes(dag):
        if node not in data and "function" not in dag.nodes[node]:
            missing_nodes.append(node)

    if missing_nodes:
        formatted = format_list_linewise(missing_nodes)
        raise ValueError(f"The following data columns are missing.\n{formatted}")


def _fail_if_more_than_necessary_data_is_passed(dag, data, check_minimal_specification):
    root_nodes = set(_root_nodes(dag))
    unnecessary_data = set(data) - root_nodes
    formatted = format_list_linewise(unnecessary_data)
    message = f"The following columns in 'data' are unused.\n\n{formatted}"
    if unnecessary_data and check_minimal_specification == "warn":
        warnings.warn(message)
    elif unnecessary_data and check_minimal_specification == "raise":
        raise ValueError(message)


def _root_nodes(dag):
    for node in dag.nodes:
        has_no_parents = len(list(dag.predecessors(node))) == 0
        if has_no_parents:
            yield node


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
        partial_params = {
            i: params[i[:-7]]
            for i in get_names_of_arguments_without_defaults(function)
            if i.endswith("_params") and i[:-7] in params
        }

        # Fix old functions which requested the whole dictionary. Test if removable.
        if "params" in get_names_of_arguments_without_defaults(function):
            partial_params["params"] = params

        partialed_functions[name] = (
            functools.partial(function, **partial_params)
            if partial_params
            else function
        )

    return partialed_functions
