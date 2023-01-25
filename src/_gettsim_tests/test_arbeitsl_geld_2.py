"""
Note:
- Values for "arbeitsl_geld_2_vor_vorrang_m_hh" and "arbeitsl_geld_2_m_hh" are
  only regression tests
- "wohngeld_vor_vermög_check_m_hh" is set to 0 to avoid testing Wohngeld-Vorrang and the
  calculation of Wohngeld here.

"""
import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "alter",
    "bruttokaltmiete_m_hh",
    "heizkosten_m_hh",
    "wohnfläche_hh",
    "bewohnt_eigentum_hh",
    "alleinerz",
    "bruttolohn_m",
    "sum_ges_rente_priv_rente_m",
    "kapitaleink_brutto_m",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "eink_selbst_m",
    "eink_vermietung_m",
    "eink_st_tu",
    "soli_st_tu",
    "sozialv_beitr_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "jahr",
    "wohngeld_vor_vermög_check_m_hh",
    "vermögen_bedürft_hh",
    "geburtsjahr",
    "rentner",
    "in_ausbildung",
    "arbeitsstunden_w",
    "bürgerg_bezug_vorj",
]

OUT_COLS = [
    # "arbeitsl_geld_2_bruttoeink_m",
    # "arbeitsl_geld_2_eink_anr_frei_m",
    "arbeitsl_geld_2_eink_m",
    # "_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh",
    "arbeitsl_geld_2_regelsatz_m_hh",
    "arbeitsl_geld_2_kost_unterk_m_hh",
    # "unterhaltsvors_m_hh",
    # "arbeitsl_geld_2_vor_vorrang_m_hh",
    "arbeitsl_geld_2_m_hh",
]

OVERRIDE_COLS = [
    "arbeitsl_geld_m",
    "soli_st_tu",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "eink_st_tu",
    "sozialv_beitr_m",
    "sum_ges_rente_priv_rente_m",
    "wohngeld_vor_vermög_check_m_hh",
]


YEARS = [2005, 2006, 2009, 2013, 2018, 2019, 2022, 2023]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(TEST_DATA_DIR / "arbeitsl_geld_2.csv")


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_arbeitsl_geld_2(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=OVERRIDE_COLS,
    )
    if column in [
        "arbeitsl_geld_2_vor_vorrang_m_hh",
        "arbeitsl_geld_2_m_hh",
    ]:
        result = calc_result[column].round(2)
    else:
        result = calc_result[column]
    assert_series_equal(result, year_data[column], check_dtype=False, atol=1e-1, rtol=0)
