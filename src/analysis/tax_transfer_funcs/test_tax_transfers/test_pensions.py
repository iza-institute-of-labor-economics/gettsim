import pandas as pd
import pytest
from pandas.testing import assert_series_equal
from src.analysis.tax_transfer_funcs.pensions import pensions
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
    tb_pens = pd.read_excel(ppj("IN_DATA", "pensions.xlsx")).set_index("var")
    expected = load_output(year, "test_dfs_pensions.xlsx", column)
    calculated = pd.Series(name=column)
    for pid in df["pid"].unique():
        calculated = calculated.append(
            pensions(df[df["pid"] == pid], tb, tb_pens, year)
        )
    assert_series_equal(calculated, expected)
