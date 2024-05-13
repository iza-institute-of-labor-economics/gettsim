"""
Tests for `piecewise_polynomial`
"""

import numpy
from _gettsim.piecewise_functions import (
    get_piecewise_parameters,
)


def test_get_piecewise_parameters_all_intercepts_supplied():
    params_dict = {
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

    actual = get_piecewise_parameters(
        parameter_dict=params_dict,
        parameter="test",
        func_type="linear",
    )["intercepts_at_lower_thresholds"]
    expected = numpy.array([0.27, 0.5, 0.8, 1])

    numpy.testing.assert_almost_equal(actual, expected, decimal=10)
