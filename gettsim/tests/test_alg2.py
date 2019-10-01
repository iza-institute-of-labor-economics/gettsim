import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.alg2 import alg2
from gettsim.tests.auxiliary_test_tax import (
    load_input,
)
from gettsim.tests.auxiliary_test_tax import (
    load_output,
)
from gettsim.tests.auxiliary_test_tax import (
    load_tb,
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
    "year",
]


years = [2006, 2009, 2011, 2013, 2016, 2019]


@pytest.mark.parametrize("year", years)
def test_alg2(year):
    file_name = "test_dfs_alg2.xlsx"
    columns = ["ar_base_alg2_ek", "ar_alg2_ek_hh", "regelbedarf"]
    df = load_input(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    # if year <= 2010:
    #     tb["calc_regelsatz"] = regelberechnung_until_2010
    # else:
    #     tb["calc_regelsatz"] = regelberechnung_2011_and_beyond
    calculated = pd.DataFrame(columns=columns)
    for hid in df["hid"].unique():
        calculated = calculated.append(alg2(df[df["hid"] == hid], tb)[columns])
    expected = load_output(year, file_name, columns)
    assert_frame_equal(calculated, expected)
