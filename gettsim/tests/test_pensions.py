import pandas as pd
import pytest
import yaml
from numpy.testing import assert_array_almost_equal

from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.pensions import pensions
from gettsim.pensions import update_earnings_points
from gettsim.policy_for_date import get_pension_data_for_year
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


@pytest.fixture(scope="module")
def pension_data_raw():
    return yaml.safe_load((ROOT_DIR / "data" / "pension_data.yaml").read_text())


@pytest.mark.parametrize("year", YEARS)
def test_pension(input_data, pension_data_raw, year):
    column = "pensions_sim"
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    soz_vers_beitr_data = get_policies_for_date(year=year, group="soz_vers_beitr")
    if year > 2017:
        soz_vers_beitr_data["calc_rentenwert"] = _rentenwert_from_2018
    else:
        soz_vers_beitr_data["calc_rentenwert"] = _rentenwert_until_2017

    pension_data = get_pension_data_for_year(
        raw_year=year, raw_pension_data=pension_data_raw
    )
    df = _apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=[column],
        func_kwargs={
            "soz_vers_beitr_data": soz_vers_beitr_data,
            "pension_data": pension_data,
        },
    )
    assert_array_almost_equal(df[column], year_data[column])


@pytest.mark.parametrize("year", YEARS)
def test_update_earning_points(input_data, pension_data_raw, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    soz_vers_beitr_data = get_policies_for_date(year=year, group="soz_vers_beitr")
    pension_data = get_pension_data_for_year(
        raw_year=year, raw_pension_data=pension_data_raw
    )
    df = _apply_tax_transfer_func(
        df,
        tax_func=update_earnings_points,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=[],
        func_kwargs={
            "soz_vers_beitr_data": soz_vers_beitr_data,
            "pension_data": pension_data,
            "year": year,
        },
    )
    assert_array_almost_equal(df["EP"], year_data["EP_end"].values)
