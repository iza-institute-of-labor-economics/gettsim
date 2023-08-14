"""
Test for BUG-fix #629
https://github.com/iza-institute-of-labor-economics/gettsim/issues/629
"""
import numpy as np

from _gettsim_tests._helpers import cached_set_up_policy_environment

policy_params, policy_functions = cached_set_up_policy_environment(date="1.1.2005")


def test_check_intercepts():
    intercepts = policy_params["eink_st"]["rente_ertragsanteil"][
        "intercepts_at_lower_thresholds"
    ]
    assert (intercepts == np.array([0.27, 0.5, 0.8, 1])).all()
