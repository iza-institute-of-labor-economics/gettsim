import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "alleinerz",
    "alter",
    "bruttolohn_m",
    "sonstig_eink_m",
    "kapitaleink_brutto_m",
    "eink_vermietung_m",
    "eink_selbst_m",
    "arbeitsl_geld_m",
    "sum_ges_rente_priv_rente_m",
    "jahr",
    "monat",
]
OUT_COLS = ["unterhaltsvors_m"]
YEAR_MONTHS = [[2018, 1], [2019, 1], [2019, 8]]


@pytest.fixture(scope="module")
def input_data():
    file_name = "unterhalt.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize(
    "column, year, month",
    [
        (col, year_month[0], year_month[1])
        for col in OUT_COLS
        for year_month in YEAR_MONTHS
    ],
)
def test_unterhalt(input_data, column, year, month):
    year_data = input_data[
        (input_data["jahr"] == year) & (input_data["monat"] == month)
    ].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=f"{year}-{month}")

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=["arbeitsl_geld_m", "sum_ges_rente_priv_rente_m"],
    )

    assert_series_equal(
        result[column], year_data[column], check_dtype=False, atol=0, rtol=0
    )
