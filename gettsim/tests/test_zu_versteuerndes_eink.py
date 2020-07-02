import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment


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
    "alleinerziehend_freib_tu",
    "altersfreib",
    "vorsorge",
]

TEST_COLS = [
    "_zu_verst_eink_kein_kinderfreib_tu",
    "_zu_verst_eink_kinderfreib_tu",
    "kinderfreib_tu",
    "altersfreib",
    "alleinerziehend_freib_tu",
    "sum_brutto_eink",
]
YEARS = [2005, 2009, 2010, 2012, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_zve.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, target", itertools.product(YEARS, TEST_COLS))
def test_zve(
    input_data, year, target,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    columns_overriding_functions = [
        "ges_krankenv_beitr_m",
        "arbeitsl_v_beitr_m",
        "pflegev_beitr_m",
        "rentenv_beitr_m",
    ]
    result = compute_taxes_and_transfers(
        df,
        policy_params,
        policy_functions,
        targets=target,
        columns_overriding_functions=columns_overriding_functions,
    )

    if target == "kindergeld_tu":
        expected_result = sum_test_data_tu("kindergeld", year_data)
    elif target == "_zu_verst_eink_kein_kinderfreib_tu":
        expected_result = sum_test_data_tu("_zu_verst_eink_kein_kinderfreib", year_data)
    elif target == "_zu_verst_eink_kinderfreib_tu":
        expected_result = sum_test_data_tu("_zu_verst_eink_kinderfreib", year_data)
    elif target == "kinderfreib_tu":
        expected_result = sum_test_data_tu("kinderfreib", year_data)
    else:
        expected_result = year_data[target]

    # TODO: There are large differences for the 2018 test. See #217.
    assert_series_equal(
        result[target], expected_result, check_dtype=False, check_less_precise=1,
    )


def sum_test_data_tu(column, year_data):
    return (
        year_data[column]
        .groupby(year_data["tu_id"])
        .transform("sum")
        .rename(column + "_tu")
    )
