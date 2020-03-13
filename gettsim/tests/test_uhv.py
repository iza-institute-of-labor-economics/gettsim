import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.unterhalt import uhv
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "alleinerziehend",
    "alter",
    "bruttolohn_m",
    "sonstig_eink_m",
    "kapital_eink_m",
    "vermiet_eink_m",
    "eink_selbstst_m",
    "arbeitsl_geld_m",
    "ges_rente_m",
    "gem_veranlagt",
    "jahr",
]
OUT_COL = "unterhaltsvors_m"
YEARS = [2017, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_uhv.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_uhv(input_data, year, unterhalt_raw_data):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    unterhalt_params = get_policies_for_date(
        year=year, group="unterhalt", raw_group_data=unterhalt_raw_data
    )
    kindergeld_params = get_policies_for_date(year=year, group="kindergeld")
    df[OUT_COL] = np.nan
    df = df.groupby(["hh_id", "tu_id"]).apply(
        uhv, params=unterhalt_params, kindergeld_params=kindergeld_params
    )
    assert_series_equal(df[OUT_COL], year_data["unterhaltsvors_m"], check_dtype=False)


@pytest.fixture(scope="module")
def input_data_2():
    file_name = "test_dfs_uhv2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", [2019])
def test_uhv_07_2019(input_data_2, year, unterhalt_raw_data):
    year_data = input_data_2[input_data_2["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    unterhalt_params = get_policies_for_date(
        year=year, group="unterhalt", raw_group_data=unterhalt_raw_data, month=8
    )
    kindergeld_params = get_policies_for_date(year=year, group="kindergeld", month=8)
    df[OUT_COL] = np.nan
    df = df.groupby(["hh_id", "tu_id"]).apply(
        uhv, params=unterhalt_params, kindergeld_params=kindergeld_params
    )
    assert_series_equal(df[OUT_COL], year_data["unterhaltsvors_m"], check_dtype=False)
