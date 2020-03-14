import datetime

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal

from gettsim.benefits.wohngeld import calc_min_rent
from gettsim.benefits.wohngeld import calc_min_rent_regrouped
from gettsim.benefits.wohngeld import calc_wg_abzuege_regrouped
from gettsim.benefits.wohngeld import regrouped_wohngeld_formel
from gettsim.benefits.wohngeld import wg
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.policy_for_date import load_regrouped_wohngeld

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
    "elterngeld_m",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "unterhaltsvors_m",
    "brutto_eink_1",
    "brutto_eink_4",
    "brutto_eink_5",
    "brutto_eink_6",
    "eink_st_m",
    "rentenv_beit_m",
    "ges_krankv_beit_m",
    "behinderungsgrad",
    "jahr",
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
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    wohngeld_params = get_policies_for_date(
        year=year, group="wohngeld", raw_group_data=wohngeld_raw_data
    )
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hh_id").apply(wg, params=wohngeld_params)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])


@pytest.mark.parametrize("year", YEARS)
def test_regrouped_wohngeld_formula(input_data, year):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data.copy()

    actual_date = datetime.date(year=year, month=1, day=1)
    wohngeld_params = load_regrouped_wohngeld(actual_date)

    for hid in df["hh_id"].unique():
        hh_size = len(df[df["hh_id"] == hid])
        wohngeld_basis = regrouped_wohngeld_formel(
            df[df["hh_id"] == hid], wohngeld_params, hh_size
        )
        assert_allclose(
            year_data[year_data["hh_id"] == hid]["wohngeld_basis_hh"].iloc[0],
            wohngeld_basis.iloc[0],
            atol=0.1,
        )


@pytest.mark.parametrize("year", YEARS)
def test_regrouped_wohngeld_min_rent(input_data, wohngeld_raw_data, year):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data.copy()

    actual_date = datetime.date(year=year, month=1, day=1)
    wohngeld_params = load_regrouped_wohngeld(actual_date)

    wohngeld_params_org = get_policies_for_date(
        year=year, group="wohngeld", raw_group_data=wohngeld_raw_data
    )

    for hid in df["hh_id"].unique():
        hh_size = len(df[df["hh_id"] == hid])

        assert calc_min_rent_regrouped(wohngeld_params, hh_size) == calc_min_rent(
            wohngeld_params_org, hh_size
        )


@pytest.mark.parametrize("year", YEARS)
def test_regrouped_wohngeld_abzuege(input_data, year):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data.copy()
    actual_date = datetime.date(year=year, month=1, day=1)
    wohngeld_params = load_regrouped_wohngeld(actual_date)

    for hid in df["hh_id"].unique():
        for inc in [
            "arbeitsl_geld_m",
            "sonstig_eink_m",
            "brutto_eink_1",
            "brutto_eink_4",
            "brutto_eink_5",
            "brutto_eink_6",
            "eink_st_m",
            "rentenv_beit_m",
            "ges_krankv_beit_m",
            "unterhaltsvors_m",
            "elterngeld_m",
        ]:
            df[f"{inc}_tu_k"] = df.groupby("tu_id")[inc].transform("sum")
        abzuege = calc_wg_abzuege_regrouped(df[df["hh_id"] == hid], wohngeld_params,)
        assert_series_equal(
            year_data[year_data["hh_id"] == hid]["_wohngeld_abzüge"],
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
    year_data = input_data_2[input_data_2["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    wohngeld_params = get_policies_for_date(
        year=year, group="wohngeld", raw_group_data=wohngeld_raw_data
    )
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hh_id").apply(wg, params=wohngeld_params)
    assert_frame_equal(df[TEST_COLUMN], year_data[TEST_COLUMN])
