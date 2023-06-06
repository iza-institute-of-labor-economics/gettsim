"""Test für Erziehungsgeld

"""
import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_vorj_m",
    "geburtstag",
    "alleinerz",
    "arbeitsstunden_w",
    "in_ausbildung",
    "geburtsjahr",
    "bruttolohn_m",
    "alter",
    "geburtsmonat",
    "hat_kinder",
]

OUT_COLS = [
    "erziehungsgeld_m",
]

YEARS = [2005]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_erziehungsgeld.csv"
    out = pd.read_csv("test_data/erziehungsgeld/" + file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_erziehungsgeld(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=f"{year}-01-01"
    )

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
    )
    assert_series_equal(
        calc_result[column], year_data[column], atol=1e-1, rtol=0, check_dtype=False
    )
