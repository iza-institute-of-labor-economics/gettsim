"""Test generic_functions.py.

"""
import numpy as np
import pytest

from gettsim.generic_functions import fill_intercepts_at_lower_thresholds
from gettsim.generic_functions import get_dict_of_arrays_piecewise_linear
from gettsim.generic_functions import piecewise_linear


@pytest.fixture
def input_data():
    out = {
        "value": 800,
        "upper_thresholds": np.asfarray([100, 500, np.inf]),
        "rates": np.array([0.5, 0.4, 0]),
        "intercepts": np.array([0, 50, 210]),
        "list": [
            {"upper_threshold": 50, "rate": 1},
            {"upper_threshold": 150, "rate": 0.5},
            {"upper_threshold": 250, "rate": 0.1},
            {"upper_threshold": np.inf, "rate": 0},
        ],
    }

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


def test_get_dict_of_arrays_piecewise_linear(input_data):
    dict = get_dict_of_arrays_piecewise_linear(input_data["list"])
    assert (
        len(dict["upper_thresholds"]) == len(dict["rates"]) == len(dict["intercepts"])
    )


def test_piecewise_linear(input_data, expected_outcome):
    e_anr_frei = piecewise_linear(
        input_data["value"],
        input_data["upper_thresholds"],
        input_data["rates"],
        input_data["intercepts"],
        side="left",
    )
    assert e_anr_frei == expected_outcome["res_value"]
