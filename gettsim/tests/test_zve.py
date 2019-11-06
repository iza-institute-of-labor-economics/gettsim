import itertools

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.zve import zve


IN_COLS = [
    "pid",
    "hid",
    "tu_id",
    "m_wage",
    "m_self",
    "m_kapinc",
    "m_vermiet",
    "renteneintritt",
    "m_pensions",
    "w_hours",
    "ineducation",
    "zveranl",
    "child",
    "m_childcare",
    "handcap_degree",
    "rvbeit",
    "avbeit",
    "pvbeit",
    "alleinerz",
    "age",
    "child_num_tu",
    "year",
    "east",
    "gkvbeit",
]
OUT_COLS = [
    "zve_nokfb",
    "zve_abg_nokfb",
    "zve_kfb",
    "zve_abg_kfb",
    "kifreib",
    "gross_e1",
    "gross_e4",
    "gross_e5",
    "gross_e6",
    "gross_e7",
    "gross_e1_tu",
    "gross_e4_tu",
    "gross_e5_tu",
    "gross_e6_tu",
    "gross_e7_tu",
    "ertragsanteil",
    "sonder",
    "hhfreib",
    "altfreib",
    "vorsorge",
]

TEST_COLS = ["zve_nokfb", "zve_kfb"]
YEARS = [2005, 2009, 2010, 2012, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_zve.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLS))
def test_zve(input_data, tax_policy_data, year, column):
    year_data = input_data[input_data["year"] == year]
    df = year_data[IN_COLS].copy()
    tb = get_policies_for_date(year=year, tax_data_raw=tax_policy_data)
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(zve, tb=tb)

    # TODO: We need to adress this comment. This can't be our last word!
    # allow 1€ difference, caused by strange rounding issues.
    assert_series_equal(df[column], year_data[column], check_less_precise=2)
