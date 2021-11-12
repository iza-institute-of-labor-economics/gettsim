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
    "kaltmiete_m_hh",
    "heizkosten_m_hh",
    "wohnfläche_hh",
    "bruttolohn_m",
    "kapital_eink_m",
    "grundrentenzeiten",
    "rentner",
    "vermögen_hh",
    "alleinerziehend",
    "bewohnt_eigentum_hh",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "eink_selbst_m",
    "vermiet_eink_m",
    "eink_st_tu",
    "soli_st_tu",
    "sozialv_beitr_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "prv_rente_m",
    "staatl_rente_m",
]

OVERRIDE_COLS = [
    "eink_st_tu",
    "soli_st_tu",
    "sozialv_beitr_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "staatl_rente_m",
    "arbeitsl_geld_m",
]

YEARS = [2021]

OUT_COLS = [
    "regelbedarf_m_grunds_ia_vermögens_check_hh",
    "grunds_im_alter_m_hh",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_grunds_im_alter.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    out["p_id"] = out["p_id"].astype(int)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_grundrente(input_data, year, column):
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
