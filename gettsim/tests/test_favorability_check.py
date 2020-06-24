from itertools import product

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date


INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "kind",
    "_st_kein_kind_freib_tu",
    "_st_kind_freib_tu",
    "abgelt_st_tu",
    "_kindergeld_m_basis",
    "_kindergeld_m_tu_basis",
    "jahr",
]
YEARS = [2010, 2012, 2016]
TEST_COLUMNS = ["eink_st_tu", "kindergeld_m", "kindergeld_m_hh", "kindergeld_m_tu"]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(
        ROOT_DIR / "tests" / "test_data" / "test_dfs_favorability_check.csv"
    )


@pytest.mark.parametrize("year, column", product(YEARS, TEST_COLUMNS))
def test_favorability_check(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=year, policy_groups="eink_st_abzuege",
    )
    columns = [
        "_st_kein_kind_freib_tu",
        "_st_kind_freib_tu",
        "abgelt_st_tu",
        "_kindergeld_m_basis",
        "_kindergeld_m_tu_basis",
    ]

    result = compute_taxes_and_transfers(
        df,
        user_functions=policy_func_dict,
        user_columns=columns,
        targets=column,
        params=params_dict,
    )

    assert_series_equal(
        result[column], year_data[column], check_dtype=False, check_names=False
    )
