import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim import compute_taxes_and_transfers
from gettsim import set_up_policy_environment
from gettsim.config import ROOT_DIR


INPUT_COLS = [
    "p_id",
    "tu_id",
    "hh_id",
    "jahr",
    "kind",
    "alter",
    "bruttokaltmiete_m_hh",
    "heizkosten_m_hh",
    "wohnfläche_hh",
    "bruttolohn_m",
    "kapitaleink_brutto_m",
    "grundr_zeiten",
    "rentner",
    "schwerbeh_g",
    "vermögen_hh",
    "alleinerz",
    "bewohnt_eigentum_hh",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "eink_selbst_m",
    "vermiet_eink_m",
    "eink_st_tu",
    "soli_st_tu",
    "sozialv_beitr_gesamt_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "priv_rente_m",
    "ges_rente_m",
]

OVERRIDE_COLS = [
    "eink_st_tu",
    "soli_st_tu",
    "sozialv_beitr_gesamt_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "ges_rente_m",
    "arbeitsl_geld_m",
]

YEARS = [2017, 2018, 2020, 2021, 2022]

OUT_COLS = [
    "grunds_im_alter_m_hh",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_grunds_im_alter.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    out["p_id"] = out["p_id"].astype(int)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_grunds_im_alter(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=f"{year}-07-01")

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=OUT_COLS,
        columns_overriding_functions=OVERRIDE_COLS,
    )

    # Retype outcols to float (from int)
    expected = year_data[column].astype(float)
    assert_series_equal(calc_result[column], expected)
