import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.alg2 import alg2
from gettsim.config import ROOT_DIR
from gettsim.tests.policy_for_date import get_policies_for_date

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


@pytest.fixture
def input_data():
    file_name = "test_dfs_alg2.csv"
    out = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")
    return out


@pytest.mark.parametrize("year", years)
def test_alg2(input_data, tax_policy_data, year):
    columns = ["ar_base_alg2_ek", "ar_alg2_ek_hh", "regelbedarf"]
    year_data = input_data[input_data["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    # if year <= 2010:
    #     tb["calc_regelsatz"] = regelberechnung_until_2010
    # else:
    #     tb["calc_regelsatz"] = regelberechnung_2011_and_beyond
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(alg2, tb=tb)
    assert_frame_equal(df[columns], year_data[columns])
