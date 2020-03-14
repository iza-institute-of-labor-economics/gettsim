import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.kindergeld import kindergeld


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


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_kindergeld.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_kindergeld(input_data, year, kindergeld_raw_data):
    test_column = "kindergeld_m_tu_basis"
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    kindergeld_params = get_policies_for_date(
        year=year, group="kindergeld", raw_group_data=kindergeld_raw_data
    )
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hh_id", "tu_id"])[INPUT_COLS + OUT_COLS].apply(
        kindergeld, params=kindergeld_params
    )

    assert_series_equal(df[test_column], year_data[test_column], check_dtype=False)
