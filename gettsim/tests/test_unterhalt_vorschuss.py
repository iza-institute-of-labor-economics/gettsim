import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "alleinerziehend",
    "alter",
    "bruttolohn_m",
    "sonstig_eink_m",
    "kapital_eink_m",
    "vermiet_eink_m",
    "eink_selbst_m",
    "arbeitsl_geld_m",
    "ges_rente_m",
    "jahr",
    "monat",
]
OUT_COLS = ["unterhaltsvors_m"]
YEARS = [2017, 2018, 2019]
MONTHS = [8, 1]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_uhv.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize(
    "year, column, month", itertools.product(YEARS, OUT_COLS, MONTHS)
)
def test_uhv(input_data, year, column, month):
    year_data = input_data[
        (input_data["jahr"] == year) & (input_data["monat"] == month)
    ]
    df = year_data[INPUT_COLS].copy()
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=f"{year}-{month}", policy_groups=["unterhalt", "kindergeld"]
    )

    result = compute_taxes_and_transfers(
        df,
        columns_overriding_functions=["arbeitsl_geld_m"],
        targets=column,
        params=params_dict,
    )

    assert_series_equal(result[column], year_data[column], check_dtype=False)
