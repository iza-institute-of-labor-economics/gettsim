"""
Test the Zugangsfaktor for Erwerbsminderungsrente
(pension for reduced earning capacity)

"""
import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR
from _gettsim_tests._helpers import cached_set_up_policy_environment

INPUT_COLS = [
    "p_id",
    "jahr_renteneintr",
    "geburtsjahr",
]

OUT_COLS = [
    "erwerbsm_rente_zugangsfaktor",
]

YEARS = [2020]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_erwerbsm_rente_zugangsfaktor.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_erwerbsm_rente_zugangsfaktor(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=f"{year}-01-01"
    )

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
    )
    assert_series_equal(calc_result[column], year_data[column], atol=1e-1, rtol=0)
