import pandas as pd
import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal
from src.analysis.tax_transfer_funcs.pensions import (
    pensions,
    update_earnings_points,
    calc_rentenwert_until_2017,
    calc_rentenwert_from_2018,
)
from bld.project_paths import project_paths_join as ppj

from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_input,
)
from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_tb,
)
from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_output,
)

input_cols = [
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


years = [2010, 2012, 2015]


@pytest.mark.parametrize("year", years)
def test_pension(year):
    column = "pensions_sim"
    df = load_input(year, "test_dfs_pensions.xlsx", input_cols)
    tb = load_tb(year)
    if year > 2017:
        tb["calc_rentenwert"] = calc_rentenwert_from_2018
    else:
        tb["calc_rentenwert"] = calc_rentenwert_until_2017
    tb_pens = pd.read_excel(ppj("IN_DATA", "pensions.xlsx")).set_index("var")
    expected = load_output(year, "test_dfs_pensions.xlsx", column)
    calculated = pd.Series(name=column)
    for pid in df["pid"].unique():
        calculated = np.append(
            calculated, pensions(df[df["pid"] == pid].iloc[0], tb, tb_pens)
        )
    assert_array_almost_equal(calculated, expected)


@pytest.mark.parametrize("year", years)
def test_update_earning_points(year):
    column = "EP_end"
    df = load_input(year, "test_dfs_pensions.xlsx", input_cols)
    tb = load_tb(year)
    tb_pens = pd.read_excel(ppj("IN_DATA", "pensions.xlsx")).set_index("var")
    expected = load_output(year, "test_dfs_pensions.xlsx", column)
    calculated = np.array([])
    for pid in df["pid"].unique():
        calculated = np.append(
            calculated,
            update_earnings_points(df[df["pid"] == pid].iloc[0], tb, tb_pens[year]),
        )
    assert_array_almost_equal(calculated, expected.values)
