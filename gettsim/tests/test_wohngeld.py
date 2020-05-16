import itertools
from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date


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
    "kindergeld_anspruch",
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
    "ges_krankenv_beit_m",
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


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLUMN))
def test_wg(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date, groups="wohngeld"
    )
    columns = ["elterngeld_m", "arbeitsl_geld_m", "unterhaltsvors_m"]
    result = compute_taxes_and_transfers(
        df, user_columns=columns, targets=column, params=params_dict
    )
    assert_series_equal(result, year_data[column])


@pytest.fixture(scope="module")
def input_data_2():
    file_name = "test_dfs_wg2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product([2013], TEST_COLUMN))
def test_wg_no_mietstufe_in_input_data(input_data_2, year, column):
    year_data = input_data_2[input_data_2["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date, groups="wohngeld"
    )
    columns = ["elterngeld_m", "arbeitsl_geld_m", "unterhaltsvors_m"]

    result = compute_taxes_and_transfers(
        df, user_columns=columns, targets=column, params=params_dict
    )
    assert_series_equal(result, year_data[column])
