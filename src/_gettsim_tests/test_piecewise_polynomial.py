"""
Tests for `piecewise_polynomial`
"""
import numpy as np
from _gettsim.piecewise_functions import (
    get_piecewise_parameters,
)


def test_get_intercepts_for_piecewise_polynomial():
    params = {
        "type": "piecewise_quadratic",
        "progressionsfaktor": True,
        0: {
            "lower_threshold": "-inf",
            "upper_threshold": 2005,
            "rate_linear": 0,
            "intercept_at_lower_threshold": 0.27,
        },
        1: {
            "lower_threshold": 2005,
            "upper_threshold": 2021,
            "rate_linear": 0.02,
            "intercept_at_lower_threshold": 0.5,
        },
        2: {
            "lower_threshold": 2021,
            "upper_threshold": 2041,
            "rate_linear": 0.01,
            "intercept_at_lower_threshold": 0.8,
        },
        3: {
            "lower_threshold": 2041,
            "upper_threshold": "inf",
            "rate_linear": 0,
            "intercept_at_lower_threshold": 1,
        },
    }

    piecewise_parameters = get_piecewise_parameters(
        params,
        "eink_st_tarif",
        "linear",
    )

    assert (
        piecewise_parameters["intercepts_at_lower_thresholds"]
        == np.array([0.27, 0.5, 0.8, 1])
    ).all()
