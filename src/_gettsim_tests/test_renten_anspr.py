"""Test the updating of Entgeltpunkte and the pension income based on Entgeltpunkte.

These are "only" regression tests.

"""
import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests import TEST_DATA_DIR
from _gettsim_tests._helpers import cached_set_up_policy_environment

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_m",
    "wohnort_ost",
    "alter",
    "jahr",
    "geburtsjahr",
    "entgeltp",
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
    "entgeltp_update",
    "entgeltp_update_lohn",
    "_ges_rente_altersgrenze_abschlagsfrei",
    # "_ges_rentenv_beitr_bemess_grenze_m",
]

YEARS = [2010, 2012, 2015, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "renten_anspr.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_renten_anspr(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = cached_set_up_policy_environment(date=f"{year}-07-01")

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
    )
    assert_series_equal(calc_result[column], year_data[column], atol=1e-1, rtol=0)
