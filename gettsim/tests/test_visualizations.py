import networkx as nx
import pytest

from gettsim.visualization import _get_selected_nodes
from gettsim.visualization import _kth_order_neighbors
from gettsim.visualization import _node_and_ancestors
from gettsim.visualization import _node_and_descendants
from gettsim.visualization import _select_nodes_in_dag
from gettsim.visualization import plot_dag


@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, 1, {2, 3, 4}), (5, 1, 2, {0, 1, 2, 3})],
)
def test_kth_order_neighbors(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_kth_order_neighbors(dag, node, order))
    assert nodes == expected


@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, None, {0, 1, 2, 3}), (5, 1, None, {0, 1})],
)
def test_node_and_ancestors(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_node_and_ancestors(dag, node, order))
    assert nodes == expected


@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, 1, {2, 3}), (5, 1, 2, {0, 1})],
)
def test_node_and_ancestors_order(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_node_and_ancestors(dag, node, order))
    assert nodes == expected


@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, None, {3, 4, 5}), (5, 1, None, {1, 2, 3, 4, 5})],
)
def test_node_and_descendants(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_node_and_descendants(dag, node, order))
    assert nodes == expected


@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, 1, {3, 4}), (5, 1, 2, {1, 2, 3})],
)
def test_node_and_descendants_order(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_node_and_descendants(dag, node, order))
    assert nodes == expected


@pytest.mark.parametrize(
    "n_nodes, selector, expected",
    [
        (5, {"node": 1, "type": "ancestors"}, {0, 1}),
        (5, {"node": 2, "type": "descendants"}, {2, 3, 4, 5}),
        (5, {"node": 1, "type": "ancestors", "order": 2}, {0, 1}),
        (5, {"node": 2, "type": "descendants", "order": 2}, {2, 3, 4}),
        (5, {"node": 3, "type": "neighbors", "order": 1}, {2, 3, 4}),
        (5, {"node": 3, "type": "neighbours", "order": 2}, {1, 2, 3, 4, 5}),
        (5, {"node": [5, 1, 2], "type": "nodes"}, {1, 2, 5}),
    ],
)
def test_get_selected_nodes(n_nodes, selector, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_get_selected_nodes(dag, selector))
    assert nodes == expected


@pytest.mark.parametrize(
    "n_nodes, selectors, expected",
    [
        (5, [{"node": [1, 2], "type": "nodes"}], {1, 2}),
        (
            5,
            [{"node": [0], "type": "nodes"}, {"node": 3, "type": "descendants"}],
            {0, 3, 4, 5},
        ),
        (
            5,
            [
                {"node": [0], "type": "nodes"},
                {"node": 3, "type": "descendants"},
                {"node": [4], "type": "nodes", "select": False},
            ],
            {0, 3, 5},
        ),
    ],
)
def test_select_nodes_in_dag(n_nodes, selectors, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    dag = _select_nodes_in_dag(dag, selectors)
    assert set(dag.nodes) == expected


def test_plot_dag():
    """Make sure that minimal example doesn't produce an error"""
    plot_dag(functions=[], targets=["erwachsene_alle_rentner_hh"])
