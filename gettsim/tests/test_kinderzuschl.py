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
    "kind",
    "alter",
    "arbeitsstunden_w",
    "bruttolohn_m",
    "in_ausbildung",
    "bruttokaltmiete_m_hh",
    "heizkosten_m_hh",
    "alleinerz",
    "kindergeld_anspruch",
    "_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh",
    "arbeitsl_geld_2_brutto_eink_m_hh",
    "arbeitsl_geld_2_eink_m_hh",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "jahr",
]
OUT_COLS = ["kinderzuschl_vorläufig_m"]
# 2006 and 2009 are missing
YEARS = [2011, 2013, 2016, 2017, 2019, 2020, 2021]


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
    policy_params, policy_functions = set_up_policy_environment(date=year)
    columns = [
        "_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh",
        "arbeitsl_geld_2_eink_m_hh",
        "kindergeld_m_hh",
        "unterhaltsvors_m",
        "arbeitsl_geld_2_brutto_eink_m_hh",
        "kindergeld_anspruch",
    ]

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=columns,
    )

    assert_series_equal(
        result[column], year_data[column], check_dtype=False,
    )
