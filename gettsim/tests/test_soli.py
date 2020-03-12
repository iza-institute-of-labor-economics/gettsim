import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date

INPUT_COLS = ["p_id", "hh_id", "tu_id", "solibasis"]

YEARS = [1991, 1993, 1996, 1999, 2003, 2022]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_soli.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_tax_sched(
    input_data, year, soli_st_raw_data,
):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()

    soli_st_params = get_policies_for_date(
        year=year, group="soli_st", raw_group_data=soli_st_raw_data
    )

    df["soli"] = soli_st_params["soli_formula"](df["solibasis"], soli_st_params)
    assert_series_equal(
        df["soli"], year_data["soli"], check_dtype=False, check_names=False
    )
