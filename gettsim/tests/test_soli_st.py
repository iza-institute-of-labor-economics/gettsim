from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.tests.auxiliary import select_input_by_level
from gettsim.tests.auxiliary import select_output_by_level

INPUT_COLS = ["p_id", "hh_id", "tu_id", "kind", "_st_kind_freib_tu", "abgelt_st_tu"]

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
        policy_date=policy_date, groups="soli_st",
    )
    data = dict(df)
    for column_name, data_series in data.items():
        data[column_name] = select_input_by_level(
            data_series, data["tu_id"], data["hh_id"]
        )

    user_cols = ["_st_kind_freib_tu", "abgelt_st_tu"]
    results = compute_taxes_and_transfers(
        data, user_columns=user_cols, targets="soli_st_tu", params=params_dict
    )
    expected_result = select_output_by_level("soli_st_tu", year_data)

    assert_series_equal(
        results, expected_result, check_dtype=False, check_names=False,
    )
