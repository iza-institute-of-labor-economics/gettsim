import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "kaltmiete_m_hh",
    "alleinerziehend",
    "alter",
    "immobilie_baujahr_hh",
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
    "rentenv_beitr_m",
    "ges_krankenv_beitr_m",
    "behinderungsgrad",
    "jahr",
]
YEARS = [2006, 2009, 2013, 2016, 2018, 2019]
TEST_COLUMN = ["wohngeld_basis_hh"]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(ROOT_DIR / "tests" / "test_data" / "test_dfs_wg.csv")


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLUMN))
def test_wg(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    columns = [
        "elterngeld_m",
        "arbeitsl_geld_m",
        "unterhaltsvors_m",
        "_ertragsanteil",
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "brutto_eink_6",
        "ges_krankenv_beitr_m",
        "rentenv_beitr_m",
        "kindergeld_anspruch",
    ]
    policy_functions["eink_st_tu"] = eink_st_m_tu_from_data

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=columns,
    )
    assert_series_equal(result[column], year_data[column])


@pytest.fixture(scope="module")
def input_data_2():
    return pd.read_csv(ROOT_DIR / "tests" / "test_data" / "test_dfs_wg2.csv")


@pytest.mark.parametrize("year, column", itertools.product([2013], TEST_COLUMN))
def test_wg_no_mietstufe_in_input_data(input_data_2, year, column):
    year_data = input_data_2[input_data_2["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    columns = [
        "elterngeld_m",
        "arbeitsl_geld_m",
        "unterhaltsvors_m",
        "_ertragsanteil",
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "brutto_eink_6",
        "ges_krankenv_beitr_m",
        "rentenv_beitr_m",
        "kindergeld_anspruch",
    ]

    policy_functions["eink_st_tu"] = eink_st_m_tu_from_data

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=columns,
    )
    assert_series_equal(result[column], year_data[column])


def eink_st_m_tu_from_data(eink_st_m, tu_id):
    return eink_st_m.groupby(tu_id).sum()
