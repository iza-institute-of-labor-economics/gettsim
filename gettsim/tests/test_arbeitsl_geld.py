from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
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
    input_data, year,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date,
        groups=[
            "arbeitsl_geld",
            "soz_vers_beitr",
            "eink_st_abzuege",
            "eink_st",
            "soli_st",
        ],
    )

    result = compute_taxes_and_transfers(
        df, targets="arbeitsl_geld_m", params=params_dict
    )

    # to prevent errors from rounding, allow deviations after the 3rd digit.
    assert_series_equal(
        result, year_data["arbeitsl_geld_m"], check_less_precise=3, check_dtype=False
    )
