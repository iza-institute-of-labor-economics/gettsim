import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment

INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "alter",
    "arbeitsstunden_w",
    "in_ausbildung",
    "bruttolohn_m",
]
OUT_COLS = ["_kindergeld_m_basis", "_kindergeld_m_tu_basis"]
YEARS = [2000, 2002, 2010, 2011, 2013, 2019]
TEST_COLS = ["_kindergeld_m_tu_basis"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_kindergeld.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLS))
def test_kindergeld(input_data, year, column):

    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    params, policy_functions = set_up_policy_environment(date=year)

    calc_result = compute_taxes_and_transfers(
        df, params=params, functions=policy_functions, targets=column
    )

    assert_series_equal(calc_result[column], year_data[column], check_dtype=False)
