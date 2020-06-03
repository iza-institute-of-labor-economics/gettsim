import itertools
from datetime import date

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
    "kind",
    "rentner",
    "alter",
    "vermögen_hh",
    "anz_minderj_hh",
    "_kinderzuschlag_m_vorläufig",
    "wohngeld_basis_hh",
    "regelbedarf_m",
    "_sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m",
    "geburtsjahr",
    "jahr",
]

YEARS = [2006, 2009, 2011, 2013, 2014, 2016, 2019]
OUT_COLS = ["kinderzuschlag_m", "wohngeld_m", "arbeitsl_geld_2_m"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_prio.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_benefit_checks(input_data, year, column):
    """Test the benefit checks."""
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    columns = [
        "_kinderzuschlag_m_vorläufig",
        "wohngeld_basis_hh",
        "regelbedarf_m",
        "_sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m",
    ]

    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date, groups="arbeitsl_geld_2",
    )
    result = compute_taxes_and_transfers(
        df,
        user_columns=columns,
        user_functions=policy_func_dict,
        targets=column,
        params=params_dict,
    )
    assert_series_equal(result, year_data[column], check_dtype=False)
