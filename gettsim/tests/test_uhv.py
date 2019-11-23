import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.unterhaltsvorschuss import uhv
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date


INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "alleinerz",
    "age",
    "m_wage",
    "m_transfers",
    "m_kapinc",
    "m_vermiet",
    "m_self",
    "m_alg1",
    "m_pensions",
    "zveranl",
    "year",
]
OUT_COL = "uhv"
YEARS = [2017, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_uhv.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_uhv(input_data, year, unterhalt_raw_data):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    unterhalt_params = get_policies_for_date(
        year=year, group="unterhalt", raw_group_data=unterhalt_raw_data
    )
    df[OUT_COL] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(uhv, params=unterhalt_params)
    assert_series_equal(df[OUT_COL], year_data["uhv"], check_dtype=False)
