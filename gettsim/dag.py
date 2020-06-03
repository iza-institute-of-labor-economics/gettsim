import functools
import inspect

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
    dag = nx.DiGraph()
    for name, function in func_dict.items():
        dag.add_node(name, function=function)
        for dependency in inspect.getfullargspec(function).args:
            attr = (
                {"function": func_dict.get(dependency)}
                if dependency in func_dict
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


def execute_dag(dag, data, targets):
    """Naive serial scheduler for our tasks.

    We will probably use some existing scheduler instead. Interesting sources are:
    - https://ipython.org/ipython-doc/3/parallel/dag_dependencies.html
    - https://docs.dask.org/en/latest/graphs.html

    The main reason for writing an own implementation is to explore how difficult it
    would to avoid dask as a dependency.

    Parameters
    ----------
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
            if "function" in dag.nodes[task]:
                kwargs = _dict_subset(data, dag.predecessors(task))
                data[task] = dag.nodes[task]["function"](**kwargs).rename(task)
            else:
                dependants = list(dag.successors(task))
                raise KeyError(
                    f"Missing variable or function '{task}'. It is required to compute "
                    f"{dependants}."
                )

            visited_nodes.add(task)

            if targets:
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
