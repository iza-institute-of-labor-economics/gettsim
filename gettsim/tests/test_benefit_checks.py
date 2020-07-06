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
    "rentner",
    "alter",
    "vermögen_hh",
    "anz_minderj_hh",
    "_kinderzuschlag_m_vorläufig",
    "wohngeld_basis_hh",
    "regelbedarf_m_hh",
    "kindergeld_m_hh",
    "unterhaltsvors_m_hh",
    "arbeitsl_geld_2_eink_hh",
    "geburtsjahr",
    "jahr",
]

YEARS = [2006, 2009, 2011, 2013, 2014, 2016, 2019]
OUT_COLS = ["kinderzuschlag_m_hh", "wohngeld_m_hh", "arbeitsl_geld_2_m_hh"]


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(ROOT_DIR / "tests" / "test_data" / "test_dfs_prio.csv")


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_benefit_checks(input_data, year, column):
    """Test the benefit checks."""
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    columns = [
        "_kinderzuschlag_m_vorläufig",
        "wohngeld_basis_hh",
        "regelbedarf_m_hh",
        "kindergeld_m_hh",
        "unterhaltsvors_m_hh",
        "arbeitsl_geld_2_eink_hh",
    ]

    policy_params, policy_functions = set_up_policy_environment(date=year)
    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=columns,
    )
    assert_series_equal(result[column], year_data[column], check_dtype=False)
