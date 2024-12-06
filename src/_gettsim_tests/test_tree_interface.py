from _gettsim.interface import compute_taxes_and_transfers
from gettsim import create_synthetic_data, set_up_policy_environment


def test_tree_interface():
    policy_env = set_up_policy_environment(2024)
    targets = {"eink_st": {"eink_st_y_sn": None}}
    data = create_synthetic_data(n_adults=1)
    compute_taxes_and_transfers(data, policy_env, targets)
