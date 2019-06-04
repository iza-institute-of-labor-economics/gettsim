import pandas as pd
from itertools import product
import pytest
from pandas.testing import assert_series_equal
from src.analysis.tax_transfer_funcs.social_insurance import soc_ins_contrib
from tests.auxiliary_test import load_tax_transfer_input_data as load_input
from tests.auxiliary_test import load_tb
from tests.auxiliary_test import load_tax_transfer_output_data as load_output

input_cols = [
    "pid",
    "hid",
    "tu_id",
    "m_wage",
    "east",
    "age",
    "selfemployed",
    "haskids",
    "m_self",
    "m_pensions",
    "pkv",
    "year",
]


years = [2010, 2018]
columns = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]
to_test = list(product(years, columns))


@pytest.mark.parametrize("year, column", to_test)
def test_soc_ins_contrib(year, column):
    df = load_input(year, "test_dfs_ssc.xlsx", input_cols)
    tb = load_tb(year)
    expected = load_output(year, "test_dfs_ssc.xlsx", column)
    calculated = pd.Series(name=column)
    for pid in df["pid"].unique():
        calculated = calculated.append(
            soc_ins_contrib(df[df["pid"] == pid], tb, year)[column]
        )
    assert_series_equal(calculated, expected)
