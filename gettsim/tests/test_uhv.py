import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.unterhaltsvorschuss import uhv
from gettsim.tests.auxiliary_test_tax import load_tb
from gettsim.tests.auxiliary_test_tax import load_test_data


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
    file_name = "test_dfs_uhv.ods"
    df = load_test_data(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    calculated = pd.Series(name="uhv")
    for tu_id in df["tu_id"].unique():
        calculated = calculated.append(uhv(df[df["tu_id"] == tu_id], tb))
    expected = load_test_data(year, file_name, "uhv")
    assert_series_equal(calculated, expected, check_dtype=False)
