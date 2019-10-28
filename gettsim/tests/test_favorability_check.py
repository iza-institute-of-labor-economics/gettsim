from itertools import product

import numpy as np
import pytest
from pandas.testing import assert_series_equal

from gettsim.taxes.favorability_check import favorability_check
from gettsim.tests.auxiliary_test_tax import load_test_data


input_cols = [
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
out_cols = ["incometax_tu", "incometax", "kindergeld", "kindergeld_hh", "kindergeld_tu"]
years = [2010, 2012, 2016]
columns = ["incometax_tu", "kindergeld", "kindergeld_hh", "kindergeld_tu"]
to_test = list(product(years, columns))


@pytest.mark.parametrize("year, column", to_test)
def test_favorability_check(year, column):
    file_name = "test_dfs_favorability_check.ods"
    df = load_test_data(year, file_name, input_cols, bool_cols=["zveranl", "child"])

    tb = {"zve_list": ["nokfb", "kfb"], "yr": year}
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(favorability_check, tb=tb)
    expected = load_test_data(year, file_name, column)
    assert_series_equal(df[column], expected, check_dtype=False)
