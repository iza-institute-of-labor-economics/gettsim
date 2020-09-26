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
    "bruttolohn_m",
    "wohnort_ost",
    "alter",
    "jahr",
    "geburtsjahr",
    "entgeltpunkte",
]


YEARS = [2010, 2012, 2015]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_pensions.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_pension(input_data, year, renten_daten):
    column = "rente_anspr_m"
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    policy_params["renten_daten"] = renten_daten

    calc_result = compute_taxes_and_transfers(
        data=df, params=policy_params, functions=policy_functions, targets=column,
    )
    assert_series_equal(calc_result[column].round(2), year_data[column])


@pytest.mark.parametrize("year", YEARS)
def test_update_earning_points(input_data, renten_daten, year):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()

    policy_params, policy_functions = set_up_policy_environment(date=year)

    policy_params["renten_daten"] = renten_daten

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets="entgeltpunkte_update",
    )
    assert_series_equal(
        calc_result["entgeltpunkte_update"], year_data["EP_end"], check_names=False
    )
