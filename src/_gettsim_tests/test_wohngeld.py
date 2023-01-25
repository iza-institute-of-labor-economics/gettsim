import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

# Variables for the standard wohngeld test.
INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "bruttokaltmiete_m_hh",
    "alleinerz",
    "alter",
    "immobilie_baujahr_hh",
    "kindergeld_anspruch",
    "mietstufe",
    "bruttolohn_m",
    "sum_ges_rente_priv_rente_m",
    "rente_ertragsanteil",
    "elterngeld_m",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "unterhaltsvors_m",
    "eink_selbst_m",
    "eink_abhängig_beschäftigt",
    "kapitaleink_brutto",
    "eink_vermietung_m",
    "ges_rentenv_beitr_m",
    "ges_krankenv_beitr_m",
    "behinderungsgrad",
    "jahr",
    "eink_st_tu",
    "vermögen_bedürft_hh",
    "haushaltsgröße_hh",
]
YEARS_TEST = [2006, 2009, 2013, 2016, 2018, 2019, 2021, 2023]

# ToDo: add "wohngeld_miete_m_hh" "wohngeld_eink_m" to test data and to
# ToDo: OUT_COLS (take care of rounding)

OUT_COLS = ["wohngeld_vor_vermög_check_m_hh", "wohngeld_nach_vermög_check_m_hh"]

OVERRIDE_COLS = [
    "elterngeld_m",
    "arbeitsl_geld_m",
    "unterhaltsvors_m",
    "rente_ertragsanteil",
    "eink_abhängig_beschäftigt",
    "eink_st_tu",
    "ges_krankenv_beitr_m",
    "ges_rentenv_beitr_m",
    "kindergeld_anspruch",
    "sum_ges_rente_priv_rente_m",
    "kapitaleink_brutto",
    "haushaltsgröße_hh",
]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(TEST_DATA_DIR / "wohngeld.csv")


@pytest.mark.parametrize("year, column", itertools.product(YEARS_TEST, OUT_COLS))
def test_wohngeld(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=OVERRIDE_COLS,
    )
    if column == "wohngeld_eink_m":
        result[column] = result[column].round(1)
    else:
        result[column] = result[column].round(2)

    assert_series_equal(result[column].astype(float), year_data[column], atol=0, rtol=0)
