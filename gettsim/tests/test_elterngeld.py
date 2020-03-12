import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.apply_tax_funcs import apply_tax_transfer_func
from gettsim.benefits.elterngeld import elterngeld
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date

INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "kind",
    "bruttolohn_m",
    "bruttolohn_vorj_m",
    "wohnort_ost",
    "eink_st",
    "soli_st",
    "sozialv_beit_m",
    "geburtsjahr",
    "geburtsmonat",
    "geburtstag",
    "m_elterngeld_mut",
    "m_elterngeld_vat",
    "m_elterngeld",
    "year",
]

OUT_COLS = ["elterngeld", "geschw_bonus", "anz_mehrlinge", "elternzeit_anspruch"]
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
    e_st_abzuege_raw_data,
    e_st_raw_data,
    soli_st_raw_data,
    input_data,
):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    elterngeld_params = get_policies_for_date(
        year=year, group="elterngeld", raw_group_data=elterngeld_raw_data
    )
    soz_vers_beitr_params = get_policies_for_date(
        year=year, group="soz_vers_beitr", raw_group_data=soz_vers_beitr_raw_data
    )
    e_st_abzuege_params = get_policies_for_date(
        year=year, group="e_st_abzuege", raw_group_data=e_st_abzuege_raw_data
    )
    e_st_params = get_policies_for_date(
        year=year, group="e_st", raw_group_data=e_st_raw_data
    )
    soli_st_params = get_policies_for_date(
        year=year, group="soli_st", raw_group_data=soli_st_raw_data
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": elterngeld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "e_st_abzuege_params": e_st_abzuege_params,
            "e_st_params": e_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    assert_series_equal(
        df[column],
        year_data[column],
        check_dtype=False,
        check_exact=False,
        check_less_precise=2,
    )


# hh_id 7 in test cases is for the calculator on
# https://familienportal.de/familienportal/meta/egr. The result of the calculator is
# 10 Euro off the result from gettsim. We need to discuss if we should adapt the
# calculation of the proxy wage of last year or anything else.
