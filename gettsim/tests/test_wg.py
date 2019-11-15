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
    "hh_korr",
    "hhsize",
    "child",
    "miete",
    "heizkost",
    "alleinerz",
    "child11_num_tu",
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
    "divdy",
    "year",
    "hhsize_tu",
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
def test_wg(input_data, raw_tax_policy_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    tb = get_policies_for_date(year=year, tax_data_raw=raw_tax_policy_data)
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hid").apply(wg, tb=tb)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])


@pytest.fixture(scope="module")
def input_data_2():
    file_name = "test_dfs_wg2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", [2013])
def test_wg_no_mietstufe_in_input_data(input_data_2, raw_tax_policy_data, year):
    year_data = input_data_2[input_data_2["year"] == year]
    df = year_data[INPUT_COLS].copy()
    tb = get_policies_for_date(year=year, tax_data_raw=raw_tax_policy_data)
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hid").apply(wg, tb=tb)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])
