import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.unterhaltsvorschuss import uhv
from gettsim.config import ROOT_DIR
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data


input_cols = [
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
out_col = "uhv"
years = [2017, 2019]
tax_policy_data = load_tax_benefit_data()


@pytest.fixture
def input_data():
    file_name = "test_dfs_uhv.csv"
    out = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")
    return out


@pytest.mark.parametrize("year", years)
def test_uhv(input_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    df[out_col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(uhv, tb=tb)
    assert_series_equal(df[out_col], year_data["uhv"], check_dtype=False)
