""" Some tests for the dag module"""
import networkx as nx
import pytest

from gettsim.dag import _fail_if_dag_contains_cycle


def test_fail_if_dag_contains_cycle():
    dag = nx.DiGraph({"1": "2", "2": "1"})
    with pytest.raises(ValueError):
        _fail_if_dag_contains_cycle(dag)
