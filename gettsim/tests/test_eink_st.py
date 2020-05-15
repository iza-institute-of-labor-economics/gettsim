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
    "_zu_versteuerndes_eink_kein_kind_freib",
    "_zu_versteuerndes_eink_kind_freib",
    "_zu_versteuerndes_eink_abgelt_st_m_kind_freib",
    "_zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib",
    "brutto_eink_5",
    "gem_veranlagt",
    "brutto_eink_5_tu",
]

TEST_COLUMNS = [
    "_st_kein_kind_freib_tu",
    "_st_kind_freib_tu",
    "abgelt_st_m",
    "abgelt_st_m_tu",
    "soli_st_m",
    "soli_st_m_tu",
]

OUT_COLS = [
    "_st_kein_kind_freib_tu",
    "_st_kind_freib_tu",
    "_st_kein_kind_freib",
    "_st_kind_freib",
    "abgelt_st_m",
    "abgelt_st_m_tu",
    "soli_st_m",
    "soli_st_m_tu",
]
YEARS = [2009, 2012, 2015, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_sched.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLUMNS))
def test_tax_sched(
    input_data,
    year,
    column,
    eink_st_raw_data,
    eink_st_abzuege_raw_data,
    soli_st_raw_data,
    abgelt_st_raw_data,
):
    policy_date = date(year, 1, 1)
    eink_st_params = get_policies_for_date(
        policy_date=policy_date, group="eink_st", raw_group_data=eink_st_raw_data
    )

    eink_st_abzuege_params = get_policies_for_date(
        policy_date=policy_date,
        group="eink_st_abzuege",
        raw_group_data=eink_st_abzuege_raw_data,
    )
    soli_st_params = get_policies_for_date(
        policy_date=policy_date, group="soli_st", raw_group_data=soli_st_raw_data
    )
    abgelt_st_params = get_policies_for_date(
        policy_date=policy_date, group="abgelt_st", raw_group_data=abgelt_st_raw_data
    )

    params_dict = {
        "eink_st_params": eink_st_params,
        "eink_st_abzuege_params": eink_st_abzuege_params,
        "soli_st_params": soli_st_params,
        "abgelt_st_params": abgelt_st_params,
    }

    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()

    result = compute_taxes_and_transfers(dict(df), targets=column, params=params_dict)

    expected_result = select_output_by_level(column, year_data)

    assert_series_equal(
        result,
        expected_result,
        check_dtype=False,
        check_less_precise=1,
        check_names=False,
    )
