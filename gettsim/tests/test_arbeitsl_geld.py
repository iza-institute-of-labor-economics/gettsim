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
    "arbeitsl_monate_lfdj",
    "arbeitsl_monate_vorj",
    "arbeitsl_monate_v2j",
    "sum_ges_rente_priv_rente_m",
    "arbeitsstunden_w",
    "alter",
    "jahr",
]
YEARS = [2010, 2011, 2015, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_ui.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_ui(
    input_data, year,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets="arbeitsl_geld_m",
        columns_overriding_functions=["sum_ges_rente_priv_rente_m"],
    )

    # to prevent errors from rounding, allow deviations after the 3rd digit.
    assert_series_equal(
        result["arbeitsl_geld_m"],
        year_data["arbeitsl_geld_m"],
        atol=1e-3,
        rtol=1,
        check_dtype=False,
    )
