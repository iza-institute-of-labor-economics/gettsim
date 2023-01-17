import itertools
import random

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from _gettsim_tests import TEST_DATA_DIR
from pandas.testing import assert_series_equal


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "alter",
    "jahr",
    "geburtsjahr",
    "geburtsmonat",
    "m_arbeitsunfähig",
    "m_krank_ab_16_bis_24",
    "m_mutterschutz",
    "m_arbeitslos",
    "m_ausbild_suche",
    "m_schul_ausbild",
    "m_alg1_übergang",
    "m_geringf_beschäft",
    "weiblich",
    "y_pflichtbeitr_ab_40",
    "m_pflichtbeitrag",
    "m_freiw_beitrag",
    "m_ersatzzeit",
    "m_kind_berücks_zeit",
    "m_pfleg_berücks_zeit",
]

OUT_COLS = [
    "_ges_rente_altersgrenze_abschlagsfrei",
]

YEARS = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]


@pytest.fixture(scope="module")
def input_data():
    # Original Data Source: Seibold, A. (2021).
    # Reference points for retirement behavior:
    # Evidence from german pension discontinuities.
    # American Economic Review, 111(4), 1126-65.

    # IDs were added to the original data
    # m_pflichtbeitrag is added as an identifier for pension kind
    # 60: Regelaltersrente, 420: Langjährig Versichert, 180: Altersrente für Frauen
    original_data = pd.read_csv(TEST_DATA_DIR / "renten_alter.csv")

    original_data.columns = original_data.columns.str.lower()

    # Rename variables to GETTSIM convention
    var_names = {
        "id": "p_id",
        "yob": "geburtsjahr",
        "mob": "geburtsmonat",
        "regsray": "Rentenalter_Jahr",
        "regsram": "Rentenalter_Monat",
        "m_pflichtbeitrag": "m_pflichtbeitrag",
    }
    out = original_data[[*var_names]].rename(columns=var_names).copy()

    # Create IDs
    out["tu_id"] = out["p_id"]
    out["hh_id"] = out["p_id"]

    # Create variables needed in GETTSIM
    out["weiblich"] = True
    out["jahr"] = random.choice(YEARS)
    out["alter"] = out["jahr"] - out["geburtsjahr"]
    out["m_arbeitsunfähig"] = 0
    out["m_krank_ab_16_bis_24"] = 0
    out["m_mutterschutz"] = 0
    out["m_arbeitslos"] = 0
    out["m_ausbild_suche"] = 0
    out["m_schul_ausbild"] = 0
    out["m_alg1_übergang"] = 0
    out["m_geringf_beschäft"] = 0
    out["m_freiw_beitrag"] = 0
    out["m_ersatzzeit"] = 0
    out["m_kind_berücks_zeit"] = 0
    out["m_pfleg_berücks_zeit"] = 0
    out["_ges_rente_altersgrenze_abschlagsfrei"] = out["Rentenalter_Jahr"] + out[
        "Rentenalter_Monat"
    ] * (1 / 12)
    out.loc[out["m_pflichtbeitrag"] == 180, "y_pflichtbeitr_ab_40"] = 10
    out.loc[out["m_pflichtbeitrag"] != 180, "y_pflichtbeitr_ab_40"] = 0

    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_renten_anspr(input_data, year, column):
    year_data = input_data.reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=f"{year}-07-01")

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
    )
    assert_series_equal(calc_result[column], year_data[column], atol=1e-1, rtol=0)
