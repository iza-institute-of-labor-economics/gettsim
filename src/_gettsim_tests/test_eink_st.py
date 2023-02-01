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
    "kind",
    "zu_verst_eink_kein_kinderfreib",
    "zu_verst_eink_kinderfreib",
    "kapitaleink_brutto",
]

TEST_COLUMNS = [
    "eink_st_ohne_kinderfreib_tu",
    "eink_st_mit_kinderfreib_tu",
    "abgelt_st_tu",
    "soli_st_tu",
]
YEARS = [2009, 2012, 2015, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "eink_st.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLUMNS))
def test_eink_st(
    input_data,
    year,
    column,
):
    policy_params, policy_functions = set_up_policy_environment(date=year)

    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()

    df["_zu_verst_eink_ohne_kinderfreib_tu"] = (
        df["zu_verst_eink_kein_kinderfreib"].groupby(df["tu_id"]).transform("sum")
    )

    df["zu_verst_eink_mit_kinderfreib_tu"] = (
        df["zu_verst_eink_kinderfreib"].groupby(df["tu_id"]).transform("sum")
    )

    columns = [
        "_zu_verst_eink_ohne_kinderfreib_tu",
        "zu_verst_eink_mit_kinderfreib_tu",
        "kapitaleink_brutto",
    ]

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=columns,
    )

    assert_series_equal(
        result[column], year_data[column], check_dtype=False, atol=1, rtol=0
    )
