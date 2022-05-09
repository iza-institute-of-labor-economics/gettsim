import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim import compute_taxes_and_transfers
from gettsim import set_up_policy_environment
from gettsim.config import ROOT_DIR


INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "jahr",
    "anz_kindergeld_kinder_tu",
    "wohnort_ost",
    "steuerklasse",
    "ges_krankenv_zusatz",
    "bruttolohn_m",
    "alter",
    "hat_kinder",
]

OUT_COLS = [
    "lohn_st",
    "lohn_st_soli",
]


YEARS = [2020]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(ROOT_DIR / "tests" / "test_data" / "lohn_st_2.csv")


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_lohnsteuer_2(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
    )
    assert_series_equal(result[column], year_data[column], check_dtype=False)
