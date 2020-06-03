import copy
import functools
import inspect
import textwrap
from pathlib import Path

import networkx as nx
import pandas as pd

from gettsim.functions_loader import load_functions


def compute_taxes_and_transfers(
    data,
    user_functions=None,
    user_columns=None,
    params=None,
    targets="all",
    return_dag=False,
):
    """Simulate a tax and transfers system specified in model_spec.

    Parameters
    ----------
    data : dict
        User provided dataset as dictionary of Series.
    user_functions : dict
        Dictionary with user provided functions. The keys are the names of the function.
        The values are either callables or strings with absolute or relative import
        paths to a function. If functions have the same name as an existing gettsim
        function they override that function.
    columns : str list of str
        Names of columns which are preferred over function defined in the tax and
        transfer system.
    params : dict
        A pandas Series or dictionary with user provided parameters. Currently just
        mapping a parameter name to a parameter value, in the future we will need more
        metadata. If parameters have the same name as an existing parameter from the
        gettsim parameters database at the specified date they override that parameter.
    targets : list
        List of strings with names of functions whose output is actually needed by the
        user. By default, all results are returned.

    Returns
    -------
    results : dict of pandas.Series
        Dictionary of Series containing the target quantities.
    dag : networkx.DiGraph or None
        The dag produced by the tax and transfer system.

    """
    data = copy.deepcopy(data)

    if isinstance(data, pd.DataFrame):
        data = dict(data)

    if isinstance(targets, str) and targets != "all":
        targets = [targets]

    if user_columns is None:
        user_columns = []
    elif isinstance(user_columns, str):
        user_columns = [user_columns]

    user_functions = [] if user_functions is None else user_functions
    user_functions = load_functions(user_functions)

    internal_functions = {}
    internal_function_files = [
        "soz_vers",
        "benefits",
        "taxes",
        "demographic_vars.py",
    ]
    for file in internal_function_files:
        new_funcs = load_functions(Path(__file__).parent / file)
        internal_functions.update(new_funcs)

    fail_if_user_columns_are_not_in_data(data, user_columns)
    for funcs, name in zip([internal_functions, user_functions], ["internal", "user"]):
        fail_if_functions_and_user_columns_overlap(data, funcs, name, user_columns)

    functions = create_function_dict(
        user_functions, internal_functions, user_columns, params
    )

    dag = create_dag(functions)

    if targets != "all":
        dag = prune_dag(dag, targets)

        # Remove columns in data which are not used in the DAG.
        relevant_columns = set(data) & set(dag.nodes)
        data = _dict_subset(data, relevant_columns)

    results = execute_dag(functions, dag, data, targets)

    if len(results) == 1:
        results = list(results.values())[0]

    if return_dag:
        results = (results, dag)

    return results


def create_function_dict(user_functions, internal_functions, user_columns, params):
    """Create a dictionary of all functions that will appear in the DAG.

    Parameters
    ----------
    user_functions : dict
        Dictionary with user provided functions. The keys are the names of the function.
        The values are either callables or strings with absolute or relative import
        paths to a function.
    internal_functions : dict
        Dictionary of functions provided by `gettsim`.
    user_columns : list
        Name of columns which are prioritized over functions.
    params : dict
        Dictionary of parameters which is partialed to the function such that `params`
        are invisible to the DAG.

    Returns
    -------
    partialed_functions : dict
        Dictionary mapping function names to callables with partialed parameters.

    """
    functions = {**internal_functions, **user_functions}

    # Remove functions whose results can be found in the `user_columns`.
    functions = {k: v for k, v in functions.items() if k not in user_columns}

    partialed_functions = {}
    for name, function in functions.items():
        partial_params = {
            i: params[i[:-7]]
            for i in inspect.getfullargspec(function).args
            if i.endswith("_params") and i[:-7] in params
        }
        if "params" in inspect.getfullargspec(function).args:
            partial_params["params"] = params

        partialed_functions[name] = functools.partial(function, **partial_params)

    return partialed_functions


def fail_if_user_columns_are_not_in_data(data, columns):
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

    formatted = '",\n    "'.join(unused_user_columns)
    column_sg_pl = "column" if n_cols == 1 else "columns"

    if unused_user_columns:
        first_part = format_text_for_cmdline(
            f"You passed the following user {column_sg_pl}:"
        )
        list_ = textwrap.dedent(
            """
            [
                "{formatted}",
            ]
            """
        ).format(formatted=formatted)

        second_part = format_text_for_cmdline(
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


def fail_if_functions_and_user_columns_overlap(data, functions, type_, user_columns):
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
    n_cols = len(overlap)

    formatted = '",\n    "'.join(overlap)

    if overlap:
        first_part = format_text_for_cmdline(
            f"Your data provides the column{'' if n_cols == 1 else 's'}:"
        )

        list_ = textwrap.dedent(
            """
            [
                "{formatted}",
            ]
            """
        ).format(formatted=formatted)

        second_part = format_text_for_cmdline(
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


def create_dag(func_dict):
    """Create a directed acyclic graph (DAG) capturing dependencies between functions.

    Parameters
    ----------
    func_dict : dict
        Maps function names to functions.

    Returns
    -------
    networkx.DiGraph
        The DAG, represented as a dictionary of lists that maps function names to a list
        of its data dependencies.

    """
    dag_dict = {
        name: inspect.getfullargspec(func).args for name, func in func_dict.items()
    }
    return nx.DiGraph(dag_dict).reverse()


def prune_dag(dag, targets):
    """Prune the dag.

    Parameters
    ----------
    dag : networkx.DiGraph
        The unpruned DAG.
    targets : list
        Variables of interest.

    Returns
    -------
    dag : networkx.DiGraph
        Pruned DAG.

    """
    # Go through the DAG from the targets to the bottom and collect all visited nodes.
    visited_nodes = set(targets)
    visited_nodes_changed = True
    while visited_nodes_changed:
        n_visited_nodes = len(visited_nodes)
        for node in visited_nodes:
            visited_nodes = visited_nodes.union(nx.ancestors(dag, node))

        visited_nodes_changed = n_visited_nodes != len(visited_nodes)

    # Redundant nodes are nodes not visited going from the targets through the graph.
    all_nodes = set(dag.nodes)
    redundant_nodes = all_nodes - visited_nodes

    dag.remove_nodes_from(redundant_nodes)

    return dag


def execute_dag(func_dict, dag, data, targets):
    """Naive serial scheduler for our tasks.

    We will probably use some existing scheduler instead. Interesting sources are:
    - https://ipython.org/ipython-doc/3/parallel/dag_dependencies.html
    - https://docs.dask.org/en/latest/graphs.html

    The main reason for writing an own implementation is to explore how difficult it
    would to avoid dask as a dependency.

    Parameters
    ----------
    func_dict : dict
        Maps function names to functions.
    dag : networkx.DiGraph
    data : dict
    targets : list

    Returns
    -------
    data : dict
        Dictionary of pd.Series with the resulting data.

    """
    # Needed for garbage collection.
    visited_nodes = set(data)

    for task in nx.topological_sort(dag):
        if task not in data:
            if task in func_dict:
                kwargs = _dict_subset(data, dag.predecessors(task))
                data[task] = func_dict[task](**kwargs).rename(task)
            else:
                dependants = list(dag.successors(task))
                raise KeyError(
                    f"Missing variable or function '{task}'. It is required to compute "
                    f"{dependants}."
                )

            visited_nodes.add(task)

            if targets != "all":
                data = collect_garbage(data, task, visited_nodes, targets, dag)

    return data


def _dict_subset(dictionary, keys):
    return {k: dictionary[k] for k in keys}


def collect_garbage(results, task, visited_nodes, targets, dag):
    """Remove data which is no longer necessary.

    If all descendants of a node have been evaluated, the information in the node
    becomes redundant and can be removed to save memory.

    Parameters
    ----------
    results : dict
    task : str
    visited_nodes : set
    dag : networkx.DiGraph

    Returns
    -------
    results : dict

    """
    for ancestor in dag.predecessors(task):
        is_obsolete = all(
            successor in visited_nodes for successor in dag.successors(ancestor)
        )

        if is_obsolete and ancestor not in targets:
            del results[ancestor]

    return results


def format_text_for_cmdline(text, width=79):
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
        dendented_paragraph = textwrap.dedent(paragraph)
        wrapped_paragraph = textwrap.fill(dendented_paragraph, width=width)
        wrapped_paragraphs.append(wrapped_paragraph)

    formatted_text = "\n\n".join(wrapped_paragraphs)

    return formatted_text
