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
    "kind",
    "arbeitsstunden_w",
    "in_ausbildung",
    "bruttolohn_m",
    "zu_verst_eink_kein_kinderfreib_tu",
]
YEARS = [2002, 2010, 2011, 2013, 2019, 2020, 2021]
TEST_COLS = [
    "kindergeld_m_basis_tu",
    "kinderbonus_m_basis_tu",
    "kindergeld_m_hh",
    "kinderbonus_m_hh",
    "kinderbonus_m_tu",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_kindergeld.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, target", itertools.product(YEARS, TEST_COLS))
def test_kindergeld(input_data, year, target):

    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    user_cols = ["zu_verst_eink_kein_kinderfreib_tu"]
    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=user_cols,
    )
    assert_series_equal(calc_result[target], year_data[target], check_dtype=False)
