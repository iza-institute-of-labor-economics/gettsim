import functools
import inspect

import networkx as nx
import numpy as np
import pandas as pd
from bokeh.io import output_notebook
from bokeh.io import show
from bokeh.models import Arrow
from bokeh.models import BoxZoomTool
from bokeh.models import Circle
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models import LabelSet
from bokeh.models import NormalHead
from bokeh.models import OpenURL
from bokeh.models import Plot
from bokeh.models import Range1d
from bokeh.models import ResetTool
from bokeh.models import TapTool
from bokeh.models import Title
from bokeh.plotting import from_networkx
from pygments import highlight
from pygments import lexers
from pygments.formatters import HtmlFormatter

import gettsim
from gettsim.config import DEFAULT_TARGETS
from gettsim.dag import _fail_if_targets_not_in_functions
from gettsim.dag import create_dag
from gettsim.functions_loader import load_user_and_internal_functions
from gettsim.shared import format_list_linewise
from gettsim.shared import get_names_of_arguments_without_defaults
from gettsim.shared import parse_to_list_of_strings


ARROW_KWARGS_DEFAULTS = {"size": 7, "fill_color": "red"}
EDGE_KWARGS_DEFAULTS = {"line_color": "red", "line_width": 1}
NODE_KWARGS_DEFAULTS = {"size": 15, "fill_color": "blue"}
PLOT_KWARGS_DEFAULTS = {
    "plot_width": 600,
    "plot_height": 600,
    "x_range": Range1d(-1.3, 1.3),
    "y_range": Range1d(-1.3, 1.3),
}
LABEL_KWARGS_DEFAULT = {
    "x_offset": -30,
    "y_offset": 8,
    "render_mode": "canvas",
    "text_font_size": "12px",
}


TOOLTIPS = """
column: @index <br>
source code: @source_code{safe}
"""


def plot_dag(
    functions,
    targets=None,
    columns_overriding_functions=None,
    check_minimal_specification="ignore",
    selectors=None,
    labels=True,
    tooltips=False,
    plot_kwargs=None,
    arrow_kwargs=None,
    edge_kwargs=None,
    label_kwargs=None,
    node_kwargs=None,
):
    """Plot the dag of the tax and transfer system.

    Parameters
    ----------
    functions : str, pathlib.Path, callable, module, imports statements, dict
        Functions can be anything of the specified types and a list of the same objects.
        If the object is a dictionary, the keys of the dictionary are used as a name
        instead of the function name. For all other objects, the name is inferred from
        the function name.
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
    labels : bool, default True
        Annotate nodes with labels.
    tooltips : bool, default False
        Experimental feature which makes the source code of the functions accessible as
        a tooltip. Sometimes, the tooltip is not properly displayed.
    plot_kwargs : dict
        Additional keyword arguments passed to :class:`bokeh.models.Plot`.
    arrow_kwargs : dict
        Additional keyword arguments passed to :class:`bokeh.models.Arrow`. For example,
        change the size of the head with ``{"size": 10}``.
    edge_kwargs : dict
        Additional keyword arguments passed to :class:`bokeh.models.MultiLine`. For
        example, change the color with ``{"fill_color": "green"}``.
    label_kwargs : dict
        Additional keyword arguments passed to :class:`bokeh.models.LabelSet`. For
        example, change the fontsize with ``{"text_font_size": "12px"}``.
    node_kwargs : dict
        Additional keyword arguments passed to :class:`bokeh.models.Circle`. For
        example, change the color with ``{"fill_color": "orange"}``.

    """
    targets = DEFAULT_TARGETS if targets is None else targets
    targets = parse_to_list_of_strings(targets, "targets")
    columns_overriding_functions = parse_to_list_of_strings(
        columns_overriding_functions, "columns_overriding_functions"
    )

    # Load functions and perform checks.
    functions, internal_functions = load_user_and_internal_functions(functions)

    # Create one dictionary of functions and perform check.
    functions = {**internal_functions, **functions}
    functions = {
        k: v for k, v in functions.items() if k not in columns_overriding_functions
    }
    _fail_if_targets_not_in_functions(functions, targets)

    # Partial parameters to functions such that they disappear in the DAG.
    functions = _mock_parameters_arguments(functions)

    dag = create_dag(
        functions, targets, columns_overriding_functions, check_minimal_specification
    )

    selectors = [] if selectors is None else _to_list(selectors)
    plot_kwargs = {} if plot_kwargs is None else plot_kwargs
    arrow_kwargs = {} if arrow_kwargs is None else arrow_kwargs
    edge_kwargs = {} if edge_kwargs is None else edge_kwargs
    label_kwargs = {} if label_kwargs is None else label_kwargs
    node_kwargs = {} if node_kwargs is None else node_kwargs

    dag = _select_nodes_in_dag(dag, selectors)

    dag = _add_url_to_dag(dag)
    # Even if we do not use the source codes as tooltips, we need to remove the
    # functions.
    dag = _replace_functions_with_source_code(dag)

    plot_kwargs["title"] = _to_bokeh_title(
        plot_kwargs.get("title", "Tax and Transfer System")
    )
    plot = Plot(**{**PLOT_KWARGS_DEFAULTS, **plot_kwargs})

    layout = _create_pydot_layout(dag)
    graph_renderer = from_networkx(dag, layout, scale=1, center=(0, 0))

    graph_renderer.node_renderer.glyph = Circle(
        **{**NODE_KWARGS_DEFAULTS, **node_kwargs}
    )

    graph_renderer.edge_renderer.visible = False
    for (
        _,
        (start_node, end_node),
    ) in graph_renderer.edge_renderer.data_source.to_df().iterrows():
        (x_start, y_start), (x_end, y_end) = _compute_arrow_coordinates(
            layout[start_node], layout[end_node]
        )
        plot.add_layout(
            Arrow(
                end=NormalHead(**{**ARROW_KWARGS_DEFAULTS, **arrow_kwargs}),
                x_start=x_start,
                y_start=y_start,
                x_end=x_end,
                y_end=y_end,
                **{**EDGE_KWARGS_DEFAULTS, **edge_kwargs},
            )
        )

    plot.renderers.append(graph_renderer)

    tools = [BoxZoomTool(), ResetTool()]
    tools.append(TapTool(callback=OpenURL(url="@url")))
    if tooltips:
        tools.append(HoverTool(tooltips=TOOLTIPS))

    plot.add_tools(*tools)

    if labels:
        source = ColumnDataSource(
            pd.DataFrame(layout).T.rename(columns={0: "x", 1: "y"})
        )
        labels = LabelSet(
            x="x",
            y="y",
            text="index",
            source=source,
            **{**LABEL_KWARGS_DEFAULT, **label_kwargs},
        )
        plot.add_layout(labels)

    output_notebook()
    show(plot)

    return plot


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


def _to_bokeh_title(title):
    t = Title()
    t.text = title
    return t


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
        # function name is a valid target. E.g., wohngeld_eink_abzüge and
        # wohngeld_eink_abzüge_bis_2015.
        if "function" in dag.nodes[node]:
            # Fix for partialed functions.
            try:
                name = dag.nodes[node]["function"].__name__
            except AttributeError:
                name = name = dag.nodes[node]["function"].func.__name__
        else:
            name = node
        dag.nodes[node]["url"] = _create_url(name)

    return dag


def _create_url(func_name):
    return (
        f"https://gettsim.readthedocs.io/en/v{gettsim.__version__}/gettsim_objects"
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
            dag.nodes[node]["source_code"] = _highlight_source_code(source)
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


def _create_pydot_layout(dag):
    """Create a layout for the graph with pydot.

    The function :func:`networkx.drawing.nx_pydot.pydot_layout` has some shortcoming
    which are resolved here.

    - Cannot handle underscores in node labels and longer labels.
    - Cannot handle node attributes which cannot be serialized with JSON.
    - Produces coordinates which are not inside the unit cube.

    Parameters
    ----------
    dag : networkx.DiGraph
        The DAG for which to produce the layout

    Returns
    -------
    layout : dict of arrays
        A dictionary node labels as keys and xy coordinates as values in an array.

    """
    # Convert node labels to integers because some names cannot be handled by pydot.
    dag_w_integer_nodes = nx.relabel.convert_node_labels_to_integers(dag)

    # Remove all node attributes from the graph, because they cannot be serialized to
    # JSON.
    for node in dag_w_integer_nodes.nodes:
        for attr in list(dag_w_integer_nodes.nodes[node]):
            dag_w_integer_nodes.nodes[node].pop(attr)

    # Create the integer layout.
    integer_layout = nx.drawing.nx_pydot.pydot_layout(dag_w_integer_nodes, prog="dot")

    # Remap layout from integers to labels.
    integer_to_labels = dict(zip(dag_w_integer_nodes.nodes, dag.nodes))
    layout = {
        integer_to_labels[i]: np.array(integer_layout[i]) for i in integer_to_labels
    }

    # Convert nonnegative integer coordinates from the layout to unit cube.
    min_x = min(i[0] for i in layout.values())
    min_y = min(i[1] for i in layout.values())
    min_ = np.array([min_x, min_y])

    max_x = max(i[0] for i in layout.values())
    max_y = max(i[1] for i in layout.values())
    max_ = np.array([max_x, max_y])

    for k, v in layout.items():
        layout[k] = (v - (max_ + min_) / 2) / ((max_ - min_) / 2).clip(1)

    return layout


def _compute_arrow_coordinates(start, end, scalar=0.05):
    """Compute arrow coordinates.

    This function computes the coordinates of the tail and the head of the arrow. The
    scalar compresses the arrow such that its tail and head do not overlap with the
    nodes.

    """
    unit_vector = (end - start) / np.sum(np.abs(end - start))
    return start + unit_vector * scalar, end - unit_vector * scalar


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
        if isinstance(scalar_or_iter, str) or isinstance(scalar_or_iter, dict)
        else list(scalar_or_iter)
    )


def _validate_selectors(selectors):
    for selector in selectors:
        if not isinstance(selector, str) or not (
            isinstance(selector, dict) and "node" in selector and "type" in selector
        ):
            raise ValueError("A selector has to be a str or a dictionary.")

        if selector["type"] in ["neighbors", "neighbours"]:
            if selector["order"] < 1:
                raise ValueError("The order of neighbors cannot be smaller than one.")


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
        selected_nodes = _node_and_ancestors(dag, selector["node"])
    elif selector["type"] == "descendants":
        selected_nodes = _node_and_descendants(dag, selector["node"])
    elif selector["type"] in ["neighbors", "neighbours"]:
        selected_nodes = list(
            _kth_order_neighbors(dag, selector["node"], selector.get("order", 1))
        )
    else:
        raise NotImplementedError(f"Selector type '{selector['type']}' is not defined.")

    return set(selected_nodes)


def _node_and_ancestors(dag, node):
    return [node] + list(nx.ancestors(dag, node))


def _node_and_descendants(dag, node):
    return [node] + list(nx.descendants(dag, node))


def _kth_order_neighbors(dag, node, order):
    yield node

    if 1 <= order:
        for predecessor in dag.predecessors(node):
            yield from _kth_order_predecessors(dag, predecessor, order=order - 1)

        for successor in dag.successors(node):
            yield from _kth_order_successors(dag, successor, order=order - 1)


def _kth_order_predecessors(dag, node, order):
    yield node

    if 1 <= order:
        for predecessor in dag.predecessors(node):
            yield from _kth_order_predecessors(dag, predecessor, order=order - 1)


def _kth_order_successors(dag, node, order):
    yield node

    if 1 <= order:
        for successor in dag.successors(node):
            yield from _kth_order_successors(dag, successor, order=order - 1)
