import pandas as pd
import pytest
from numpy.testing import assert_array_almost_equal

from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.pensions import pensions
from gettsim.pensions import update_earnings_points
from gettsim.tax_transfer import _apply_tax_transfer_func
from gettsim.tests.policy_for_date import get_policies_for_date


INPUT_COLS = [
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


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_pensions.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_pension(input_data, tax_policy_data, year):
    column = "pensions_sim"
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    if year > 2017:
        tb["calc_rentenwert"] = _rentenwert_from_2018
    else:
        tb["calc_rentenwert"] = _rentenwert_until_2017
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    df = _apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=[column],
        func_kwargs={"tb": tb, "tb_pens": tb_pens},
    )
    assert_array_almost_equal(df[column], year_data[column])


@pytest.mark.parametrize("year", YEARS)
def test_update_earning_points(input_data, tax_policy_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    df = _apply_tax_transfer_func(
        df,
        tax_func=update_earnings_points,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=[],
        func_kwargs={"tb": tb, "tb_pens": tb_pens[year]},
    )
    assert_array_almost_equal(df["EP"], year_data["EP_end"].values)
