import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_almost_equal

from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.pensions import pensions
from gettsim.pensions import update_earnings_points
from gettsim.tests.auxiliary_test_tax import load_tb
from gettsim.tests.auxiliary_test_tax import load_test_data

INPUT_COLUMNS = [
    "pid",
    "hid",
    "tu_id",
    "m_wage",
    "east",
    "age",
    "year",
    "byear",
    "exper",
    "EP",
]


YEARS = [2010, 2012, 2015]


@pytest.mark.parametrize("year", YEARS)
def test_pension(year):
    column = "pensions_sim"
    file_name = "test_dfs_pensions.ods"
    df = load_test_data(year, file_name, INPUT_COLUMNS)
    tb = load_tb(year)
    tb["yr"] = year
    if year > 2017:
        tb["calc_rentenwert"] = _rentenwert_from_2018
    else:
        tb["calc_rentenwert"] = _rentenwert_until_2017
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    expected = load_test_data(year, file_name, column)
    df[column] = np.nan
    df = df.groupby(["hid", "tu_id", "pid"]).apply(pensions, tb=tb, tb_pens=tb_pens)
    assert_array_almost_equal(df[column], expected)


@pytest.mark.parametrize("year", YEARS)
def test_update_earning_points(year):
    column = "EP_end"
    file_name = "test_dfs_pensions.ods"
    df = load_test_data(year, file_name, INPUT_COLUMNS)
    tb = load_tb(year)
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    expected = load_test_data(year, file_name, column)
    calculated = np.array([])
    for pid in df["pid"].unique():
        calculated = np.append(
            calculated,
            update_earnings_points(df[df["pid"] == pid].iloc[0], tb, tb_pens[year]),
        )
    assert_array_almost_equal(calculated, expected.values)
