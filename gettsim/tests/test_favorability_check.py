from itertools import product

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.favorability_check import favorability_check


INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "gem_veranlagt",
    "kind",
    "_st_kein_kind_freib_tu",
    "_st_kind_freib_tu",
    "abgelt_st_tu",
    "kindergeld_m_basis",
    "kindergeld_m_tu_basis",
    "year",
]
OUT_COLS = [
    "eink_st_tu",
    "eink_st",
    "kindergeld_m",
    "kindergeld_m_hh",
    "kindergeld_m_tu",
]
YEARS = [2010, 2012, 2016]
TEST_COLUMNS = ["eink_st_tu", "kindergeld_m", "kindergeld_m_hh", "kindergeld_m_tu"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_favorability_check.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", product(YEARS, TEST_COLUMNS))
def test_favorability_check(input_data, year, column, e_st_abzuege_raw_data):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    e_st_abzuege_params = get_policies_for_date(
        year=year, group="e_st_abzuege", raw_group_data=e_st_abzuege_raw_data
    )
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hh_id", "tu_id"]).apply(
        favorability_check, params=e_st_abzuege_params
    )
    assert_series_equal(df[column], year_data[column])
