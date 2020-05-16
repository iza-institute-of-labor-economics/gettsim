import itertools
from datetime import date

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.taxes.zu_versteuerndes_eink import vorsorge_pre_2005
from gettsim.taxes.zu_versteuerndes_eink import vorsorge_since_2005
from gettsim.taxes.zu_versteuerndes_eink import vorsorge_since_2010


IN_COLS = [
    "p_id",
    "tu_id",
    "bruttolohn_m",
    "kind",
    "prv_rente_beit_m",
    "rentenv_beit_m",
    "arbeitsl_v_beit_m",
    "pflegev_beit_m",
    "jahr",
    "ges_krankenv_beit_m",
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
    input_data, year, column,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[IN_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date, groups=["eink_st_abzuege", "soz_vers_beitr"],
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
            params=params_dict["eink_st_abzuege"],
            soz_vers_beitr_params=params_dict["soz_vers_beitr"],
        )

    assert_series_equal(
        df[column], year_data[column], check_less_precise=2, check_dtype=False
    )
