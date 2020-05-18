import itertools
from datetime import date

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "alter",
    "arbeitsstunden_w",
    "bruttolohn_m",
    "in_ausbildung",
    "kaltmiete_m",
    "heizkost_m",
    "alleinerziehend",
    "kindergeld_anspruch",
    "alleinerziehenden_mehrbedarf",
    "anz_erw_tu",
    "anz_kinder_tu",
    "arbeitsl_geld_2_brutto_eink_hh",
    "sum_arbeitsl_geld_2_eink_hh",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "jahr",
]
OUT_COLS = ["kinderzuschlag_temp"]
YEARS = [2006, 2009, 2011, 2013, 2016, 2017, 2019, 2020]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_kiz.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_kiz(
    input_data, year, column,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict = get_policies_for_date(
        policy_date=policy_date, groups=["kinderzuschlag", "arbeitsl_geld_2"],
    )
    columns = [
        "alleinerziehenden_mehrbedarf",
        "arbeitsl_geld_2_brutto_eink_hh",
        "sum_arbeitsl_geld_2_eink_hh",
        "kindergeld_m_hh",
        "unterhaltsvors_m",
    ]

    result = compute_taxes_and_transfers(
        df, user_columns=columns, targets=column, params=params_dict
    )

    assert_series_equal(result, year_data[column], check_less_precise=True)
