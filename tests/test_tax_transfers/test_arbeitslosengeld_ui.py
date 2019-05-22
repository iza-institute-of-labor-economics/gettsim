import pytest
import pandas as pd
from pandas.testing import assert_series_equal
from tests.auxiliary_test import load_tax_transfer_input_data as load_input
from tests.auxiliary_test import load_tax_transfer_output_data as load_output
from tests.auxiliary_test import load_tb
from src.analysis.tax_transfer import ui

input_cols = [
    "pid",
    "hid",
    "tu_id",
    "m_wage_l1",
    "east",
    "child",
    "months_ue",
    "months_ue_l1",
    "months_ue_l2",
    "alg_soep",
    "m_pensions",
    "w_hours",
    "child_num_tu",
    "age",
    "year",
]

years = [2010, 2011, 2015, 2019]


@pytest.mark.parametrize("year", years)
def test_ui(year):
    file_name = "test_dfs_ui.xlsx"
    df = load_input(year, file_name, input_cols, pd_kwargs={'true_values': "TRUE"})
    tb = load_tb(year)
    tb["yr"] = year
    expected = load_output(year, file_name, "m_alg1")
    calculated = pd.Series(name="m_alg1")
    for pid in df.index:
        calculated = calculated.append(ui(df.loc[[pid]], tb, year))
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_series_equal(calculated, expected, check_less_precise=3)