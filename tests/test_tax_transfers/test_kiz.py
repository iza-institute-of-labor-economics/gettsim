import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from tests.auxiliary_test import load_tax_transfer_input_data as load_input
from tests.auxiliary_test import load_tax_transfer_output_data as load_output
from tests.auxiliary_test import load_tb
from src.analysis.tax_transfer_funcs.benefits import kiz


input_cols = [
    "pid",
    "hid",
    "tu_id",
    "head",
    "hhtyp",
    "hh_korr",
    "hhsize",
    "child",
    "pensioner",
    "age",
    "miete",
    "heizkost",
    "alleinerz",
    "mehrbed",
    "adult_num_tu",
    "child_num_tu",
    "alg2_grossek_hh",
    "ar_alg2_ek_hh",
    "wohngeld_basis_hh",
    "regelbedarf",
    "ar_base_alg2_ek",
    "kindergeld_hh",
    "uhv",
    "year",
]

years = [2006, 2009, 2011, 2013, 2016, 2019]


@pytest.mark.parametrize("year", years)
def test_kiz(year):
    file_name = "test_dfs_kiz.xlsx"
    columns = ["kiz", "m_alg2", "wohngeld"]
    df = load_input(year, file_name, input_cols)
    tb = load_tb(year)
    calculated = pd.DataFrame(columns=columns)
    for hid in df["hid"].unique():
        calculated = calculated.append(
            kiz(df[df["hid"] == hid], tb, year, False)[columns]
        )
    expected = load_output(year, file_name, columns)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_frame_equal(calculated, expected, check_dtype=False)
