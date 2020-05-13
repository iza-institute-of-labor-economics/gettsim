from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_vorj_m",
    "wohnort_ost",
    "kind",
    "arbeitsl_lfdj_m",
    "arbeitsl_vorj_m",
    "arbeitsl_vor2j_m",
    "ges_rente_m",
    "arbeitsstunden_w",
    "anz_kinder_tu",
    "alter",
    "jahr",
]
YEARS = [2010, 2011, 2015, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_ui.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_ui(
    input_data,
    year,
    arbeitsl_geld_raw_data,
    soz_vers_beitr_raw_data,
    eink_st_abzuege_raw_data,
    eink_st_raw_data,
    soli_st_raw_data,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    arbeitsl_geld_params = get_policies_for_date(
        policy_date=policy_date,
        group="arbeitsl_geld",
        raw_group_data=arbeitsl_geld_raw_data,
    )
    soz_vers_beitr_params = get_policies_for_date(
        policy_date=policy_date,
        group="soz_vers_beitr",
        raw_group_data=soz_vers_beitr_raw_data,
    )
    eink_st_abzuege_params = get_policies_for_date(
        policy_date=policy_date,
        group="eink_st_abzuege",
        raw_group_data=eink_st_abzuege_raw_data,
    )
    eink_st_params = get_policies_for_date(
        policy_date=policy_date, group="eink_st", raw_group_data=eink_st_raw_data
    )
    soli_st_params = get_policies_for_date(
        policy_date=policy_date, group="soli_st", raw_group_data=soli_st_raw_data
    )

    params_dict = {
        "arbeitsl_geld_params": arbeitsl_geld_params,
        "soz_vers_beitr_params": soz_vers_beitr_params,
        "eink_st_abzuege_params": eink_st_abzuege_params,
        "eink_st_params": eink_st_params,
        "soli_st_params": soli_st_params,
    }

    result = compute_taxes_and_transfers(
        dict(df), targets="arbeitsl_geld_m", params=params_dict
    )

    # to prevent errors from rounding, allow deviations after the 3rd digit.
    assert_series_equal(result, year_data["arbeitsl_geld_m"], check_less_precise=3)
