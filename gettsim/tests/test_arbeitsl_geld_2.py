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
    "vorstand_tu",
    "kind",
    "alter",
    "kaltmiete_m",
    "heizkost_m",
    "wohnfläche",
    "bewohnt_eigentum",
    "alleinerziehend",
    "bruttolohn_m",
    "ges_rente_m",
    "kapital_eink_m",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "eink_selbstst_m",
    "vermiet_eink_m",
    "eink_st_m",
    "soli_st_m",
    "sozialv_beit_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "jahr",
]
OUT_COLS = [
    "sum_basis_arbeitsl_geld_2_eink",
    "sum_arbeitsl_geld_2_eink",
    "arbeitsl_geld_2_brutto_eink_hh",
    "alleinerziehenden_mehrbedarf",
    "regelbedarf_m",
    "regelsatz_m",
    "kost_unterk_m",
    "unterhaltsvors_m_hh",
    "eink_anrechn_frei",
    "arbeitsl_geld_2_eink",
    "sum_arbeitsl_geld_2_eink_hh",
]


YEARS = [2005, 2006, 2009, 2011, 2013, 2016, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_alg2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_alg2(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date, groups="arbeitsl_geld_2",
    )
    columns = [
        "arbeitsl_geld_m",
        "soli_st_m",
        "kindergeld_m_hh",
        "unterhaltsvors_m",
        "elterngeld_m",
    ]

    result = compute_taxes_and_transfers(
        df, user_columns=columns, targets=column, params=params_dict
    )

    assert_series_equal(result, year_data[column], check_dtype=False)
