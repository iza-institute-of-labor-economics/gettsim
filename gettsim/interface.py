import copy
import textwrap

import pandas as pd

from gettsim.config import INTERNAL_FUNCTION_FILES
from gettsim.config import ORDER_OF_IDS
from gettsim.dag import _dict_subset
from gettsim.dag import create_dag
from gettsim.dag import create_function_dict
from gettsim.dag import execute_dag
from gettsim.dag import prune_dag
from gettsim.functions_loader import convert_paths_to_internal_functions_to_imports
from gettsim.functions_loader import load_functions


def compute_taxes_and_transfers(
    data,
    user_functions=None,
    user_columns=None,
    params=None,
    targets=None,
    return_dag=False,
    debug=False,
):
    """Compute taxes and transfers.

    Parameters
    ----------
    data : pandas.Series or pandas.DataFrame or dict of pandas.Series
        Data provided by the user.
    user_functions : dict
        Dictionary with user provided functions. The keys are the names of the function.
        The values are either callables or strings with absolute or relative import
        paths to a function. If functions have the same name as an existing gettsim
        function they override that function.
    user_columns : str list of str
        Names of columns which are preferred over function defined in the tax and
        transfer system.
    params : dict
        A pandas Series or dictionary with user provided parameters. Currently just
        mapping a parameter name to a parameter value, in the future we will need more
        metadata. If parameters have the same name as an existing parameter from the
        gettsim parameters database at the specified date they override that parameter.
    targets : str or list of str or None
        String or list of strings with names of functions whose output is actually
        needed by the user. By default, `targets` is `None` and all results are
        returned.
    return_dag : bool
        Indicates whether the DAG should be returned as well for inspection.
    debug : bool
        The debug mode does the following:

        1. All necessary inputs and all computed variables are returned.
        2. If an exception occurs while computing one variable, the exception is
           printed, but not raised. The computation of all dependent variables is
           skipped.

    Returns
    -------
    results : dict of pandas.Series
        Dictionary of Series containing the target quantities.
    dag : networkx.DiGraph or None
        The dag produced by the tax and transfer system.

    """
    data = copy.deepcopy(data)

    data = _process_data(data)
    ids = _dict_subset(data, set(data) & {"hh_id", "tu_id"})
    data = _reduce_data(data)

    if isinstance(targets, str):
        targets = [targets]

    if user_columns is None:
        user_columns = []
    elif isinstance(user_columns, str):
        user_columns = [user_columns]

    user_functions = [] if user_functions is None else user_functions
    user_functions = load_functions(user_functions)

    imports = convert_paths_to_internal_functions_to_imports(INTERNAL_FUNCTION_FILES)
    internal_functions = load_functions(imports)

    _fail_if_user_columns_are_not_in_data(data, user_columns)
    _fail_if_user_columns_are_not_in_functions(
        user_columns, internal_functions, user_functions
    )
    for funcs, name in zip([internal_functions, user_functions], ["internal", "user"]):
        _fail_if_functions_and_columns_overlap(data, funcs, name, user_columns)

    functions = create_function_dict(
        user_functions, internal_functions, user_columns, params
    )

    dag = create_dag(functions)

    if targets:
        dag = prune_dag(dag, targets)

        # Remove columns in data which are not used in the DAG.
        relevant_columns = set(data) & set(dag.nodes) | (
            set(data) & {"p_id", "hh_id", "tu_id"}
        )
        data = _dict_subset(data, relevant_columns)

    results = execute_dag(dag, data, targets, debug)

    results = _expand_data(results, ids)
    results = pd.DataFrame(results)

    if debug:
        results = _reorder_columns(results)
    elif len(targets) == 1:
        results = results[targets[0]]
    else:
        results = results[targets]
        results = _reorder_columns(results)

    if return_dag:
        results = (results, dag)

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
        for level in ["hh", "tu"]:
            if f"_{level}_" in name or name.endswith(f"_{level}"):
                expanded_s = s.loc[ids[f"{level}_id"]]
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


def _fail_if_user_columns_are_not_in_data(data, columns):
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
    unused_user_columns = sorted(set(columns) - set(data))
    n_cols = len(unused_user_columns)

    column_sg_pl = "column" if n_cols == 1 else "columns"

    if unused_user_columns:
        first_part = _format_text_for_cmdline(
            f"You passed the following user {column_sg_pl}:"
        )
        list_ = create_linewise_printed_list(unused_user_columns)

        second_part = _format_text_for_cmdline(
            f"""
            {'This' if n_cols == 1 else 'These'} {column_sg_pl} cannot be found in the
            data.

            If you want {'this' if n_cols == 1 else 'a'} data column to be used
            instead of calculating it within GETTSIM, please add it to *data*.

            If you want {'this' if n_cols == 1 else 'a'} data column to be
            calculated internally by GETTSIM, remove it from the *user_columns* you
            pass to GETTSIM.

            {'' if n_cols == 1 else '''You need to pick one option for each column that
            appears in the list above.'''}
            """
        )
        raise ValueError("\n".join([first_part, list_, second_part]))


def _fail_if_user_columns_are_not_in_functions(
    user_columns, internal_functions, user_functions
):
    """Fail if user columns are not found in functions.

    Parameters
    ----------
    user_columns : str list of str
        Names of columns which are preferred over function defined in the tax and
        transfer system.
    internal_functions : dict
        Dictionary with internally defined functions.
    user_functions : dict
        Dictionary with user provided functions. The keys are the names of the function.
        The values are either callables or strings with absolute or relative import
        paths to a function. If functions have the same name as an existing gettsim
        function they override that function.

    Raises
    ------
    ValueError
        Fail if the user columns are not found in internal or user functions.

    """
    unnecessary_user_columns = (
        set(user_columns) - set(internal_functions) - set(user_functions)
    )

    if unnecessary_user_columns:
        n_cols = len(unnecessary_user_columns)
        intro = _format_text_for_cmdline(
            f"""
            You passed the following user column{'' if n_cols == 1 else 's'} which {'is'
            if n_cols == 1 else 'are'} unnecessary because there {'is' if n_cols == 1
            else 'are'} no corresponding function{'' if n_cols == 1 else 's'} in the
            internal or user functions.
            """
        )
        list_ = create_linewise_printed_list(unnecessary_user_columns)
        raise ValueError("\n".join([intro, list_]))


def _fail_if_functions_and_columns_overlap(data, functions, type_, user_columns):
    """Fail if functions which compute columns overlap with existing columns.

    Parameters
    ----------
    data : dict of pandas.Series
        Dictionary containing data columns as Series.
    functions : dict
        Dictionary of functions.
    type_ : {"internal", "user"}
        Source of the functions.
    user_columns : list of str
        Columns provided by the user.

    Raises
    ------
    ValueError
        Fail if functions which compute columns overlap with existing columns.

    """
    overlap = sorted(
        name for name in functions if name in data and name not in user_columns
    )

    if overlap:
        n_cols = len(overlap)
        first_part = _format_text_for_cmdline(
            f"Your data provides the column{'' if n_cols == 1 else 's'}:"
        )

        list_ = create_linewise_printed_list(overlap)

        second_part = _format_text_for_cmdline(
            f"""
            {'This is' if n_cols == 1 else 'These are'} already present among the
            {type_} functions of the taxes and transfers system.

            If you want {'this' if n_cols == 1 else 'a'} data column to be used
            instead of calculating it within GETTSIM, please specify it among the
            *user_columns*{'.' if type_ == 'internal' else ''' or remove the function
            from *user_functions*.'''}

            If you want {'this' if n_cols == 1 else 'a'} data column to be calculated
            by {type_} functions, remove it from the *data* you pass to GETTSIM.

            {'' if n_cols == 1 else '''You need to pick one option for each column that
            appears in the list above.'''}
            """
        )
        raise ValueError("\n".join([first_part, list_, second_part]))


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


def create_linewise_printed_list(list_):
    formatted_list = '",\n    "'.join(list_)
    return textwrap.dedent(
        """
        [
            "{formatted_list}",
        ]
        """
    ).format(formatted_list=formatted_list)


def _reorder_columns(results):
    ids_in_data = {"hh_id", "p_id", "tu_id"} & set(results.columns)
    sorted_ids = sorted(ids_in_data, key=lambda x: ORDER_OF_IDS[x])
    remaining_columns = [i for i in results.columns if i not in sorted_ids]

    return results[sorted_ids + remaining_columns]
