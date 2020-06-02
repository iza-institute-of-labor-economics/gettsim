import copy
import functools
import inspect

import networkx as nx
import numpy as np
from bokeh.io import output_notebook
from bokeh.io import show
from bokeh.models import BoxZoomTool
from bokeh.models import Circle
from bokeh.models import HoverTool
from bokeh.models import MultiLine
from bokeh.models import Plot
from bokeh.models import Range1d
from bokeh.models import ResetTool
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx
from pygments import highlight
from pygments import lexers
from pygments.formatters import HtmlFormatter


EDGE_KWARGS_DEFAULTS = {"line_color": Spectral4[3], "line_alpha": 0.8, "line_width": 1}
NODE_KWARGS_DEFAULTS = {"size": 15, "fill_color": Spectral4[0]}
PLOT_KWARGS_DEFAULTS = {
    "plot_width": 800,
    "plot_height": 800,
    "x_range": Range1d(-1.1, 1.1),
    "y_range": Range1d(-1.1, 1.1),
}


TOOLTIPS = """
column: @index <br>
source code: @source_code{safe}
"""


def plot_dag(dag, plot_kwargs=None, node_kwargs=None, edge_kwargs=None):
    dag = copy.deepcopy(dag)

    plot_kwargs = {} if plot_kwargs is None else plot_kwargs
    node_kwargs = {} if node_kwargs is None else node_kwargs
    edge_kwargs = {} if edge_kwargs is None else edge_kwargs

    dag = _replace_functions_with_source_code(dag)

    plot = Plot(**{**PLOT_KWARGS_DEFAULTS, **plot_kwargs})

    plot.title.text = "Tax and Transfer System - 2018 - Target: sum_brutto_eink"

    node_hover_tool = HoverTool(tooltips=TOOLTIPS)

    plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

    graph_renderer = from_networkx(dag, _create_pydot_layout(dag))

    graph_renderer.node_renderer.glyph = Circle(
        **{**NODE_KWARGS_DEFAULTS, **node_kwargs}
    )
    graph_renderer.edge_renderer.glyph = MultiLine(
        **{**EDGE_KWARGS_DEFAULTS, **edge_kwargs}
    )

    plot.renderers.append(graph_renderer)

    output_notebook()
    show(plot)

    return plot


def _replace_functions_with_source_code(dag):
    """Replace functions in the DAG with their source code.

    Parameters
    ----------
    dag : nx.DiGraph
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
    max_x = max(i[0] for i in layout.values())
    max_y = max(i[1] for i in layout.values())

    for k, v in layout.items():
        layout[k] = v / (max_x, max_y) * 2 - 1

    return layout
