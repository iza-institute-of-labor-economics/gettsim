import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.tests.auxiliary_test_tax import load_tb
from gettsim.tests.auxiliary_test_tax import load_test_data


input_cols = [
    "pid",
    "hid",
    "tu_id",
    "hh_korr",
    "hhsize",
    "child",
    "pensioner",
    "age",
    "hh_wealth",
    "adult_num",
    "child0_18_num",
    "kiz_temp",
    "wohngeld_basis_hh",
    "regelbedarf",
    "ar_base_alg2_ek",
    "year",
]

years = [2006, 2009, 2011, 2013, 2014, 2016, 2019]


@pytest.mark.parametrize("year", years)
def test_kiz(year):
    file_name = "test_dfs_prio.xlsx"
    columns = ["kiz", "m_alg2", "wohngeld"]
    df = load_test_data(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    calculated = pd.DataFrame(columns=columns)
    for hid in df["hid"].unique():
        calculated = calculated.append(
            benefit_priority(df[df["hid"] == hid], tb)[columns]
        )

    expected = load_test_data(year, file_name, columns)
    assert_frame_equal(calculated, expected, check_dtype=False)
