import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim import compute_taxes_and_transfers
from gettsim import set_up_policy_environment
from gettsim.config import ROOT_DIR


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
    file_name = "renten_alter.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_renten_anspr(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=f"{year}-07-01")

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
    )
    assert_series_equal(calc_result[column], year_data[column], atol=1e-1, rtol=0)
