import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "eink_st_mit_kinderfreib_tu",
    "abgelt_st_tu",
]

YEARS = [1991, 1993, 1996, 1999, 2003, 2022]


@pytest.fixture(scope="module")
def input_data():
    file_name = "soli_st.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_soli_st(
    input_data,
    year,
):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()

    policy_params, policy_functions = set_up_policy_environment(date=year)

    user_cols = ["eink_st_mit_kinderfreib_tu", "abgelt_st_tu"]
    results = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets="soli_st_tu",
        columns_overriding_functions=user_cols,
    )
    assert_series_equal(
        results["soli_st_tu"],
        year_data["soli_st_tu"],
        check_dtype=False,
        atol=1e-2,
        rtol=0,
    )
