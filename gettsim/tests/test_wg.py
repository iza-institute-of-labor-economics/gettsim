import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal

from gettsim.benefits.wohngeld import calc_wg_abzuege_regrouped
from gettsim.benefits.wohngeld import regrouped_wohngeld_formel
from gettsim.benefits.wohngeld import wg
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.policy_for_date import load_regrouped_wohngeld

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
    "elterngeld",
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
    df = df.groupby("hid").apply(wg, params=wohngeld_params)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])


@pytest.mark.parametrize("year", YEARS)
def test_regrouped_wohngeld_formula(input_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data.copy()
    wohngeld_params = load_regrouped_wohngeld(year)

    for hid in df["hid"].unique():
        hh_size = len(df[df["hid"] == hid])
        wohngeld_basis = regrouped_wohngeld_formel(
            df[df["hid"] == hid], wohngeld_params, hh_size
        )
        assert_allclose(
            year_data[year_data["hid"] == hid]["wohngeld_basis_hh"].iloc[0],
            wohngeld_basis.iloc[0],
            atol=0.1,
        )


@pytest.mark.parametrize("year", YEARS)
def test_regrouped_wohngeld_abzuege(input_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data.copy()
    wohngeld_params = load_regrouped_wohngeld(year)

    for hid in df["hid"].unique():
        for inc in [
            "m_alg1",
            "m_transfers",
            "gross_e1",
            "gross_e4",
            "gross_e5",
            "gross_e6",
            "incometax",
            "rvbeit",
            "gkvbeit",
            "uhv",
            "elterngeld",
        ]:
            df[f"{inc}_tu_k"] = df.groupby("tu_id")[inc].transform("sum")
        abzuege = calc_wg_abzuege_regrouped(df[df["hid"] == hid], wohngeld_params,)
        assert_series_equal(
            year_data[year_data["hid"] == hid]["wg_abzuege"],
            abzuege,
            check_dtype=False,
            check_names=False,
        )


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
    df = df.groupby("hid").apply(wg, params=wohngeld_params)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])
