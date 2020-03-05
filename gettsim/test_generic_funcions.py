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
        "lower_thresholds": np.array([0, 100, 500]),
        "upper_thresholds": np.asfarray([100, 500, np.inf]),
        "rates": np.array([0.5, 0.4, 0]),
        "intercepts": np.array([0, 50, 210]),
        "dict": {
            0: {
                "lower_threshold": 0,
                "upper_threshold": 50,
                "rate": 1,
                "intercept_at_lower_threshold": 0,
            },
            1: {"upper_threshold": 150, "rate": 0.5},
            2: {"upper_threshold": 250, "rate": 0.1},
            3: {"upper_threshold": np.inf, "rate": 0},
        },
        "dict_wrong_key": {
            4: {
                "lower_threshold": 0,
                "upper_threshold": 50,
                "rate": 1,
                "intercept_at_lower_threshold": 0,
            },
            1: {"upper_threshold": 150, "rate": 0.5},
            2: {"upper_threshold": 250, "rate": 0.1},
            3: {"upper_threshold": np.inf, "rate": 0},
        },
        "dict_missing_lowest_threshold": {
            0: {"upper_threshold": 50, "rate": 1, "intercept_at_lower_threshold": 0},
            1: {"upper_threshold": 150, "rate": 0.5},
            2: {"upper_threshold": 250, "rate": 0.1},
            3: {"upper_threshold": np.inf, "rate": 0},
        },
        "dict_omit_key": {
            0: {
                "lower_threshold": 0,
                "upper_threshold": 50,
                "rate": 1,
                "intercept_at_lower_threshold": 0,
            },
            2: {"upper_threshold": 150, "rate": 0.5},
            3: {"upper_threshold": 250, "rate": 0.1},
            4: {"upper_threshold": np.inf, "rate": 0},
        },
        "dict_missing_threshold": {
            0: {
                "lower_threshold": 0,
                "upper_threshold": 50,
                "rate": 1,
                "intercept_at_lower_threshold": 0,
            },
            1: {"rate": 0.5},
            2: {"upper_threshold": 250, "rate": 0.1},
            3: {"upper_threshold": np.inf, "rate": 0},
        },
        "dict_missing_rate": {
            0: {
                "lower_threshold": 0,
                "upper_threshold": 50,
                "rate": 1,
                "intercept_at_lower_threshold": 0,
            },
            1: {"upper_threshold": 150},
            2: {"upper_threshold": 250, "rate": 0.1},
            3: {"upper_threshold": np.inf, "rate": 0},
        },
        "dict_no_intercept": {
            0: {"lower_threshold": 0, "upper_threshold": 50, "rate": 1},
            1: {"upper_threshold": 150, "rate": 0.5},
            2: {"upper_threshold": 250, "rate": 0.1},
            3: {"upper_threshold": np.inf, "rate": 0},
        },
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
        input_data["lower_thresholds"],
        input_data["upper_thresholds"],
        input_data["rates"],
        0,
        piecewise_linear,
    )
    np.testing.assert_equal(icpts, expected_outcome["intercepts"])


def test_get_dict_of_arrays_piecewise_linear_len(input_data):
    arrays = get_dict_of_arrays_piecewise_linear(input_data["dict"])
    assert (
        len(arrays["lower_thresholds"])
        == len(arrays["upper_thresholds"])
        == len(arrays["rates"])
        == len(arrays["intercepts"])
    )


def test_get_dict_of_arrays_piecewise_linear_wrong_key(input_data):
    with pytest.raises(
        ValueError,
        match="The keys of the passed list of dictionaries " "do not start with 0.",
    ):
        get_dict_of_arrays_piecewise_linear(input_data["dict_wrong_key"])


def test_get_dict_of_arrays_piecewise_linear_missing_lowest_threshold(input_data):
    with pytest.raises(
        ValueError,
        match="The first dictionary of the passed list needs "
        "to contain a lower_threshold value.",
    ):
        get_dict_of_arrays_piecewise_linear(input_data["dict_missing_lowest_threshold"])


def test_get_dict_of_arrays_piecewise_linear_omit_key(input_data):
    with pytest.raises(
        ValueError,
        match="The keys of the passed list of dictionaries "
        "are not consecutive numbers.",
    ):
        get_dict_of_arrays_piecewise_linear(input_data["dict_omit_key"])


def test_get_dict_of_arrays_piecewise_linear_missing_threshold(input_data):
    with pytest.raises(
        ValueError,
        match="Current Key: 2. Either this dictionary needs to "
        "contain a lower_thresholds value or the previous "
        "dictionary needs to contain an upper_threshold value.",
    ):
        get_dict_of_arrays_piecewise_linear(input_data["dict_missing_threshold"])


def test_get_dict_of_arrays_piecewise_linear_missing_rate(input_data):
    with pytest.raises(
        ValueError,
        match="Current Key: 1. The current " "dictionary has no rate specified.",
    ):
        get_dict_of_arrays_piecewise_linear(input_data["dict_missing_rate"])


def test_get_dict_of_arrays_piecewise_linear_no_intercept(input_data):
    with pytest.raises(
        ValueError,
        match="The first dictionary needs an intercept, "
        "because either the lowest intercept or all "
        "intercepts must be passed.",
    ):
        get_dict_of_arrays_piecewise_linear(input_data["dict_no_intercept"])


def test_piecewise_linear(input_data, expected_outcome):
    e_anr_frei = piecewise_linear(
        input_data["value"],
        input_data["lower_thresholds"],
        input_data["upper_thresholds"],
        input_data["rates"],
        input_data["intercepts"],
        side="left",
    )
    assert e_anr_frei == expected_outcome["res_value"]
