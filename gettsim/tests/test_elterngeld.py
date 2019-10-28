from pandas.testing import assert_series_equal

from gettsim.benefits.elterngeld import elt_geld
from gettsim.tests.auxiliary_test_tax import load_test_data

input_cols = [
    "hid",
    "pid",
    "m_wage",
    "elt_zeit"
    "year",
]

bool_cols = ["elt_zeit"]

def test_eltgeld():
    file_name = "test_df_eltg.xlsx"
    df = load_test_data(file_name, input_cols)
    calculated = elt_geld(df)
    expected = load_test_data(file_name, input_cols)["elt_geld"]
    assert_series_equal(calculated, expected, check_dtype=False)