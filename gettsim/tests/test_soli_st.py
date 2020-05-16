from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.pre_processing.piecewise_functions import piecewise_polynomial
from gettsim.pre_processing.policy_for_date import get_policies_for_date

INPUT_COLS = ["p_id", "hh_id", "tu_id", "solibasis"]

YEARS = [1991, 1993, 1996, 1999, 2003, 2022]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_soli.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_soli_st(
    input_data, year,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date, groups="soli_st"
    )

    df["soli"] = df["solibasis"].apply(
        piecewise_polynomial,
        args=(
            params_dict["soli_st"]["soli_st"]["lower_thresholds"],
            params_dict["soli_st"]["soli_st"]["upper_thresholds"],
            params_dict["soli_st"]["soli_st"]["rates"],
            params_dict["soli_st"]["soli_st"]["intercepts_at_lower_thresholds"],
        ),
    )
    assert_series_equal(
        df["soli"], year_data["soli"], check_dtype=False, check_names=False
    )
