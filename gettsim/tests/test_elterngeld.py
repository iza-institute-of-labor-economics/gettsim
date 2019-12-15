import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.elterngeld import elt_geld
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.tax_transfer import _apply_tax_transfer_func


INPUT_COLS = [
    "hid",
    "tu_id",
    "pid",
    "m_wage",
    "m_wage_l1",
    "east",
    "incometax",
    "soli",
    "svbeit",
    "elt_zeit",
    "geschw_bonus",
    "year",
]

OUT_COLS = ["elt_geld"]
YEARS = [2017, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_eltg.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_eltgeld(
    year,
    arbeitsl_geld_raw_data,
    soz_vers_beitr_raw_data,
    e_st_abzuege_raw_data,
    e_st_raw_data,
    soli_st_raw_data,
    input_data,
):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    elterngeld_params = get_policies_for_date(year=year, group="elterngeld")
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
        tax_func=elt_geld,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": elterngeld_params,
            "arbeitsl_geld_params": arbeitsl_geld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "e_st_abzuege_params": e_st_abzuege_params,
            "e_st_params": e_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    assert_frame_equal(
        df[OUT_COLS].round(), year_data[OUT_COLS].round(), check_dtype=False
    )
