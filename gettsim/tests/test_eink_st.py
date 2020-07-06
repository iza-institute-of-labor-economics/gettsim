import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "_zu_verst_eink_kein_kinderfreib",
    "_zu_verst_eink_kinderfreib",
    "brutto_eink_5",
]

TEST_COLUMNS = [
    "_st_kein_kind_freib_tu",
    "_st_kind_freib_tu",
    "abgelt_st_tu",
    "soli_st_tu",
]
YEARS = [2009, 2012, 2015, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_sched.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLUMNS))
def test_tax_sched(
    input_data, year, column,
):
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=year,
        policy_groups=["eink_st", "eink_st_abzuege", "soli_st", "abgelt_st"],
    )

    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()

    df["_zu_verst_eink_kein_kinderfreib_tu"] = (
        df["_zu_verst_eink_kein_kinderfreib"].groupby(df["tu_id"]).transform("sum")
    )

    df["_zu_verst_eink_kinderfreib_tu"] = (
        df["_zu_verst_eink_kinderfreib"].groupby(df["tu_id"]).transform("sum")
    )

    columns = [
        "_zu_verst_eink_kein_kinderfreib_tu",
        "_zu_verst_eink_kinderfreib_tu",
        "brutto_eink_5",
    ]

    result = compute_taxes_and_transfers(
        df, user_columns=columns, targets=column, params=params_dict
    )

    assert_series_equal(
        result[column], year_data[column], check_dtype=False, check_less_precise=2,
    )
