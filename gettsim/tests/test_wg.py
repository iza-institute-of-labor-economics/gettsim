import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.wohngeld import wg
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "tu_vorstand",
    "kind",
    "kaltmiete_m",
    "heizkost_m",
    "alleinerziehend",
    "alter",
    "immobilie_baujahr",
    "mietstufe",
    "bruttolohn_m",
    "ges_rente_m",
    "_ertragsanteil",
    "elterngeld",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "unterhaltsvors_m",
    "brutto_eink_1",
    "brutto_eink_4",
    "brutto_eink_5",
    "brutto_eink_6",
    "eink_st",
    "rentenv_beit_m",
    "ges_krankv_beit_m",
    "behinderungsgrad",
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
    df = df.groupby("hh_id").apply(wg, params=wohngeld_params)
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
    df = df.groupby("hh_id").apply(wg, params=wohngeld_params)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])
