import pandas as pd
import pytest
from numpy.testing import assert_array_almost_equal

from gettsim.config import ROOT_DIR
from gettsim.pensions import pensions
from gettsim.pensions import update_earnings_points
from gettsim.policy_for_date import get_policies_for_date
from gettsim.tax_transfer import _apply_tax_transfer_func

INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "m_wage",
    "east",
    "age",
    "year",
    "byear",
    "exper",
    "EP",
]


YEARS = [2010, 2012, 2015]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_pensions.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_pension(input_data, year, ges_renten_vers_raw_data, soz_vers_beitr_raw_data):
    column = "pensions_sim"
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    soz_vers_beitr_data = get_policies_for_date(
        year=year, group="soz_vers_beitr", raw_group_data=soz_vers_beitr_raw_data
    )
    ges_renten_vers_data = get_policies_for_date(
        year=year, group="ges_renten_vers", raw_group_data=ges_renten_vers_raw_data
    )
    df = _apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=[column],
        func_kwargs={
            "soz_vers_beitr_data": soz_vers_beitr_data,
            "ges_renten_vers_data": ges_renten_vers_data,
        },
    )
    assert_array_almost_equal(df[column], year_data[column])


@pytest.mark.parametrize("year", YEARS)
def test_update_earning_points(input_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    soz_vers_beitr_data = get_policies_for_date(year=year, group="soz_vers_beitr")
    ges_renten_vers_data = get_policies_for_date(year=year, group="ges_renten_vers")
    df = _apply_tax_transfer_func(
        df,
        tax_func=update_earnings_points,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=[],
        func_kwargs={
            "soz_vers_beitr_data": soz_vers_beitr_data,
            "ges_renten_vers_data": ges_renten_vers_data,
            "year": year,
        },
    )
    assert_array_almost_equal(df["EP"], year_data["EP_end"].values)
