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
    "gr_bewertungszeiten",
    "wohnort_ost",
    "zu_verst_eink_excl_grundr_zuschlag_tu",
    "alter",
    "alleinstehend",
    "geburtsjahr",
    "bruttolohn_m",
    "entgeltpunkte",
    "zugangsfaktor",
    "rentner",
    "entgeltpunkte_grundrente",
    "kind",
]


YEARS = [2021]

OUT_COLS_ROUNDING = {
    "bonus_entgeltpunkte_grundr": 4,
    "grundr_zuschlag_vor_eink_anr": 0,
    "grundr_zuschlag_m": 0,
    "staatl_rente_m": 0,
}
OUT_COLS = OUT_COLS_ROUNDING.keys()


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
    functions = "gettsim.transfers.grundrente"

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=[policy_functions, functions],
        targets=column,
        columns_overriding_functions=[
            "zu_verst_eink_excl_grundr_zuschlag_tu",
            "zugangsfaktor",
        ],
    )
    rounding = OUT_COLS_ROUNDING[column]
    assert_series_equal(
        calc_result[column].round(rounding), year_data[column].round(rounding)
    )
