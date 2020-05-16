from datetime import date
from itertools import product

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.tests.auxiliary import select_output_by_level


INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "gem_veranlagt",
    "kind",
    "_st_kein_kind_freib_tu",
    "_st_kind_freib_tu",
    "abgelt_st_m_tu",
    "kindergeld_m_basis",
    "kindergeld_m_tu_basis",
    "jahr",
]
OUT_COLS = [
    "eink_st_m_tu",
    "eink_st_m",
    "kindergeld_m",
    "kindergeld_m_hh",
    "kindergeld_m_tu",
]
YEARS = [2010, 2012, 2016]
TEST_COLUMNS = ["eink_st_m_tu", "kindergeld_m", "kindergeld_m_hh", "kindergeld_m_tu"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_favorability_check.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", product(YEARS, TEST_COLUMNS))
def test_favorability_check(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date, groups="eink_st_abzuege",
    )
    columns = [
        "_st_kein_kind_freib_tu",
        "_st_kind_freib_tu",
        "abgelt_st_m_tu",
        "kindergeld_m_basis",
        "kindergeld_m_tu_basis",
    ]
    calc_result = compute_taxes_and_transfers(
        df, user_columns=columns, targets=column, params=params_dict
    )

    expected_result = select_output_by_level(column, year_data)
    assert_series_equal(
        calc_result, expected_result, check_dtype=False, check_names=False
    )
