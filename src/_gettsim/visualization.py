import functools
import inspect
import operator
from functools import reduce

import dags
import networkx as nx
import numpy
import pandas as pd
import plotly.graph_objects as go
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

from _gettsim.config import DEFAULT_TARGETS
from _gettsim.interface import (
    _round_and_partial_parameters_to_functions,
    build_targets_tree,
    set_up_dag,
)
from _gettsim.policy_environment import PolicyEnvironment
from _gettsim.policy_environment_postprocessor import (
    add_derived_functions_to_functions_tree,
)
from _gettsim.shared import (
    _filter_tree_by_name_list,
    format_list_linewise,
    get_names_of_arguments_without_defaults,
    tree_to_dict_with_qualified_name,
)


def plot_dag(
    environment: PolicyEnvironment,
    targets=None,
    columns_overriding_functions=None,
    check_minimal_specification="ignore",
    selectors=None,
    orientation="v",
    show_labels=None,
    hover_source_code=False,
):
    """Plot the dag of the tax and transfer system. Note that if 10 or less nodes are
    plotted, labels are always displayed.

    Parameters
    ----------
    environment:
        The policy environment.
    targets : str, list of str
        String or list of strings with names of functions whose output is actually
        needed by the user.
    columns_overriding_functions : str list of str
        Names of columns in the data which are preferred over function defined in the
        tax and transfer system.
    check_minimal_specification : {"ignore", "warn", "raise"}, default "ignore"
        Indicator for whether checks which ensure the most minimal configuration should
        be silenced, emitted as warnings or errors.
    selectors : str or list of str or dict or list of dict or list of str and dict
        Selectors allow to you to select and de-select nodes in the graph for
        visualization. For the full list of options, see the tutorial about
        `visualization <../docs/tutorials/visualize.ipynb>`_. By default, all nodes are
        shown.
    orientation :str,default "v"
         Whether the graph is horizontal or vertical
    show_labels : bool, default None
        Whether the graph is annotated with labels next to each node. By default,
        the labels are shown when the number of nodes is at most 10.
        Otherwise, names are displayed next to the node only when hovering over it.
        It is also possible to display labels regardless of the number of nodes, setting
        variable as True or hide labels when the variable is False.
    hover_source_code: bool, default as false
        Experimental feature which makes the source code of the functions accessible as
        a hover information. Sometimes, the tooltip is not properly displayed.

    """
    targets = build_targets_tree(DEFAULT_TARGETS if targets is None else targets)

    if isinstance(columns_overriding_functions, dict):
        names_of_columns_overriding_functions = tree_to_dict_with_qualified_name(
            columns_overriding_functions
        ).keys()
    elif isinstance(columns_overriding_functions, str):
        names_of_columns_overriding_functions = [columns_overriding_functions]
    elif columns_overriding_functions is None:
        names_of_columns_overriding_functions = []
    else:
        names_of_columns_overriding_functions = columns_overriding_functions

    # Load functions.
    all_functions = add_derived_functions_to_functions_tree(
        environment=environment,
        targets=targets,
        names_of_columns_in_data=names_of_columns_overriding_functions,
    )
    functions_not_overridden, _ = _filter_tree_by_name_list(
        tree=all_functions,
        qualified_names_list=names_of_columns_overriding_functions,
    )

    # Create parameter input structure.
    input_structure = dags.dag_tree.create_input_structure_tree(
        functions=functions_not_overridden,
        targets=None,  # None because no functions should be filtered out
    )

    # Select necessary nodes by creating a preliminary DAG.
    dag = set_up_dag(
        all_functions=functions_not_overridden,
        targets=targets,
        names_of_columns_overriding_functions=names_of_columns_overriding_functions,
        input_structure=input_structure,
        check_minimal_specification=check_minimal_specification,
    )

    _, necessary_functions = _filter_tree_by_name_list(
        functions_not_overridden, dag.nodes
    )
    processed_functions = _round_and_partial_parameters_to_functions(
        necessary_functions,
        environment.params,
        rounding=False,
    )

    input_structure = dags.dag_tree.create_input_structure_tree(
        functions=processed_functions,
        targets=None,
    )

    # Calculate results.
    dag = set_up_dag(
        all_functions=processed_functions,
        targets=targets,
        names_of_columns_overriding_functions=names_of_columns_overriding_functions,
        input_structure=input_structure,
        check_minimal_specification=check_minimal_specification,
    )

    selectors = [] if selectors is None else _to_list(selectors)
    dag = _select_nodes_in_dag(dag, selectors)
    dag = _add_url_to_dag(dag)
    # Even if we do not show the source codes , we need to remove the functions.
    dag = _replace_functions_with_source_code(dag)
    layout_df = _create_pygraphviz_layout(dag, orientation)
    # prepare for the nodes dataframe including their url
    names = layout_df.index
    node_x_coord = layout_df[0].values
    node_y_coord = layout_df[1].values
    url = numpy.array([dag.nodes[x]["url"] for x in names])
    codes = [dag.nodes[x]["source_code"] for x in names]

    combo = pd.DataFrame(
        {"x": node_x_coord, "y": node_y_coord, "url": url, "source_code": codes}
    )
    combo.source_code = combo.source_code.str.split("\n").str.join("<br>")

    # prepare for the edges dataframe
    df = pd.DataFrame(list(dag.edges))
    if len(df) == 0:
        df["x0"] = 0
        df["y0"] = 0
    else:
        df["x0"] = df[0].map(layout_df[0])
        df["y0"] = df[0].map(layout_df[1])
        df["x1"] = df[1].map(layout_df[0])
        df["y1"] = df[1].map(layout_df[1])
    df["None"] = ""
    if len(df) == 0:
        edge_x = []
        edge_y = []
    else:
        edge_x = df[["x0", "x1", "None"]].apply(tuple, axis=1).tolist()
        edge_x = list(reduce(operator.concat, edge_x))
        edge_y = df[["y0", "y1", "None"]].apply(tuple, axis=1).tolist()
        edge_y = list(reduce(operator.concat, edge_y))
    arrows = [
        go.layout.Annotation(
            x=df["x1"][i],
            y=df["y1"][i],
            xref="x",
            yref="y",
            text="",
            showarrow=True,
            axref="x",
            ayref="y",
            ax=df["x0"][i],
            ay=df["y0"][i],
            arrowhead=2,
            arrowsize=2,
            startstandoff=5,
            standoff=5,
            arrowcolor="gray",
        )
        for i in range(len(df))
    ]

    # plot the nodes, edges and arrows together
    fig = go.FigureWidget(
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            annotations=arrows,
            hoverlabel_font_size=10,
            margin={"b": 20, "l": 5, "r": 5, "t": 40},
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        )
    )
    fig.add_scatter(
        x=edge_x,
        y=edge_y,
        line={"width": 0.5, "color": "blue"},
        hoverinfo="none",
        mode="lines",
        showlegend=False,
    )
    # choose the different options for plotting
    # When show_lebels = None and number of nodes >10
    # labels are shown when hovering over it.
    # Same happens when show_labels is False,
    # Otherwise, labels are displayed next to the nodes.
    if show_labels or (show_labels is None and len(names) <= 10):
        mode = "markers+text"
        hover_info = "skip"
    else:
        mode = "markers"
        hover_info = "text"

    fig.add_scatter(
        x=combo.x,
        y=combo.y,
        mode=mode,
        hoverinfo=hover_info,
        textposition="bottom center",
        text=list(names),
        showlegend=False,
        marker={
            "showscale": False,
            "reversescale": True,
            "color": "red",
            "size": 15,
        },
    )

    # add the source code to the graph,
    # that is displayed as hover information

    if hover_source_code:
        for i in range(len(combo)):
            fig.add_scatter(
                x=[combo.x[i]],
                y=[combo.y[i]],
                mode=mode,
                hovertext=combo.source_code[i],
                hoverinfo="text",
                textposition="bottom center",
                hoverlabel={"bgcolor": "lightgrey", "font": {"color": "black"}},
                text=names[i],
                showlegend=False,
                name=names[i],
                marker={
                    "showscale": False,
                    "reversescale": True,
                    "color": "red",
                    "size": 15,
                },
            )

    elif not hover_source_code:
        fig.add_scatter(
            x=combo.x,
            y=combo.y,
            mode=mode,
            hoverinfo="skip",
            textposition="bottom center",
            text=list(names),
            showlegend=False,
            marker={
                "showscale": False,
                "reversescale": True,
                "color": "red",
                "size": 15,
            },
        )
    else:
        raise ValueError(
            "hover_source_code must be either True"
            f" or False, but got {hover_source_code!r}"
        )

    return fig


def _mock_parameters_arguments(functions):
    """Mock the parameter arguments.

    Functions have parameter arguments which should not be visible while plotting the
    DAG. Thus, partial empty dictionaries to the functions.

    """
    mocked_functions = {}
    for name, function in functions.items():
        partial_params = {
            i: {}
            for i in get_names_of_arguments_without_defaults(function)
            if i.endswith("_params")
        }

        # Fix old functions which requested the whole dictionary. Test if removable.
        if "params" in get_names_of_arguments_without_defaults(function):
            partial_params["params"] = {}

        mocked_functions[name] = (
            functools.partial(function, **partial_params)
            if partial_params
            else function
        )

    return mocked_functions


def _select_nodes_in_dag(dag, raw_selectors):
    """Select nodes in the DAG based on the selectors."""
    raw_selectors = _convert_non_dict_selectors(raw_selectors)
    selectors, deselectors = _separate_selectors_and_deselectors(raw_selectors)
    dag = _apply_selectors_and_deselectors(dag, selectors, deselectors)

    if len(dag.nodes) == 0:
        raise ValueError("After selection and de-selection, the DAG contains no nodes.")

    return dag


def _add_url_to_dag(dag):
    for node in dag.nodes:
        # Retrieve the name from the function because some functions are defined for
        # time periods and the node name will point to a non-existent function, but the
        # function name is a valid target. E.g., wohngeld_eink_freib_m and
        # wohngeld_eink_freib_m_bis_2015.
        if "function" in dag.nodes[node]:
            # Fix for partialed functions.
            try:
                name = dag.nodes[node]["function"].__name__
            except AttributeError:
                name = dag.nodes[node]["function"].func.__name__
        else:
            name = node
        dag.nodes[node]["url"] = _create_url(name)

    return dag


def _create_url(func_name):
    return (
        f"https://gettsim.readthedocs.io/en/latest/gettsim_objects"
        f"/functions.html#gettsim.functions.{func_name}"
    )


def _replace_functions_with_source_code(dag):
    """Replace functions in the DAG with their source code.

    Parameters
    ----------
    dag : networkx.DiGraph
        The graph whose nodes can contain Python functions in the node attributes.

    Returns
    -------
    dag : nx.DiGraph
        The graph whose nodes can contain a string of the source code of Python
        function.

    """
    for node in dag.nodes:
        if "function" in dag.nodes[node]:
            function = dag.nodes[node].pop("function")
            if isinstance(function, functools.partial):
                source = inspect.getsource(function.func)
            else:
                source = inspect.getsource(function)
            dag.nodes[node]["source_code_highlighted"] = _highlight_source_code(source)
            dag.nodes[node]["source_code"] = source
        else:
            dag.nodes[node]["source_code"] = "Column in data"

    return dag


def _highlight_source_code(source):
    """Highlight the source code of functions.

    Parameters
    ----------
    source : str
        Source code of the function.

    Returns
    -------
    highlighted_source : str
        The source code of the function in HTML format and highlighted.

    """
    lex = lexers.get_lexer_by_name("python")
    formatter = HtmlFormatter(full=True)
    return highlight(source, lex, formatter)


def _create_pygraphviz_layout(dag, orientation):
    # Convert node labels to integers because some names cannot be handled by pydot.
    dag_w_integer_nodes = nx.relabel.convert_node_labels_to_integers(dag)

    # Remove all node attributes from the graph, because they cannot be serialized to
    # JSON.
    for node in dag_w_integer_nodes.nodes:
        for attr in list(dag_w_integer_nodes.nodes[node]):
            dag_w_integer_nodes.nodes[node].pop(attr)

    # Create the integer layout.
    integer_layout = nx.nx_agraph.pygraphviz_layout(dag_w_integer_nodes, prog="dot")

    # Remap layout from integers to labels.
    integer_to_labels = dict(zip(dag_w_integer_nodes.nodes, dag.nodes))
    layout = {
        integer_to_labels[i]: numpy.array(integer_layout[i]) for i in integer_to_labels
    }

    # Convert nonnegative integer coordinates from the layout to unit cube.
    min_x = min(i[0] for i in layout.values())
    min_y = min(i[1] for i in layout.values())
    min_ = numpy.array([min_x, min_y])

    max_x = max(i[0] for i in layout.values())
    max_y = max(i[1] for i in layout.values())
    max_ = numpy.array([max_x, max_y])

    for k, v in layout.items():
        layout[k] = (v - (max_ + min_) / 2) / ((max_ - min_) / 2).clip(1)

    if orientation == "v":
        layout_df = numpy.transpose(pd.DataFrame.from_dict(layout))

    elif orientation == "h":
        layout_df = numpy.transpose(pd.DataFrame.from_dict(layout))
        layout_df[[0, 1]] = layout_df[[1, 0]]
        layout_df[0] = layout_df[0] * (-1)

    else:
        raise ValueError(
            f"orientation must be one of 'v', 'h', but got {orientation!r}"
        )

    return layout_df


def _to_list(scalar_or_iter):
    """Convert scalars and iterables to list.

    Parameters
    ----------
    scalar_or_iter : str or list

    Returns
    -------
    list

    Examples
    --------
    >>> _to_list("a")
    ['a']
    >>> _to_list(["b"])
    ['b']

    """
    return (
        [scalar_or_iter]
        if isinstance(scalar_or_iter, str | dict)
        else list(scalar_or_iter)
    )


def _convert_non_dict_selectors(selectors_):
    selectors = [i for i in selectors_ if isinstance(i, dict)]
    str_selectors = [i for i in selectors_ if not isinstance(i, dict)]

    if str_selectors:
        selector = {"node": str_selectors, "type": "nodes", "select": True}
        selectors += [selector]

    return selectors


def _separate_selectors_and_deselectors(selectors_):
    selectors = []
    deselectors = []
    for selector in selectors_:
        if selector.get("select", True):
            selectors.append(selector)
        else:
            deselectors.append(selector)

    return selectors, deselectors


def _apply_selectors_and_deselectors(dag, selectors, deselectors):
    if selectors:
        selected_nodes = set().union(
            *[_get_selected_nodes(dag, selector) for selector in selectors]
        )
    else:
        selected_nodes = set(dag.nodes)

    selected_nodes_not_in_dag = selected_nodes - set(dag.nodes)
    if selected_nodes_not_in_dag:
        raise ValueError(
            "The following selected nodes are not in the DAG:"
            f"\n{format_list_linewise(selected_nodes_not_in_dag)}"
        )

    deselected_nodes = set().union(
        *[_get_selected_nodes(dag, deselector) for deselector in deselectors]
    )
    deselected_nodes_not_in_dag = deselected_nodes - set(dag.nodes)
    if deselected_nodes_not_in_dag:
        raise ValueError(
            "The following de-selected nodes are not in the DAG:"
            f"\n{format_list_linewise(deselected_nodes_not_in_dag)}"
        )

    nodes_to_be_removed = set(dag.nodes) - set(selected_nodes) | set(deselected_nodes)

    dag.remove_nodes_from(nodes_to_be_removed)

    return dag


def _get_selected_nodes(dag, selector):
    if selector["type"] == "nodes":
        selected_nodes = _to_list(selector["node"])
    elif selector["type"] == "ancestors":
        selected_nodes = _node_and_ancestors(
            dag, selector["node"], selector.get("order", None)
        )
    elif selector["type"] == "descendants":
        selected_nodes = _node_and_descendants(
            dag, selector["node"], selector.get("order", None)
        )
    elif selector["type"] in ["neighbors", "neighbours"]:
        selected_nodes = list(
            _kth_order_neighbors(dag, selector["node"], selector.get("order", 1))
        )
    else:
        raise NotImplementedError(
            f"Selector type {selector['type']!r} is not defined. "
            "Allowed are only 'nodes', 'ancestors', 'descendants', or 'neighbors'."
        )

    return set(selected_nodes)


def _node_and_ancestors(dag, node, order):
    ancestors = list(nx.ancestors(dag, node))
    if order:
        ancestors = list(_kth_order_predecessors(dag, node, order=order))
    return [node, *ancestors]


def _node_and_descendants(dag, node, order):
    descendants = list(nx.descendants(dag, node))
    if order:
        descendants = list(_kth_order_successors(dag, node, order=order))
    return [node, *descendants]


def _kth_order_neighbors(dag, node, order):
    yield node

    if order >= 1:
        for predecessor in dag.predecessors(node):
            yield from _kth_order_predecessors(dag, predecessor, order=order - 1)

        for successor in dag.successors(node):
            yield from _kth_order_successors(dag, successor, order=order - 1)


def _kth_order_predecessors(dag, node, order):
    yield node

    if order >= 1:
        for predecessor in dag.predecessors(node):
            yield from _kth_order_predecessors(dag, predecessor, order=order - 1)


def _kth_order_successors(dag, node, order):
    yield node

    if order >= 1:
        for successor in dag.successors(node):
            yield from _kth_order_successors(dag, successor, order=order - 1)
