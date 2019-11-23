import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.wohngeld import wg
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date

INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "head_tu",
    "child",
    "miete",
    "heizkost",
    "alleinerz",
    "age",
    "cnstyr",
    "mietstufe",
    "m_wage",
    "m_pensions",
    "ertragsanteil",
    "m_alg1",
    "m_transfers",
    "uhv",
    "gross_e1",
    "gross_e4",
    "gross_e5",
    "gross_e6",
    "incometax",
    "rvbeit",
    "gkvbeit",
    "handcap_degree",
    "year",
]
OUT_COLS = ["wohngeld_basis", "wohngeld_basis_hh"]
YEARS = [2006, 2009, 2013, 2016, 2018, 2019]
TEST_COLUMN = ["wohngeld_basis_hh"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_wg.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_wg(input_data, year, wohngeld_raw_data):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    wohngeld_params = get_policies_for_date(
        year=year, group="wohngeld", raw_group_data=wohngeld_raw_data
    )
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hid").apply(wg, wohngeld_params=wohngeld_params)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])


@pytest.fixture(scope="module")
def input_data_2():
    file_name = "test_dfs_wg2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", [2013])
def test_wg_no_mietstufe_in_input_data(input_data_2, year, wohngeld_raw_data):
    year_data = input_data_2[input_data_2["year"] == year]
    df = year_data[INPUT_COLS].copy()
    wohngeld_params = get_policies_for_date(
        year=year, group="wohngeld", raw_group_data=wohngeld_raw_data
    )
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hid").apply(wg, wohngeld_params=wohngeld_params)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])
