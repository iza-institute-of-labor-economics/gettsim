import pytest
import pandas as pd
from pandas.testing import assert_series_equal
from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_input,
)
from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_output,
)
from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_tb,
)
from src.analysis.tax_transfer_funcs.benefits import uhv


input_cols = [
    "pid",
    "hid",
    "tu_id",
    "alleinerz",
    "age",
    "m_wage",
    "m_transfers",
    "m_kapinc",
    "m_vermiet",
    "m_self",
    "m_alg1",
    "m_pensions",
    "zveranl",
    "year",
]
years = [2017, 2019]


@pytest.mark.parametrize("year", years)
def test_uhv(year):
    file_name = "test_dfs_uhv.xlsx"
    df = load_input(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    calculated = pd.Series(name="uhv")
    for tu_id in df["tu_id"].unique():
        calculated = calculated.append(uhv(df[df["tu_id"] == tu_id], tb))
    expected = load_output(year, file_name, "uhv")
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_series_equal(calculated, expected, check_dtype=False)
