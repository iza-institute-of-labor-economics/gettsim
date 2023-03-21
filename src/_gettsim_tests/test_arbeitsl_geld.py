import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR
from _gettsim_tests._policy_test_utils import load_policy_test_data, PolicyTestData, cached_set_up_policy_environment

INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "bruttolohn_vorj_m",
    "wohnort_ost",
    "kind",
    "arbeitsstunden_w",
    "alter",
    "geburtsjahr",
    "jahr",
    "anwartschaftszeit",
    "arbeitssuchend",
    "m_durchg_alg1_bezug",
    "soz_vers_pflicht_5j",
]
YEARS = [2010, 2011, 2015, 2019]

data = load_policy_test_data("arbeitsl_geld")

@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=lambda x: str(x),
)
def test_arbeitsl_geld_new(
    test_data: PolicyTestData,
    column: str,
):
    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(date=test_data.date)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
    )

    # to prevent errors from rounding, allow deviations after the 3rd digit.
    assert_series_equal(
        result[column],
        test_data.output_df[column],
        atol=1e-2,
        rtol=0,
        check_dtype=False,
    )

@pytest.fixture(scope="module")
def input_data():
    file_name = "arbeitsl_geld.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
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
