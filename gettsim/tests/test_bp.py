import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.config import ROOT_DIR
from gettsim.tests.policy_for_date import get_policies_for_date


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
    "byear",
    "year",
]

years = [2006, 2009, 2011, 2013, 2014, 2016, 2019]
out_cols = ["kiz", "wohngeld", "m_alg2"]


@pytest.fixture
def input_data():
    file_name = "test_dfs_prio.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", years)
def test_kiz(input_data, tax_policy_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(benefit_priority, tb=tb)
    assert_frame_equal(df[out_cols], year_data[out_cols], check_dtype=False)
