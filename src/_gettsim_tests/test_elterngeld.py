import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

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
    "m_elterngeld_mut_hh",
    "m_elterngeld_vat_hh",
    "m_elterngeld",
    "jahr",
]

OUT_COLS = [
    "elterngeld_m",
    "elterngeld_geschw_bonus_anspruch",
    "_elterngeld_anz_mehrlinge_anspruch",
    "elternzeit_anspruch",
]
YEARS = [2017, 2018, 2019]

OVERRIDE_COLS = [
    "soli_st_tu",
    "sozialv_beitr_m",
    "eink_st_tu",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "elterngeld.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_elterngeld(
    year,
    column,
    input_data,
):
    """Run tests to validate elterngeld.

    hh_id 7 in test cases is for the calculator on
    https://familienportal.de/familienportal/meta/egr. The calculator's result is 10
    Euro off GETTSIM's result. We need to discuss if we should adapt the calculation of
    the proxy wage of last year or anything else.

    """
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    df["soli_st_tu"] = df["soli_st_m"].groupby(df["tu_id"]).transform("sum") * 12
    df["eink_st_tu"] = df["eink_st_m"].groupby(df["tu_id"]).transform("sum") * 12

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=OVERRIDE_COLS,
    )

    assert_series_equal(
        result[column], year_data[column], check_dtype=False, atol=1e-1, rtol=0
    )
