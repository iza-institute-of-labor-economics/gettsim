import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date


INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
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

YEARS = [2006, 2009, 2011, 2013, 2014, 2016, 2019]
OUT_COLS = ["kiz", "wohngeld", "m_alg2"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_prio.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_kiz(input_data, year, arbeitsl_geld_2_raw_data):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    arbeitsl_geld_2_data = get_policies_for_date(
        year=year, group="arbeitsl_geld_2", raw_group_data=arbeitsl_geld_2_raw_data
    )
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hid").apply(
        benefit_priority, arbeitsl_geld_2_data=arbeitsl_geld_2_data
    )
    assert_frame_equal(df[OUT_COLS], year_data[OUT_COLS], check_dtype=False)
