import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from tests.auxiliary_test import load_tax_transfer_input_data as load_input
from tests.auxiliary_test import load_tax_transfer_output_data as load_output
from tests.auxiliary_test import load_tb
from src.analysis.tax_transfer_funcs.taxes import tax_sched, tarif
from src.model_code.imports import tarif_ubi


input_cols = [
    "pid",
    "hid",
    "tu_id",
    "child",
    "zve_nokfb",
    "zve_kfb",
    "zve_abg_kfb",
    "zve_abg_nokfb",
    "gross_e5",
    "zveranl",
    "gross_e5_tu",
]

years = [2009, 2012, 2015, 2018]


@pytest.mark.parametrize("year", years)
def test_tax_sched(year):
    file_name = "test_dfs_tax_sched.xlsx"
    columns = ["tax_nokfb", "tax_kfb", "tax_abg_nokfb", "tax_abg_kfb", "abgst"]
    df = load_input(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    calculated = pd.DataFrame(columns=columns)
    for tu_id in df["tu_id"].unique():
        calculated = calculated.append(
            tax_sched(df[df["tu_id"] == tu_id], tb, year, tarif)[columns]
        )
    expected = load_output(year, file_name, columns)
    assert_frame_equal(
        calculated, expected, check_dtype=False, check_exact=False, check_less_precise=0
    )
