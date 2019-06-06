import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from tests.auxiliary_test import load_tax_transfer_input_data as load_input
from tests.auxiliary_test import load_tax_transfer_output_data as load_output
from tests.auxiliary_test import load_tb
from src.analysis.tax_transfer_funcs.benefits import (
    alg2,
    regelberechnung_until_2010,
    regelberechnung_2011_and_beyond,
)

input_cols = [
    "pid",
    "hid",
    "tu_id",
    "head_tu",
    "child",
    "age",
    "miete",
    "heizkost",
    "wohnfl",
    "eigentum",
    "alleinerz",
    "m_wage",
    "m_pensions",
    "m_kapinc",
    "m_alg1",
    "m_transfers",
    "m_self",
    "m_vermiet",
    "incometax",
    "soli",
    "svbeit",
    "kindergeld_hh",
    "uhv",
    "divdy",
    "year",
]


years = [2006, 2009, 2011, 2013, 2016, 2019]


@pytest.mark.parametrize("year", years)
def test_alg2(year):
    file_name = "test_dfs_alg2.xlsx"
    columns = ["ar_base_alg2_ek", "ar_alg2_ek_hh", "regelbedarf"]
    df = load_input(year, file_name, input_cols)
    tb = load_tb(year)
    if year <= 2010:
        tb["calc_regelsatz"] = regelberechnung_until_2010
    else:
        tb["calc_regelsatz"] = regelberechnung_2011_and_beyond
    calculated = pd.DataFrame(columns=columns)
    for hid in df["hid"].unique():
        calculated = calculated.append(alg2(df[df["hid"] == hid], tb, year)[columns])
    expected = load_output(year, file_name, columns)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_frame_equal(calculated, expected)
