import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.kiz import kiz
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date


INPUT_COLS = [
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
    "w_hours",
    "m_wage",
    "ineducation",
    "miete",
    "heizkost",
    "alleinerz",
    "mehrbed",
    "adult_num_tu",
    "child_num_tu",
    "alg2_grossek_hh",
    "ar_alg2_ek_hh",
    "kindergeld_hh",
    "uhv",
    "year",
]
OUT_COLS = ["kiz_temp", "kiz_incrange"]
YEARS = [2006, 2009, 2011, 2013, 2016, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_kiz.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_kiz(input_data, tax_policy_data, year):
    columns = ["kiz_temp"]
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    tb = get_policies_for_date(year=year, tax_data_raw=tax_policy_data)
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hid").apply(kiz, tb=tb)
    assert_frame_equal(df[columns], year_data[columns], check_less_precise=True)
