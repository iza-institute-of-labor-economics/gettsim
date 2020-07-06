import traceback
import warnings

import networkx as nx

from gettsim.config import DEFAULT_TARGETS
from gettsim.shared import format_list_linewise
from gettsim.shared import get_names_of_arguments_without_defaults


def create_dag(
    functions,
    targets=None,
    columns_overriding_functions=None,
    check_minimal_specification="ignore",
):
    """Create the DAG for the defined tax and transfer system.

    Parameters
    ----------
    functions : str, pathlib.Path, callable, module, imports statements, dict
        Functions can be anything of the specified types and a list of the same objects.
        If the object is a dictionary, the keys of the dictionary are used as a name
        instead of the function name. For all other objects, the name is inferred from
        the function name.
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

    Returns
    -------
    dag : networkx.DiGraph
        The DAG of the tax and transfer system.

    """
    targets = DEFAULT_TARGETS if targets is None else targets
    if check_minimal_specification not in ["ignore", "warn", "raise"]:
        raise ValueError(
            "'check_minimal_specification' must be one of ['ignore', 'warn', 'raise']."
        )

    dag = _create_complete_dag(functions)

    if targets:
        dag = _limit_dag_to_targets_and_their_ancestors(dag, targets)

    _fail_if_columns_overriding_functions_are_not_in_dag(
        dag, columns_overriding_functions, check_minimal_specification
    )

    dag = _remove_unused_ancestors_of_columns_overriding_functions(
        dag, columns_overriding_functions
    )

    return dag


def _create_complete_dag(functions):
    """Create the complete DAG.

    This DAG is constructed from all functions and not pruned by specified root nodes or
    targets.

    Parameters
    ----------
    functions : dict of callable
        Dictionary containing functions to build the DAG.

    Returns
    -------
    dag : networkx.DiGraph
        The complete DAG of the tax and transfer system.

    """
    # Construct DAG from dictionary.
    functions_arguments_dict = {
        name: get_names_of_arguments_without_defaults(function)
        for name, function in functions.items()
    }
    dag = nx.DiGraph(functions_arguments_dict).reverse()

    # Save functions in DAG.
    for name, function in functions.items():
        dag.nodes[name]["function"] = function

    return dag


def _fail_if_targets_not_in_functions(functions, targets):
    """Fail if targets are not in functions.

    Parameters
    ----------
    functions : dict of callable
        Dictionary containing functions to build the DAG.
    targets : list of str
        The targets which should be computed. They limit the DAG in the way that only
        ancestors of these nodes need to be considered.

    Raises
    ------
    ValueError
        Raised if ``targets`` are not in functions.

    """
    targets_not_in_functions = set(targets) - set(functions)
    if targets_not_in_functions:
        formatted = format_list_linewise(targets_not_in_functions)
        raise ValueError(
            f"The following targets have no corresponding function:\n{formatted}"
        )


def _limit_dag_to_targets_and_their_ancestors(dag, targets):
    """Limit DAG to targets and their ancestors.

    Parameters
    ----------
    dag : networkx.DiGraph
        The complete DAG.
    targets : list of str
        Variables which should be computed.

    Returns
    -------
    dag : networkx.DiGraph
        Pruned DAG.

    """
    used_nodes = set(targets)
    for target in targets:
        used_nodes = used_nodes | set(nx.ancestors(dag, target))

    all_nodes = set(dag.nodes)

    unused_nodes = all_nodes - used_nodes

    dag.remove_nodes_from(unused_nodes)

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


def _remove_unused_ancestors_of_columns_overriding_functions(
    dag, columns_overriding_functions
):
    """Remove unused ancestors of ``columns_overriding_functions``.

    If a node is not computed because it is provided by the data, ancestors of the node
    can become irrelevant. Thus, remove predecessors which are only used to compute
    variables found in data.

    Parameters
    ----------
    dag : networkx.DiGraph
        The DAG which is limited to targets and their ancestors.
    columns_overriding_functions : list of str
        The nodes which are provided by columns in the data and do not need to be
        computed. These columns limit the depth of the DAG.

    Returns
    -------
    dag : networkx.DiGraph
        A DAG which contains only nodes which need to be computed.

    """
    unused_nodes = set()
    for name in columns_overriding_functions:
        # This if-clause is necessary as long as there are nodes from
        # ``columns_overriding_functions`` which are unused. Corresponds to
        # ``_fail_if_columns_overriding_functions_are_not_in_dag``.
        if name in dag.nodes:
            _find_unused_ancestors(
                dag, name, set(columns_overriding_functions), unused_nodes
            )

    dag.remove_nodes_from(unused_nodes)

    return dag


def _find_unused_ancestors(dag, name, columns_overriding_functions, unused_nodes):
    """Find unused ancestors which are nodes which solely produce unused columns.

    Note that this function changes ``unused_columns`` in-place.

    """
    for predecessor in dag.predecessors(name):
        if all(
            successor in unused_nodes | columns_overriding_functions
            for successor in dag.successors(predecessor)
        ):
            unused_nodes.add(predecessor)
            _find_unused_ancestors(
                dag, predecessor, columns_overriding_functions, unused_nodes
            )


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
                except Exception as e:
                    if debug:
                        traceback.print_exc()
                        skipped_nodes = skipped_nodes.union(nx.descendants(dag, task))
                    else:
                        raise e

            else:
                successors = list(dag.successors(task))
                raise KeyError(
                    f"Missing variable or function '{task}'. It is required to compute "
                    f"{successors}."
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
