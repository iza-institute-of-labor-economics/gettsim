"""Test generic_functions.py.

"""
import numpy as np
import pytest
from generic_functions import fill_intercepts_at_lower_thresholds
from generic_functions import piecewise_linear


@pytest.fixture
def input_data():
    out = {}
    out["value"] = 800
    out["upper_thresholds"] = np.asfarray([100, 500, "inf"], float)
    out["rates"] = np.array([0.5, 0.4, 0])
    out["intercepts"] = np.array([0, 50, 210])

    return out


@pytest.fixture
def expected_outcome():
    out = {}
    out["res_value"] = 210
    out["intercepts"] = np.array([0, 50, 210])

    return out


def test_fill_intercepts_at_lower_thresholds(input_data, expected_outcome):
    icpts = fill_intercepts_at_lower_thresholds(
        input_data["upper_thresholds"], input_data["rates"], 0, piecewise_linear
    )
    np.testing.assert_equal(icpts, expected_outcome["intercepts"])


def test_piecewise_linear(input_data, expected_outcome):
    e_anr_frei = piecewise_linear(
        input_data["value"],
        input_data["upper_thresholds"],
        input_data["rates"],
        input_data["intercepts"],
        side="left",
    )
    assert e_anr_frei == expected_outcome["res_value"]
