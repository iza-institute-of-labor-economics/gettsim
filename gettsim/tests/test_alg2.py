import numpy as np
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.alg2 import alg2
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data
from gettsim.tests.auxiliary_test_tax import load_test_data

input_cols = [
    "pid",
    "hid",
    "tu_id",
    "head_tu",
    "child",
    "age",
    "miete",
    "heizkost",
    "wohnfl",
    "eigentum",
    "alleinerz",
    "m_wage",
    "m_pensions",
    "m_kapinc",
    "m_alg1",
    "m_transfers",
    "m_self",
    "m_vermiet",
    "incometax",
    "soli",
    "svbeit",
    "kindergeld_hh",
    "uhv",
    "year",
]
out_cols = [
    "ar_base_alg2_ek",
    "ar_alg2_ek_hh",
    "alg2_grossek_hh",
    "mehrbed",
    "regelbedarf",
    "regelsatz",
    "alg2_kdu",
    "uhv_hh",
    "ekanrefrei",
]


years = [2006, 2009, 2011, 2013, 2016, 2019]
tax_policy_data = load_tax_benefit_data()


@pytest.mark.parametrize("year", years)
def test_alg2(year):
    file_name = "test_dfs_alg2.ods"
    columns = ["ar_base_alg2_ek", "ar_alg2_ek_hh", "regelbedarf"]
    df = load_test_data(year, file_name, input_cols)
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    # if year <= 2010:
    #     tb["calc_regelsatz"] = regelberechnung_until_2010
    # else:
    #     tb["calc_regelsatz"] = regelberechnung_2011_and_beyond
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(alg2, tb=tb)
    expected = load_test_data(year, file_name, columns)
    assert_frame_equal(df[columns], expected)
