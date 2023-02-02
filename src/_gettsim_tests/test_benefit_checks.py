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
    "rentner",
    "alter",
    "vermögen_bedürft_hh",
    "_kinderzuschl_vor_vermög_check_m_tu",
    "wohngeld_vor_vermög_check_m_hh",
    "arbeitsl_geld_2_regelbedarf_m_hh",
    "kindergeld_m_hh",
    "unterhaltsvors_m_hh",
    "arbeitsl_geld_2_eink_m_hh",
    "geburtsjahr",
    "jahr",
]

YEARS = [2006, 2009, 2011, 2013, 2014, 2016, 2019]
OUT_COLS = ["kinderzuschl_m_hh", "wohngeld_m_hh", "arbeitsl_geld_2_m_hh"]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(TEST_DATA_DIR / "benefit_checks.csv")


@pytest.mark.parametrize("year, target", itertools.product(YEARS, OUT_COLS))
def test_benefit_checks(input_data, year, target):
    """Test the benefit checks."""
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    columns = [
        "_kinderzuschl_vor_vermög_check_m_tu",
        "wohngeld_vor_vermög_check_m_hh",
        "arbeitsl_geld_2_regelbedarf_m_hh",
        "kindergeld_m_hh",
        "unterhaltsvors_m_hh",
        "arbeitsl_geld_2_eink_m_hh",
    ]

    policy_params, policy_functions = set_up_policy_environment(date=year)
    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=columns,
    )
    assert_series_equal(
        result[target], year_data[target], check_dtype=False, atol=1e-1, rtol=0
    )
