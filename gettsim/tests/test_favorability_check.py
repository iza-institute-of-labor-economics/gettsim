from datetime import date
from itertools import product

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.taxes.favorability_check import favorability_check


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
def test_favorability_check(input_data, year, column, eink_st_abzuege_raw_data):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    eink_st_abzuege_params = get_policies_for_date(
        policy_date=policy_date,
        group="eink_st_abzuege",
        raw_group_data=eink_st_abzuege_raw_data,
    )
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby().apply(favorability_check, params=eink_st_abzuege_params)
    assert_series_equal(df[column], year_data[column])
