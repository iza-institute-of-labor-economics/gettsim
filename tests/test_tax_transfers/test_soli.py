import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from tests.auxiliary_test import load_tax_transfer_input_data as load_input
from tests.auxiliary_test import load_tax_transfer_output_data as load_output
from tests.auxiliary_test import load_tb
from src.analysis.tax_transfer.taxes import soli


input_cols = [
    "pid",
    "hid",
    "tu_id",
    "zveranl",
    "tax_kfb_tu",
    "tax_abg_kfb_tu",
    "abgst_tu",
    "child",
    "incometax_tu",
]

years = [2003, 2012, 2016, 2018]


@pytest.mark.parametrize("year", years)
def test_soli(year):
    file_name = "test_dfs_soli.xlsx"
    columns = ["soli", "soli_tu"]
    df = load_input(year, file_name, input_cols)
    tb = load_tb(year)
    calculated = pd.DataFrame(columns=columns)
    for tu_id in df["tu_id"].unique():
        calculated = calculated.append(
            soli(df[df["tu_id"] == tu_id], tb, year)[columns]
        )
    expected = load_output(year, file_name, columns)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_frame_equal(calculated, expected)
