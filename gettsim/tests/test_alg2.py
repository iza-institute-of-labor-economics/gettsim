PIECEWISE_LIN_FUNCS = ["e_anr_frei", "e_anr_frei_kinder"]

import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.arbeitsl_geld_2 import alg2, regrouped_ein_anr_frei
from gettsim.config import ROOT_DIR
from gettsim.pre_processing.policy_for_date import get_policies_for_date

import yaml

from gettsim.pre_processing.policy_for_date import load_regrouped_data, process_data

from gettsim.pre_processing.generic_functions import get_piecewise_parameters
from gettsim.pre_processing.piecewise_functions import piecewise_linear

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
    "mehrbed",
    "regelbedarf_m",
    "regelsatz_m",
    "kost_unterk_m",
    "unterhaltsvors_m_hh",
    "eink_anrechn_frei",
]


YEARS = [2005, 2006, 2009, 2011, 2013, 2016, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_alg2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_alg2(input_data, arbeitsl_geld_2_raw_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()

    arbeitsl_geld_2_params = get_policies_for_date(
        year=year, group="arbeitsl_geld_2", raw_group_data=arbeitsl_geld_2_raw_data
    )

    df = df.reindex(columns=df.columns.tolist() + OUT_COLS)
    df = df.groupby("hh_id", group_keys=False).apply(
        alg2, params=arbeitsl_geld_2_params
    )
    assert_series_equal(df[column], year_data[column], check_dtype=False)


@pytest.mark.parametrize("year", YEARS)
def test_regrouped_alg2(input_data, arbeitsl_geld_2_raw_data, year):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()

    arbeitsl_geld_2_params = get_policies_for_date(
        year=year, group="arbeitsl_geld_2", raw_group_data=arbeitsl_geld_2_raw_data
    )
    raw_group_data = yaml.safe_load(
        (ROOT_DIR / "data" / "arbeitsl_geld_2_neu.yaml").read_text()
    )
    arbeitsl_geld_2_params_neu = process_data(
        arbeitsl_geld_2_params["datum"],
        group="arbeitsl_geld_2_neu",
        raw_group_data=raw_group_data,
    )
    arbeitsl_geld_2_params_neu["a2we"] = arbeitsl_geld_2_params["a2we"]
    arbeitsl_geld_2_params_neu["a2ve"] = arbeitsl_geld_2_params["a2ve"]

    df = df.reindex(columns=df.columns.tolist() + OUT_COLS)

    df1 = df.groupby("hh_id", group_keys=False).apply(
        alg2, params=arbeitsl_geld_2_params
    )
    df2 = df.groupby("hh_id", group_keys=False).apply(
        regrouped_ein_anr_frei, params=arbeitsl_geld_2_params_neu
    )
    assert_series_equal(
        df1["eink_anrechn_frei"], df2["eink_anrechn_frei"], check_dtype=False
    )
