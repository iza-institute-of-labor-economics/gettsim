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
    "grundrentenzeiten",
    "g_r_bewertungsreiten",
    "wohnort_ost",
    "eink_excl_grundr_zuschlag_m_tu",
    "alter",
    "alleinstehend",
    "geburtsjahr",
    "bruttolohn_m",
    "entgeltpunkte",
    "zugangsfaktor",
    "rentner",
    "entgeltp_grundr",
    "kind",
]


YEARS = [2021]

OUT_COLS_TOL = {
    "grundr_zuschlag_bonus_entgeltp": 0.0001,
    "grundr_zuschlag_vor_eink_anr_m": 1,
    "grundr_zuschlag_m": 1,
    "ges_rente_m": 1,
}
OUT_COLS = OUT_COLS_TOL.keys()


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_grundrente.csv"
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
        targets=column,
        columns_overriding_functions=[
            "eink_excl_grundr_zuschlag_m_tu",
            "zugangsfaktor",
        ],
    )
    tol = OUT_COLS_TOL[column]
    assert_series_equal(calc_result[column], year_data[column], atol=tol)
