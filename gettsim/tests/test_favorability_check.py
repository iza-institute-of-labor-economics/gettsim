from itertools import product

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
    "kind",
    "st_kein_kind_freib_tu",
    "st_kind_freib_tu",
    "abgelt_st_tu",
    "kindergeld_m_basis",
    "kindergeld_m_basis_tu",
    "jahr",
]
YEARS = [2010, 2012, 2016]
TEST_COLUMNS = ["eink_st_tu", "kindergeld_m", "kindergeld_m_hh", "kindergeld_m_tu"]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(
        ROOT_DIR / "tests" / "test_data" / "test_dfs_favorability_check.csv"
    )


@pytest.mark.parametrize("year, target", product(YEARS, TEST_COLUMNS))
def test_favorability_check(input_data, year, target):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    columns_overriding_functions = [
        "st_kein_kind_freib_tu",
        "st_kind_freib_tu",
        "abgelt_st_tu",
        "kindergeld_m_basis",
        "kindergeld_m_basis_tu",
    ]

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=columns_overriding_functions,
    )

    assert_series_equal(result[target], year_data[target], check_dtype=False)
