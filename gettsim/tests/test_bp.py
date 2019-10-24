import numpy as np
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
out_cols = ["kiz", "wohngeld", "m_alg2"]


@pytest.mark.parametrize("year", years)
def test_kiz(year):
    file_name = "test_dfs_prio.ods"
    df = load_test_data(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(benefit_priority, tb=tb)
    expected = load_test_data(year, file_name, out_cols)
    assert_frame_equal(df[out_cols], expected, check_dtype=False)
