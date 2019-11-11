from itertools import product

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.favorability_check import favorability_check


INPUT_COLS = [
    "hid",
    "tu_id",
    "pid",
    "zveranl",
    "child",
    "tax_nokfb_tu",
    "tax_kfb_tu",
    "abgst_tu",
    "kindergeld_basis",
    "kindergeld_tu_basis",
    "year",
]
OUT_COLS = ["incometax_tu", "incometax", "kindergeld", "kindergeld_hh", "kindergeld_tu"]
YEARS = [2010, 2012, 2016]
TEST_COLUMNS = ["incometax_tu", "kindergeld", "kindergeld_hh", "kindergeld_tu"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_favorability_check.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", product(YEARS, TEST_COLUMNS))
def test_favorability_check(input_data, tax_policy_data, year, column):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    tb = get_policies_for_date(year=year, tax_data_raw=tax_policy_data)
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(favorability_check, tb=tb)
    assert_series_equal(df[column], year_data[column])
