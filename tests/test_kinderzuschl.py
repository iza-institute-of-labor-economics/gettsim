import itertools

import pandas as pd
import pytest
from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

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
    "geburtsjahr",
    "vermögen_bedürft_hh",
]
OUT_COLS = [
    "_kinderzuschl_vor_vermög_check_m_hh",
    "_kinderzuschl_nach_vermög_check_m_hh",
]
# 2006 and 2009 are missing
YEARS = [2011, 2013, 2016, 2017, 2019, 2020, 2021]

OVERRIDE_COLS = [
    "_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh",
    "arbeitsl_geld_2_eink_m_hh",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "arbeitsl_geld_2_brutto_eink_m_hh",
    "kindergeld_anspruch",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "kinderzuschl.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_kinderzuschl(
    input_data,
    year,
    column,
):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=OVERRIDE_COLS,
    )

    assert_series_equal(
        result[column], year_data[column], check_dtype=False, atol=0, rtol=0
    )
