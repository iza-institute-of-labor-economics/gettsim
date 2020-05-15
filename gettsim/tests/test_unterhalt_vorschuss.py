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
    "alleinerziehend",
    "alter",
    "bruttolohn_m",
    "sonstig_eink_m",
    "kapital_eink_m",
    "vermiet_eink_m",
    "eink_selbstst_m",
    "arbeitsl_geld_m",
    "ges_rente_m",
    "gem_veranlagt",
    "jahr",
]
OUT_COLS = ["unterhaltsvors_m"]
YEARS = [2017, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_uhv.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_uhv(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    params_dict = get_policies_for_date(
        policy_date=policy_date, groups=["unterhalt", "kindergeld"]
    )

    result = compute_taxes_and_transfers(df, targets=column, params=params_dict)

    assert_series_equal(result, year_data[column], check_dtype=False)


@pytest.fixture(scope="module")
def input_data_2():
    file_name = "test_dfs_uhv2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_uhv_07_2019(input_data_2, year, column):
    year_data = input_data_2[input_data_2["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 8, 1)
    params_dict = get_policies_for_date(
        policy_date=policy_date, groups=["unterhalt", "kindergeld"]
    )
    result = compute_taxes_and_transfers(df, targets=column, params=params_dict)
    assert_series_equal(result, year_data[column], check_dtype=False)
