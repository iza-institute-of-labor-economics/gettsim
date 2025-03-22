import networkx as nx
import pytest

from _gettsim.policy_environment import PolicyEnvironment
from _gettsim.visualization import (
    _get_selected_nodes,
    _kth_order_neighbors,
    _node_and_ancestors,
    _node_and_descendants,
    _select_nodes_in_dag,
    plot_dag,
)
from _gettsim_tests._helpers import cached_set_up_policy_environment

environment = cached_set_up_policy_environment(date=2020)


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, 1, {2, 3, 4}), (5, 1, 2, {0, 1, 2, 3})],
)
def test_kth_order_neighbors(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_kth_order_neighbors(dag, node, order))
    assert nodes == expected


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, None, {0, 1, 2, 3}), (5, 1, None, {0, 1})],
)
def test_node_and_ancestors(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_node_and_ancestors(dag, node, order))
    assert nodes == expected


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, 1, {2, 3}), (5, 1, 2, {0, 1})],
)
def test_node_and_ancestors_order(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_node_and_ancestors(dag, node, order))
    assert nodes == expected


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, None, {3, 4, 5}), (5, 1, None, {1, 2, 3, 4, 5})],
)
def test_node_and_descendants(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_node_and_descendants(dag, node, order))
    assert nodes == expected


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
@pytest.mark.parametrize(
    "n_nodes, node, order, expected",
    [(5, 3, 1, {3, 4}), (5, 1, 2, {1, 2, 3})],
)
def test_node_and_descendants_order(n_nodes, node, order, expected):
    dag = nx.DiGraph([(i, i + 1) for i in range(n_nodes)])
    nodes = set(_node_and_descendants(dag, node, order))
    assert nodes == expected


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
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


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
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


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
def test_plot_dag():
    """Make sure that minimal example doesn't produce an error."""
    plot_dag(
        environment=environment,
        targets=["demographics__erwachsene_alle_rentner_hh"],
    )


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
def test_should_fail_if_target_is_missing():
    with pytest.raises(
        ValueError, match="The following targets have no corresponding function"
    ):
        plot_dag(
            environment=PolicyEnvironment({}),
            targets=["demographics__erwachsene_alle_rentner_hh"],
        )


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
def test_one_dot_plot_dag():
    """Make sure that the one dot graph example doesn't produce an error."""
    selectors = "einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y_sn"
    plot_dag(environment=environment, selectors=selectors)


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
def test_10_dots_plot_dag():
    """Make sure that when No.of nodes is larger than 10 or show_labels is false, the
    graph example doesn't produce an error and hover information works properly."""
    selector = {
        "type": "descendants",
        "node": "sozialversicherung__geringfügig_beschäftigt",
    }
    plot_dag(environment=environment, selectors=selector, orientation="h")


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
def test_horizontal_plot_dag():
    """Make sure that when we choose horizontal orientation, the graph example doesn't
    produce an error."""
    plot_dag(
        environment=environment,
        selectors=[
            {
                "node": "einkommensteuer__abgeltungssteuer__zu_versteuernde_kapitaleinkünfte_y_sn",  # noqa: E501
                "type": "neighbors",
            }
        ],
        orientation="h",
    )


@pytest.mark.xfail(reason="Visualization module was not updated to the new interface.")
def test_hover_source_code_plot_dag():
    """Make sure that when hover information is source code, the graph example doesn't
    produce an error and works properly."""
    plot_dag(
        environment=environment,
        selectors=[
            {
                "node": "einkommensteuer__abgeltungssteuer__zu_versteuernde_kapitaleinkünfte_y_sn",  # noqa: E501
                "type": "neighbors",
            }
        ],
        orientation="h",
        hover_source_code=True,
    )
