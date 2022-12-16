import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_vorj_m",
    "wohnort_ost",
    "kind",
    "anwartschaftszeit",
    "arbeitssuchend",
    "soz_vers_pflicht_5j",
    "arbeitsl_geld_bezug_m",
    "arbeitsstunden_w",
    "alter",
    "geburtsjahr",
    "jahr",
]
YEARS = [2010, 2011, 2015, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "arbeitsl_geld.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_arbeitsl_geld(
    input_data,
    year,
):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets="arbeitsl_geld_m",
    )

    # to prevent errors from rounding, allow deviations after the 3rd digit.
    assert_series_equal(
        result["arbeitsl_geld_m"],
        year_data["arbeitsl_geld_m"],
        atol=1e-2,
        rtol=0,
        check_dtype=False,
    )
