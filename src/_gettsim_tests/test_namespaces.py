"""Test namespace-specific function processing."""

import pandas as pd
import pytest

from _gettsim.aggregation import AggregateByGroupSpec, AggregateByPIDSpec
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import PolicyEnvironment
from _gettsim_tests.test_data.namespaces.module1 import FUNCTIONS_MODULE1
from _gettsim_tests.test_data.namespaces.module2 import FUNCTIONS_MODULE2


@pytest.fixture
def functions_tree():
    return {
        **FUNCTIONS_MODULE1,
        **FUNCTIONS_MODULE2,
    }


@pytest.fixture
def parameters():
    return {
        "module1": {
            "a": 1,
            "b": 1,
            "c": 1,
        },
        "module2": {
            "a": 1,
            "b": 1,
            "c": 1,
        },
    }


@pytest.fixture
def aggregation_tree():
    return {
        "module1": {
            "group_mean_bg": AggregateByGroupSpec(
                source_col="f",
                aggr="sum",
            ),
        },
        "module2": {
            "p_id_aggregation_target": AggregateByPIDSpec(
                p_id_to_aggregate_by="groupings__some_foreign_keys",
                source_col="g_hh",
                aggr="sum",
            ),
        },
    }


def test_compute_taxes_and_transfers_with_tree(
    functions_tree, parameters, aggregation_tree
):
    """Test compute_taxes_and_transfers with function tree input."""
    policy_env = PolicyEnvironment(
        functions_tree=functions_tree,
        params=parameters,
        aggregation_specs_tree=aggregation_tree,
    )
    targets = {
        "module1": {
            "g_hh": None,
            "group_mean_bg": None,
        },
        "module2": {
            "g_hh": None,
            "p_id_aggregation_target": None,
        },
    }
    data = {
        "demographics": {
            "p_id": pd.Series([0, 1, 2]),
            "hh_id": pd.Series([0, 0, 1]),
            "ehe_id": pd.Series([0, 1, 2]),
        },
        "arbeitslosengeld_2": {
            "bg_id": pd.Series([0, 1, 2]),
            "eg_id": pd.Series([0, 1, 2]),
            "fg_id": pd.Series([0, 1, 2]),
        },
        "wohngeld": {
            "wthh_id": pd.Series([0, 1, 2]),
        },
        "einkommensteuer": {
            "sn_id": pd.Series([0, 1, 2]),
        },
        "groupings": {
            "some_foreign_keys": pd.Series([2, 0, 1]),
        },
        "module1": {
            "f": pd.Series([1, 2, 3]),
        },
    }
    compute_taxes_and_transfers(data, policy_env, targets)
