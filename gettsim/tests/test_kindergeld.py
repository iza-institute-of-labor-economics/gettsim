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
    "hh_id",
    "tu_id",
    "p_id",
    "alter",
    "arbeitsstunden_w",
    "in_ausbildung",
    "bruttolohn_m",
]
OUT_COLS = ["kindergeld_m_basis", "kindergeld_m_tu_basis"]
YEARS = [2000, 2002, 2010, 2011, 2013, 2019]
TEST_COLS = ["kindergeld_m_tu_basis"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_kindergeld.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLS))
def test_kindergeld(input_data, year, column):

    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict = get_policies_for_date(policy_date=policy_date, groups="kindergeld")
    calc_result = compute_taxes_and_transfers(df, targets=column, params=params_dict)

    expected_result = select_output_by_level(column, year_data)

    assert_series_equal(
        calc_result, expected_result, check_dtype=False, check_names=False
    )
