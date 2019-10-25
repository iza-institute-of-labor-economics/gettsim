import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.unterhaltsvorschuss import uhv
from gettsim.tax_transfer import _apply_tax_transfer_func
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
out_col = "uhv"
years = [2017, 2019]


@pytest.mark.parametrize("year", years)
def test_apply_tax_transfer_func_on_uhv(year):
    file_name = "test_dfs_uhv.ods"
    df = load_test_data(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    df = _apply_tax_transfer_func(
        df,
        tax_func=uhv,
        level=["hid", "tu_id"],
        in_cols=input_cols,
        out_cols=[out_col],
        func_kwargs={"tb": tb},
    )
    expected = load_test_data(year, file_name, "uhv")
    assert_series_equal(df[out_col], expected, check_dtype=False)
