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
    "alter",
    "kaltmiete_m_hh",
    "heizkosten_m_hh",
    "wohnfläche_hh",
    "bewohnt_eigentum_hh",
    "alleinerziehend",
    "bruttolohn_m",
    "ges_rente_m",
    "kapital_eink_m",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "eink_selbst_m",
    "vermiet_eink_m",
    "eink_st_tu",
    "soli_st_tu",
    "sozialv_beitr_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "jahr",
]

OUT_COLS = [
    "_arbeitsl_geld_2_brutto_eink_hh",
    "alleinerziehenden_mehrbedarf_hh",
    "regelbedarf_m_hh",
    "regelsatz_m_hh",
    "kost_unterk_m_hh",
    "unterhaltsvors_m_hh",
    "eink_anr_frei",
    "arbeitsl_geld_2_eink",
    "arbeitsl_geld_2_eink_hh",
]


YEARS = [2005, 2006, 2009, 2011, 2013, 2016, 2019]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(ROOT_DIR / "tests" / "test_data" / "test_dfs_alg2.csv")


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_alg2(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    columns = [
        "arbeitsl_geld_m",
        "soli_st_tu",
        "kindergeld_m_hh",
        "unterhaltsvors_m",
        "elterngeld_m",
        "eink_st_tu",
        "sozialv_beitr_m",
    ]

    result = compute_taxes_and_transfers(
        df,
        policy_params,
        policy_functions,
        targets=column,
        columns_overriding_functions=columns,
    )
    assert_series_equal(result[column], year_data[column], check_dtype=False)
