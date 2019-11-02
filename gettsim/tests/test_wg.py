import numpy as np
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.wohngeld import calc_max_rent_since_2009
from gettsim.benefits.wohngeld import calc_max_rent_until_2008
from gettsim.benefits.wohngeld import wg
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data
from gettsim.tests.auxiliary_test_tax import load_test_data

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


@pytest.mark.parametrize("year", years)
def test_wg(year):
    file_name = "test_dfs_wg.ods"
    df = load_test_data(
        year, file_name, input_cols, bool_cols=["head_tu", "child", "alleinerz"]
    )
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    if year < 2009:
        tb["calc_max_rent"] = calc_max_rent_until_2008
    else:
        tb["calc_max_rent"] = calc_max_rent_since_2009
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(wg, tb=tb)
    expected = load_test_data(year, file_name, test_column)
    assert_frame_equal(
        df[test_column], expected, check_exact=False, check_less_precise=2
    )


@pytest.mark.parametrize("year", [2013])
def test_wg_no_mietstufe_in_input_data(year):
    file_name = "test_dfs_wg2.csv"
    df = load_test_data(year, file_name, input_cols)
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    if year < 2009:
        tb["calc_max_rent"] = calc_max_rent_until_2008
    else:
        tb["calc_max_rent"] = calc_max_rent_since_2009
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(wg, tb=tb)
    expected = load_test_data(year, file_name, test_column)
    assert_frame_equal(
        df[test_column], expected, check_exact=False, check_less_precise=2
    )
