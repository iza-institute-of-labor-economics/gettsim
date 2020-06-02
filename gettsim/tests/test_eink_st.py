import itertools
from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.tests.auxiliary import select_output_by_level


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
    policy_date = date(year, 1, 1)

    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date,
        groups=["eink_st", "eink_st_abzuege", "soli_st", "abgelt_st"],
    )

    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()

    data = dict(df)

    data["_zu_verst_eink_kein_kinderfreib_tu"] = (
        df["_zu_verst_eink_kein_kinderfreib"].groupby(df["tu_id"]).sum()
    )

    data["_zu_verst_eink_kinderfreib_tu"] = (
        df["_zu_verst_eink_kinderfreib"].groupby(df["tu_id"]).sum()
    )

    columns = [
        "_zu_verst_eink_kein_kinderfreib_tu",
        "_zu_verst_eink_kinderfreib_tu",
        "brutto_eink_5",
    ]

    result = compute_taxes_and_transfers(
        data, user_columns=columns, targets=column, params=params_dict
    )

    expected_result = select_output_by_level(column, year_data)

    assert_series_equal(
        result,
        expected_result,
        check_dtype=False,
        check_less_precise=1,
        check_names=False,
        check_index_type=False,
    )
