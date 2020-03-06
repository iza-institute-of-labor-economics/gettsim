import itertools

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.zve import vorsorge_pre_2005
from gettsim.taxes.zve import vorsorge_since_2005
from gettsim.taxes.zve import vorsorge_since_2010


IN_COLS = [
    "pid",
    "tu_id",
    "lohn_m",
    "kind",
    "prv_rente_beit_m",
    "rentenv_beit_m",
    "arbeitsl_beit_m",
    "pflegev_beit_m",
    "year",
    "krankv_beit_m",
    "gem_veranlagt",
]
OUT_COLS = ["vorsorge"]

TEST_COLS = ["vorsorge"]
YEARS = [2004, 2005, 2010, 2012, 2025]


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
        calc_vorsorge = vorsorge_since_2010
    elif year >= 2005:
        calc_vorsorge = vorsorge_since_2005
    elif year <= 2004:
        calc_vorsorge = vorsorge_pre_2005

    df["vorsorge"] = np.nan
    for tu in df["tu_id"].unique():
        df.loc[df["tu_id"] == tu, "vorsorge"] = calc_vorsorge(
            df[df["tu_id"] == tu],
            params=e_st_abzuege_params,
            soz_vers_beitr_params=soz_vers_beitr_params,
        )

    assert_series_equal(
        df[column], year_data[column], check_less_precise=2, check_dtype=False
    )
