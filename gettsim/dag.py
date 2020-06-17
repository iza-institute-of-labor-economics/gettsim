import functools
import inspect
import traceback

import networkx as nx


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


def create_dag(functions):
    """Create a directed acyclic graph (DAG) capturing dependencies between functions.

    Parameters
    ----------
    functions : dict
        Dictionary containing functions to build the DAG.

    Returns
    -------
    dag : networkx.DiGraph
        The DAG, represented as a dictionary of lists that maps function names to a list
        of its data dependencies.

    """
    dag = nx.DiGraph()
    for name, function in functions.items():
        dag.add_node(name, function=function)
        for dependency in inspect.getfullargspec(function).args:
            attr = (
                {"function": functions.get(dependency)}
                if dependency in functions
                else {}
            )
            dag.add_node(dependency, **attr)
            dag.add_edge(dependency, name)

    return dag


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
    all_ancestors = set(targets)
    for target in targets:
        all_ancestors = all_ancestors | set(nx.ancestors(dag, target))

    all_nodes = set(dag.nodes)

    redundant_nodes = all_nodes - all_ancestors

    dag.remove_nodes_from(redundant_nodes)

    return dag


def execute_dag(dag, data, targets, debug):
    """Naive serial scheduler for our tasks.

    We will probably use some existing scheduler instead. Interesting sources are:

    - https://ipython.org/ipython-doc/3/parallel/dag_dependencies.html
    - https://docs.dask.org/en/latest/graphs.html

    The main reason for writing an own implementation is to explore how difficult it
    would to avoid dask as a dependency.

    Parameters
    ----------
    dag : networkx.DiGraph
        The DAG.
    data : dict
    targets : list
    debug : bool
        Indicator for debug mode.

    Returns
    -------
    data : dict
        Dictionary of pd.Series with the resulting data.

    """
    # Needed for garbage collection.
    visited_nodes = set(data)
    skipped_nodes = set()

    for task in nx.topological_sort(dag):
        if task not in data and task not in skipped_nodes:
            if "function" in dag.nodes[task]:
                kwargs = _dict_subset(data, dag.predecessors(task))
                try:
                    data[task] = dag.nodes[task]["function"](**kwargs).rename(task)
                except Exception:
                    if debug:
                        traceback.print_exc()
                        skipped_nodes = skipped_nodes.union(nx.descendants(dag, task))

            else:
                dependants = list(dag.successors(task))
                raise KeyError(
                    f"Missing variable or function '{task}'. It is required to compute "
                    f"{dependants}."
                )

            visited_nodes.add(task)

            if targets and not debug:
                data = collect_garbage(data, task, visited_nodes, targets, dag)

    return data


def _dict_subset(dictionary, keys):
    return {k: dictionary[k] for k in keys}


def collect_garbage(results, task, visited_nodes, targets, dag):
    """Remove data which is no longer necessary.

    Loop over all dependencies of the current `task`. If a dependency is no longer
    needed, remove it.

    Parameters
    ----------
    results : dict
        Dictionary containing `pandas.Series` as values.
    task : str
        The name of the variable which was just computed.
    visited_nodes : set of str
        The set of nodes which have been visited before.
    dag : networkx.DiGraph
        The DAG.

    Returns
    -------
    results : dict
        Dictionary where some values might have been removed by the garbage collection.

    """
    for pre in dag.predecessors(task):
        is_obsolete = all(succ in visited_nodes for succ in dag.successors(pre))

        if is_obsolete and pre not in targets:
            del results[pre]

    return results
