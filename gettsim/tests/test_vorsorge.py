import itertools

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.zve import vorsorge2004, vorsorge04_05, vorsorge04_10


IN_COLS = [
    "pid",
    "tu_id",
    "m_wage",
    "child",
    "priv_pension_exp",
    "rvbeit",
    "avbeit",
    "pvbeit",
    "year",
    "gkvbeit",
    "zveranl"
]
OUT_COLS = [
    "vorsorge"
]

TEST_COLS = ["vorsorge"]
YEARS = [2005, 2010, 2025]

@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_vorsorge.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLS))
def test_vorsorge(
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
    if year >= 2010:
        e_st_abzuege_params["vorsorge"] = vorsorge04_10
    elif year >= 2005:
        e_st_abzuege_params["vorsorge"] = vorsorge04_05
    elif year <= 2004:
        e_st_abzuege_params["vorsorge"] = vorsorge2004

    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("tu_id").apply(
        e_st_abzuege_params["vorsorge"],
        params=e_st_abzuege_params,
        soz_vers_beitr_params=soz_vers_beitr_params,        
    )

    assert_series_equal(
        df[column], year_data[column], check_less_precise=2, check_dtype=False
    )
