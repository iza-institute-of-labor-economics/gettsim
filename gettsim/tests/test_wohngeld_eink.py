import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment


# Variables for the standard wohngeld test.
INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "kind",
    "kindergeld_anspruch",
    "bruttokaltmiete_m_hh",
    "heizkost_m",
    "alleinerz",
    "alter",
    "immobilie_baujahr_hh",
    "mietstufe",
    "bruttolohn_m",
    "unterhaltsvors_m",
    "jahr",
    "wohngeld_arbeitendes_kind",
    "behinderungsgrad",
    "eink_selbst_tu",
    "kapitaleink_brutto_tu",
    "eink_vermietung_tu",
    "arbeitsl_geld_m_tu",
    "sonstig_eink_m_tu",
    "eink_rente_zu_verst_m_tu",
    "elterngeld_m_tu",
]
YEARS_TEST = [2021]

OUT_COLS = ["wohngeld_eink_m"]

OVERRIDE_COLS = [
    "arbeitsl_geld_m_tu",
    "eink_rente_zu_verst_m_tu",
    "eink_selbst_tu",
    "eink_vermietung_tu",
    "elterngeld_m_tu",
    "kapitaleink_brutto_tu",
    "unterhaltsvors_m",
    "wohngeld_arbeitendes_kind",
    "kindergeld_anspruch",
]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(ROOT_DIR / "tests" / "test_data" / "wohngeld_eink.csv")


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

    assert_series_equal(result[column].astype(float), year_data[column])
