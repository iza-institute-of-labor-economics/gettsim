import itertools

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
    "bruttolohn_m",
    "betreuungskost_m",
    "eink_selbst_m",
    "kapital_eink_m",
    "vermiet_eink_m",
    "jahr_renteneintr",
    "ges_rente_m",
    "arbeitsstunden_w",
    "in_ausbildung",
    "kind",
    "behinderungsgrad",
    "rentenv_beitr_m",
    "prv_rente_beitr_m",
    "arbeitsl_v_beitr_m",
    "pflegev_beitr_m",
    "alleinerziehend",
    "alter",
    "jahr",
    "wohnort_ost",
    "ges_krankenv_beitr_m",
]
OUT_COLS = [
    "_zu_verst_eink_kein_kinderfreib",
    "_zu_verst_eink_kinderfreib",
    "kind_freib",
    "brutto_eink_1",
    "brutto_eink_4",
    "brutto_eink_5",
    "brutto_eink_6",
    "brutto_eink_7",
    "brutto_eink_1_tu",
    "brutto_eink_4_tu",
    "brutto_eink_5_tu",
    "brutto_eink_6_tu",
    "brutto_eink_7_tu",
    "_ertragsanteil",
    "sonder",
    "hh_freib",
    "altersfreib",
    "vorsorge",
]

TEST_COLS = [
    "_zu_verst_eink_kein_kinderfreib_tu",
    "_zu_verst_eink_kinderfreib_tu",
    "kinderfreib_tu",
    "altersfreib",
    "sum_brutto_eink",
]
YEARS = [2005, 2009, 2010, 2012, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_zve.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLS))
def test_zve(
    input_data, year, column,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=str(year),
        groups=["eink_st_abzuege", "soz_vers_beitr", "kindergeld", "eink_st"],
    )

    user_columns = [
        "ges_krankenv_beitr_m",
        "arbeitsl_v_beitr_m",
        "pflegev_beitr_m",
        "rentenv_beitr_m",
    ]
    result = compute_taxes_and_transfers(
        df,
        user_columns=user_columns,
        user_functions=policy_func_dict,
        targets=column,
        params=params_dict,
    )

    if column == "kindergeld_tu":
        expected_result = sum_test_data_tu("kindergeld", year_data)
    elif column == "_zu_verst_eink_kein_kinderfreib_tu":
        expected_result = sum_test_data_tu("_zu_verst_eink_kein_kinderfreib", year_data)
    elif column == "_zu_verst_eink_kinderfreib_tu":
        expected_result = sum_test_data_tu("_zu_verst_eink_kinderfreib", year_data)
    else:
        expected_result = result

    assert_series_equal(
        result,
        expected_result,
        check_dtype=False,
        check_less_precise=1,
        check_names=False,
    )


def sum_test_data_tu(column, year_data):
    return year_data[column].groupby(year_data["tu_id"]).transform("sum")
