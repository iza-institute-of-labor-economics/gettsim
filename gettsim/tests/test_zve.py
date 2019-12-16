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

TEST_COLS = ["zve_nokfb", "zve_kfb", "vorsorge"]
YEARS = [2005, 2009, 2010, 2012, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_zve.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLS))
def test_zve(
    input_data,
    year,
    column,
    kindergeld_raw_data,
    soz_vers_beitr_raw_data,
    e_st_abzuege_raw_data,
):
    year_data = input_data[input_data["year"] == year]
    df = year_data[IN_COLS].copy()
    e_st_abzuege_params = get_policies_for_date(
        year=year, group="e_st_abzuege", raw_group_data=e_st_abzuege_raw_data
    )
    soz_vers_beitr_params = get_policies_for_date(
        year=year, group="soz_vers_beitr", raw_group_data=soz_vers_beitr_raw_data
    )
    kindergeld_params = get_policies_for_date(
        year=year, group="kindergeld", raw_group_data=kindergeld_raw_data
    )

    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(
        zve,
        e_st_abzuege_params=e_st_abzuege_params,
        soz_vers_beitr_params=soz_vers_beitr_params,
        kindergeld_params=kindergeld_params,
    )

    # TODO: We need to adress this comment. This can't be our last word!
    # allow 1€ difference, caused by strange rounding issues.
    assert_series_equal(
        df[column], year_data[column], check_less_precise=2, check_dtype=False
    )
