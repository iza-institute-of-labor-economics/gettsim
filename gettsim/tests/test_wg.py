import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.wohngeld import calc_max_rent_since_2009
from gettsim.benefits.wohngeld import calc_max_rent_until_2008
from gettsim.benefits.wohngeld import wg
from gettsim.config import ROOT_DIR
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data

input_cols = [
    "pid",
    "hid",
    "tu_id",
    "head_tu",
    "hh_korr",
    "hhsize",
    "child",
    "miete",
    "heizkost",
    "alleinerz",
    "child11_num_tu",
    "cnstyr",
    "mietstufe",
    "m_wage",
    "m_pensions",
    "ertragsanteil",
    "m_alg1",
    "m_transfers",
    "uhv",
    "gross_e1",
    "gross_e4",
    "gross_e5",
    "gross_e6",
    "incometax",
    "rvbeit",
    "gkvbeit",
    "handcap_degree",
    "divdy",
    "year",
    "hhsize_tu",
]
out_cols = ["wohngeld_basis", "wohngeld_basis_hh"]
years = [2006, 2009, 2013, 2016, 2018, 2019]
test_column = ["wohngeld_basis_hh"]
tax_policy_data = load_tax_benefit_data()


@pytest.fixture
def input_data():
    file_name = "test_dfs_wg.csv"
    out = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")
    return out


@pytest.mark.parametrize("year", years)
def test_wg(input_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    if year < 2009:
        tb["calc_max_rent"] = calc_max_rent_until_2008
    else:
        tb["calc_max_rent"] = calc_max_rent_since_2009
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(wg, tb=tb)
    assert_frame_equal(df[test_column], year_data[test_column])


@pytest.fixture
def input_data_2():
    file_name = "test_dfs_wg.csv"
    out = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")
    return out


@pytest.mark.parametrize("year", [2013])
def test_wg_no_mietstufe_in_input_data(input_data_2, year):
    year_data = input_data_2[input_data_2["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    if year < 2009:
        tb["calc_max_rent"] = calc_max_rent_until_2008
    else:
        tb["calc_max_rent"] = calc_max_rent_since_2009
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(wg, tb=tb)
    assert_frame_equal(df[test_column], year_data[test_column])
