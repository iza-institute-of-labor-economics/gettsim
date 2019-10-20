import numpy as np
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
OUT_COL = "m_alg1"
years = [2010, 2011, 2015, 2019]


@pytest.mark.parametrize("year", years)
def test_ui(year):
    file_name = "test_dfs_ui.ods"
    df = load_test_data(year, file_name, input_cols, pd_kwargs={"true_values": "TRUE"})
    tb = load_tb(year)
    tb["yr"] = year
    tb["tax_schedule"] = tarif
    expected = load_test_data(year, file_name, OUT_COL)
    df[OUT_COL] = np.nan
    df = df.groupby(["hid", "tu_id", "pid"]).apply(ui, tb=tb)
    assert_series_equal(df[OUT_COL], expected, check_less_precise=3)
