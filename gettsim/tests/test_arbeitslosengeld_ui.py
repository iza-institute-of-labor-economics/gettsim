import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.arbeitslosengeld import ui
from gettsim.taxes.calc_taxes import tarif
from gettsim.tests.auxiliary_test_tax import load_tb
from gettsim.tests.auxiliary_test_tax import load_test_data

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
    file_name = "test_dfs_ui.ods"
    df = load_test_data(year, file_name, input_cols, pd_kwargs={"true_values": "TRUE"})
    tb = load_tb(year)
    tb["yr"] = year
    tb["tax_schedule"] = tarif
    expected = load_test_data(year, file_name, "m_alg1")
    calculated = pd.Series(name="m_alg1", index=df.index)
    for i in df.index:
        calculated[i] = ui(df.loc[i], tb)
    assert_series_equal(calculated, expected, check_less_precise=3)
