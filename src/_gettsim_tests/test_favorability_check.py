from itertools import product

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
    "kind",
    "eink_st_ohne_kinderfreib_tu",
    "eink_st_mit_kinderfreib_tu",
    "zu_verst_eink_mit_kinderfreib_tu",
    "_zu_verst_eink_ohne_kinderfreib_tu",
    "abgelt_st_tu",
    "kindergeld_m",
    "jahr",
]
YEARS = [2010, 2012, 2016]
TEST_COLUMNS = ["eink_st_tu", "zu_verst_eink_tu"]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(TEST_DATA_DIR / "favorability_check.csv")


@pytest.mark.parametrize("year, target", product(YEARS, TEST_COLUMNS))
def test_favorability_check(input_data, year, target):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    columns_overriding_functions = [
        "eink_st_ohne_kinderfreib_tu",
        "eink_st_mit_kinderfreib_tu",
        "abgelt_st_tu",
        "kindergeld_m",
        "zu_verst_eink_mit_kinderfreib_tu",
        "_zu_verst_eink_ohne_kinderfreib_tu",
    ]

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=columns_overriding_functions,
    )

    assert_series_equal(
        result[target], year_data[target], check_dtype=False, atol=1e-1, rtol=0
    )
