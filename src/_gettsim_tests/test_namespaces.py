"""Test namespace-specific function processing."""

import pandas as pd

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import PolicyEnvironment
from _gettsim_tests.test_data.namespaces.module1 import FUNCTIONS_MODULE1
from _gettsim_tests.test_data.namespaces.module2 import FUNCTIONS_MODULE2

FUNCTIONS_TREE = {
    **FUNCTIONS_MODULE1,
    **FUNCTIONS_MODULE2,
}

PARAMETERS = {
    "module1_params": {
        "a": 1,
        "b": 1,
        "c": 1,
    },
    "module2_params": {
        "a": 1,
        "b": 1,
        "c": 1,
    },
}


def test_compute_taxes_and_transfers_with_tree():
    """Test compute_taxes_and_transfers with function tree input."""
    policy_env = PolicyEnvironment(
        functions_tree=FUNCTIONS_TREE,
        params=PARAMETERS,
    )
    targets = {
        "module1": {"g_hh": None},
        "module2": {"g_hh": None},
    }
    data = {
        "groupings": {  # To set groupings functions off
            "p_id": pd.Series([0, 1, 2]),
            "hh_id": pd.Series([0, 0, 1]),
            "bg_id": pd.Series([0, 1, 2]),
            "eg_id": pd.Series([0, 1, 2]),
            "ehe_id": pd.Series([0, 1, 2]),
            "wthh_id": pd.Series([0, 1, 2]),
            "sn_id": pd.Series([0, 1, 2]),
            "fg_id": pd.Series([0, 1, 2]),
        },
        "module1": {
            "f": pd.Series([1, 2, 3]),
        },
    }
    compute_taxes_and_transfers(data, policy_env, targets)
