import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim import compute_taxes_and_transfers
from gettsim import set_up_policy_environment
from gettsim.config import ROOT_DIR


INPUT_COLS = [
    "grundrentenzeiten",
    "grundrentenbewertungszeiten",
    "wohnort_ost",
    "tu_id",
    "einkommen_grundr",
    "alter",
    "alleinstehend",
    "geburtsjahr",
    "bruttolohn_m",
    "entgeltpunkte",
    "zugangsfaktor",
    "rentner",
    "entgeltpunkte_grundrente",
]


YEARS = [2021]

OUT_COLS = [
    "grundrentenzuschlag_m",
    "staatl_rente_m",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_grundrente.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_grundrente(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=f"{year}-07-01")
    functions = "gettsim.grundrente.grundrente"

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=[policy_functions, functions],
        targets=column,
        columns_overriding_functions=["einkommen_grundr", "zugangsfaktor"],
    )
    assert_series_equal(calc_result[column].round(2), year_data[column])
