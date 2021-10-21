""" Test the updating of Entgeltpunkte and
the pension income based on Entgeltpunkte.

These are "only" regression tests.
"""
import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim import compute_taxes_and_transfers
from gettsim import set_up_policy_environment
from gettsim.config import ROOT_DIR


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_m",
    "wohnort_ost",
    "alter",
    "jahr",
    "geburtsjahr",
    "entgeltpunkte",
]

OUT_COLS = [
    "rente_anspr_excl_gr_m",
    "entgeltpunkte_update",
    "entgeltpunkte_lohn",
    # "regelaltersgrenze",
    # "rentenv_beitr_bemess_grenze",
]

YEARS = [2010, 2012, 2015]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_pensions.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_pension(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=f"{year}-07-01")

    calc_result = compute_taxes_and_transfers(
        data=df, params=policy_params, functions=policy_functions, targets=column,
    )
    assert_series_equal(calc_result[column], year_data[column])
