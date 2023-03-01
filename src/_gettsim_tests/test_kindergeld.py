import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "alter",
    "kind",
    "arbeitsstunden_w",
    "in_ausbildung",
    "bruttolohn_m",
    "_zu_verst_eink_ohne_kinderfreib_tu",
]
YEARS = [2002, 2010, 2011, 2013, 2019, 2020, 2021]
TEST_COLS = [
    "kindergeld_m_tu",
    "kinderbonus_m_tu",
    "kindergeld_m_hh",
    "kinderbonus_m_hh",
    "kinderbonus_m_tu",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "kindergeld.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year, target", itertools.product(YEARS, TEST_COLS))
def test_kindergeld(input_data, year, target):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    user_cols = ["_zu_verst_eink_ohne_kinderfreib_tu"]
    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=user_cols,
    )
    assert_series_equal(
        calc_result[target], year_data[target], check_dtype=False, atol=0, rtol=0
    )
