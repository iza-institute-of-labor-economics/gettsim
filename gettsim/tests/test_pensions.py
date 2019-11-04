import pandas as pd
import pytest
from numpy.testing import assert_array_almost_equal

from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.pensions import pensions
from gettsim.pensions import update_earnings_points
from gettsim.tax_transfer import _apply_tax_transfer_func
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data
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
tax_policy_data = load_tax_benefit_data()


@pytest.mark.parametrize("year", YEARS)
def test_pension(year):
    column = "pensions_sim"
    file_name = "test_dfs_pensions.csv"
    df = load_test_data(year, file_name, INPUT_COLUMNS)
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    if year > 2017:
        tb["calc_rentenwert"] = _rentenwert_from_2018
    else:
        tb["calc_rentenwert"] = _rentenwert_until_2017
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    expected = load_test_data(year, file_name, column)
    df = _apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLUMNS,
        out_cols=[column],
        func_kwargs={"tb": tb, "tb_pens": tb_pens},
    )
    assert_array_almost_equal(df[column], expected)


@pytest.mark.parametrize("year", YEARS)
def test_update_earning_points(year):
    file_name = "test_dfs_pensions.ods"
    df = load_test_data(year, file_name, INPUT_COLUMNS)
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    expected = load_test_data(year, file_name, "EP_end")
    df = _apply_tax_transfer_func(
        df,
        tax_func=update_earnings_points,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLUMNS,
        out_cols=[],
        func_kwargs={"tb": tb, "tb_pens": tb_pens[year]},
    )
    assert_array_almost_equal(df["EP"], expected.values)
