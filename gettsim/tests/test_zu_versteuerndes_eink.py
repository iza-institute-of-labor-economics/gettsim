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
    "kapitaleink_brutto_m",
    "vermiet_eink_m",
    "jahr_renteneintr",
    "sum_ges_rente_priv_rente_m",
    "arbeitsstunden_w",
    "in_ausbildung",
    "kind",
    "behinderungsgrad",
    "ges_rentenv_beitr_m",
    "priv_rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_pflegev_beitr_m",
    "alleinerz",
    "alter",
    "jahr",
    "wohnort_ost",
    "ges_krankenv_beitr_m",
]
OUT_COLS = [
    "zu_verst_eink_kein_kinderfreib",
    "zu_verst_eink_kinderfreib",
    "kinderfreib",
    "eink_selbst",
    "eink_abhängig_beschäftigt",
    "kapitaleink_brutto",
    "eink_vermietung",
    "eink_rente_zu_verst",
    "eink_selbst_tu",
    "eink_abhängig_beschäftigt_tu",
    "kapitaleink_brutto_tu",
    "eink_vermietung_tu",
    "eink_rente_zu_verst_tu",
    "rente_ertragsanteil",
    "sonder",
    "alleinerz_freib_tu",
    "eink_st_altersfreib",
    "vorsorge",
]

TEST_COLS = [
    "_zu_verst_eink_ohne_kinderfreib_tu",
    "zu_verst_eink_mit_kinderfreib_tu",
    "eink_st_kinderfreib_tu",
    "eink_st_altersfreib",
    "alleinerz_freib_tu",
    "sum_eink",
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
        "ges_pflegev_beitr_m",
        "ges_rentenv_beitr_m",
        "sum_ges_rente_priv_rente_m",
    ]
    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=columns_overriding_functions,
    )

    if target == "kindergeld_tu":
        expected_result = sum_test_data_tu("kindergeld", year_data)
    elif target == "_zu_verst_eink_ohne_kinderfreib_tu":
        expected_result = sum_test_data_tu("_zu_verst_eink_ohne_kinderfreib", year_data)
    elif target == "zu_verst_eink_mit_kinderfreib_tu":
        expected_result = sum_test_data_tu("zu_verst_eink_mit_kinderfreib", year_data)
    elif target == "eink_st_kinderfreib_tu":
        expected_result = sum_test_data_tu("eink_st_kinderfreib", year_data)
    else:
        expected_result = year_data[target]

    # TODO: There are large differences for the 2018 test. See #217.
    assert_series_equal(
        result[target], expected_result, check_dtype=False, atol=1e-1, rtol=1,
    )


def sum_test_data_tu(column, year_data):
    return (
        year_data[column]
        .groupby(year_data["tu_id"])
        .transform("sum")
        .rename(column + "_tu")
    )
