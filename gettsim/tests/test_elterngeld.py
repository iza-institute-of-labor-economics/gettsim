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
    "sozialv_beitr_m",
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
    "berechtigt_für_geschw_bonus",
    "anz_mehrlinge_anspruch",
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
    year, column, input_data,
):
    """Run tests to validate elterngeld.

    hh_id 7 in test cases is for the calculator on
    https://familienportal.de/familienportal/meta/egr. The result of the calculator is
    10 Euro off the result from gettsim. We need to discuss if we should adapt the
    calculation of the proxy wage of last year or anything else.

    """
    policy_date = date(year, 1, 1)
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date,
        groups=[
            "elterngeld",
            "soz_vers_beitr",
            "eink_st_abzuege",
            "eink_st",
            "soli_st",
        ],
    )
    columns = ["soli_st_m", "eink_st_m"]

    result = compute_taxes_and_transfers(
        df, user_columns=columns, targets=column, params=params_dict
    )

    assert_series_equal(
        result,
        year_data[column],
        check_dtype=False,
        check_exact=False,
        check_less_precise=2,
    )
