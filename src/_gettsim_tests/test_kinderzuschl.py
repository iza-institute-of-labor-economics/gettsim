import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

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
    "kinderzuschl_bruttoeink_eltern_m",
    "kinderzuschl_eink_eltern_m",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "jahr",
    "geburtsjahr",
    "vermögen_bedürft_hh",
]
OUT_COLS = [
    "_kinderzuschl_vor_vermög_check_m_tu",
    "_kinderzuschl_nach_vermög_check_m_tu",
]
# 2006 and 2009 are missing -> are currently failing
YEARS = [2013, 2016, 2017, 2019, 2020, 2021]

OVERRIDE_COLS = [
    "_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "kinderzuschl_bruttoeink_eltern_m",
    "kinderzuschl_eink_eltern_m",
    "kindergeld_anspruch",
]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(TEST_DATA_DIR / "kinderzuschl.csv")


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
        targets=[column],
        columns_overriding_functions=OVERRIDE_COLS,
    )
    assert_series_equal(
        result[column], year_data[column], check_dtype=False, atol=0, rtol=0
    )
