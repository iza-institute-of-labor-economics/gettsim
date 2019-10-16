import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.wohngeld import calc_max_rent_since_2009
from gettsim.benefits.wohngeld import calc_max_rent_until_2008
from gettsim.benefits.wohngeld import wg
from gettsim.tests.auxiliary_test_tax import load_tb
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
years = [2006, 2009, 2013, 2016, 2018, 2019]


@pytest.mark.parametrize("year", years)
def test_wg(year):
    file_name = "test_dfs_wg.ods"
    columns = ["wohngeld_basis_hh"]
    df = load_test_data(
        year, file_name, input_cols, bool_cols=["head_tu", "child", "alleinerz"]
    )
    tb = load_tb(year)
    tb["yr"] = year
    if year < 2009:
        tb["calc_max_rent"] = calc_max_rent_until_2008
    else:
        tb["calc_max_rent"] = calc_max_rent_since_2009
    calculated = pd.DataFrame(columns=columns)
    for hid in df["hid"].unique():
        calculated = calculated.append(wg(df[df["hid"] == hid], tb)[columns])
    expected = load_test_data(year, file_name, columns)

    assert_frame_equal(calculated, expected, check_exact=False, check_less_precise=2)


@pytest.mark.parametrize("year", [2013])
def test_wg_no_mietstufe_in_input_data(year):
    file_name = "test_dfs_wg2.csv"
    columns = ["wohngeld_basis_hh"]
    df = load_test_data(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    if year < 2009:
        tb["calc_max_rent"] = calc_max_rent_until_2008
    else:
        tb["calc_max_rent"] = calc_max_rent_since_2009
    calculated = pd.DataFrame(columns=columns)
    for hid in df["hid"].unique():
        calculated = calculated.append(wg(df[df["hid"] == hid], tb)[columns])
    expected = load_test_data(year, file_name, columns)
    assert_frame_equal(calculated, expected, check_exact=False, check_less_precise=2)
