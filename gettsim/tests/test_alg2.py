import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.arbeitsl_geld_2 import alg2
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date

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
    "eink_st",
    "soli_st",
    "sozialv_beit_m",
    "kindergeld_hh",
    "unterhaltsvors_m",
    "elterngeld",
    "year",
]
OUT_COLS = [
    "sum_basis_arbeitsl_geld_2_eink",
    "sum_arbeitsl_geld_2_eink",
    "arbeitsl_geld_2_brutto_eink_hh",
    "mehrbed",
    "regelbedarf_m",
    "regelsatz_m",
    "kost_unterk_m",
    "unterhaltsvors_m_hh",
    "eink_anrech_frei",
]


YEARS = [2005, 2006, 2009, 2011, 2013, 2016, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_alg2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_alg2(input_data, arbeitsl_geld_2_raw_data, year, column):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()

    arbeitsl_geld_2_params = get_policies_for_date(
        year=year, group="arbeitsl_geld_2", raw_group_data=arbeitsl_geld_2_raw_data
    )

    df = df.reindex(columns=df.columns.tolist() + OUT_COLS)
    df = df.groupby("hh_id", group_keys=False).apply(
        alg2, params=arbeitsl_geld_2_params
    )

    assert_series_equal(df[column], year_data[column], check_dtype=False)
