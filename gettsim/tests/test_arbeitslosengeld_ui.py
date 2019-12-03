import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.arbeitslosengeld import ui
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.tax_transfer import _apply_tax_transfer_func


INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "m_wage_l1",
    "east",
    "child",
    "months_ue",
    "months_ue_l1",
    "months_ue_l2",
    "m_pensions",
    "w_hours",
    "child_num_tu",
    "age",
    "year",
]
OUT_COL = "m_alg1"
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
    e_st_abzuege_raw_data,
    e_st_raw_data,
    soli_st_raw_data,
):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    arbeitsl_geld_params = get_policies_for_date(
        year=year, group="arbeitsl_geld", raw_group_data=arbeitsl_geld_raw_data
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
    df = _apply_tax_transfer_func(
        df,
        tax_func=ui,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=[OUT_COL],
        func_kwargs={
            "params": arbeitsl_geld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "e_st_abzuege_params": e_st_abzuege_params,
            "e_st_params": e_st_params,
            "soli_st_params": soli_st_params,
        },
    )
    # to prevent errors from rounding, allow deviations after the 3rd digit.
    assert_series_equal(df[OUT_COL], year_data[OUT_COL], check_less_precise=3)
