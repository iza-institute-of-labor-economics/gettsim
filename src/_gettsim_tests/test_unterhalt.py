import itertools

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
    "kind_unterh_anspr_m",
    "kindergeld_m",
    "jahr",
    "kind",
]
OUT_COLS = ["kind_unterh_zahlbetr_m"]
YEARS = [2023]


@pytest.fixture(scope="module")
def input_data():
    file_name = "unterhalt.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_unterhalt(input_data, column, year):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=["kindergeld_m"],
    )

    assert_series_equal(
        result[column], year_data[column], check_dtype=False, atol=0, rtol=0
    )
