import itertools
from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.tests.auxiliary import select_output_by_level


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_m",
    "betreuungskost_m",
    "eink_selbstst_m",
    "kapital_eink_m",
    "vermiet_eink_m",
    "jahr_renteneintr",
    "ges_rente_m",
    "arbeitsstunden_w",
    "in_ausbildung",
    "gem_veranlagt",
    "kind",
    "behinderungsgrad",
    "rentenv_beit_m",
    "prv_rente_beit_m",
    "arbeitsl_v_beit_m",
    "pflegev_beit_m",
    "alleinerziehend",
    "alter",
    "anz_kinder_tu",
    "jahr",
    "wohnort_ost",
    "ges_krankenv_beit_m",
]
OUT_COLS = [
    "_zu_versteuerndes_eink_kein_kind_freib",
    "_zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib",
    "_zu_versteuerndes_eink_kind_freib",
    "_zu_versteuerndes_eink_abgelt_st_m_kind_freib",
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
    "_zu_versteuerndes_eink_kein_kind_freib",
    # "_zu_versteuerndes_eink_kind_freib",
    # "altersfreib",
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
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date,
        groups=["eink_st_abzuege", "soz_vers_beitr", "kindergeld"],
    )

    result = compute_taxes_and_transfers(
        df, targets=column, user_functions=policy_func_dict, params=params_dict
    )

    expected_result = select_output_by_level(column, year_data)

    assert_series_equal(
        result,
        expected_result,
        check_dtype=False,
        check_less_precise=1,
        check_names=False,
    )
