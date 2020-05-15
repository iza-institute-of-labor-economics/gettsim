import itertools
from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date

INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "kind",
    "bruttolohn_m",
    "bruttolohn_vorj_m",
    "wohnort_ost",
    "eink_st_m",
    "soli_st_m",
    "sozialv_beit_m",
    "geburtsjahr",
    "geburtsmonat",
    "geburtstag",
    "m_elterngeld_mut",
    "m_elterngeld_vat",
    "m_elterngeld",
    "jahr",
]

OUT_COLS = [
    "elterngeld_m",
    "geschw_bonus",
    "anz_mehrlinge_bonus",
    "elternzeit_anspruch",
]
YEARS = [2017, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_eltg.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_eltgeld(
    year,
    column,
    elterngeld_raw_data,
    arbeitsl_geld_raw_data,
    soz_vers_beitr_raw_data,
    eink_st_abzuege_raw_data,
    eink_st_raw_data,
    soli_st_raw_data,
    input_data,
):
    policy_date = date(year, 1, 1)
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    elterngeld_params = get_policies_for_date(
        policy_date=policy_date, group="elterngeld", raw_group_data=elterngeld_raw_data
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

    params = {
        "elterngeld_params": elterngeld_params,
        "soz_vers_beitr_params": soz_vers_beitr_params,
        "eink_st_abzuege_params": eink_st_abzuege_params,
        "eink_st_params": eink_st_params,
        "soli_st_params": soli_st_params,
    }
    result = compute_taxes_and_transfers(df, targets=column, params=params)

    assert_series_equal(
        result,
        year_data[column],
        check_dtype=False,
        check_exact=False,
        check_less_precise=2,
    )


# hh_id 7 in test cases is for the calculator on
# https://familienportal.de/familienportal/meta/egr. The result of the calculator is
# 10 Euro off the result from gettsim. We need to discuss if we should adapt the
# calculation of the proxy wage of last year or anything else.
