import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_pension_data_for_year
from gettsim.policy_for_date import get_policies_for_date
from gettsim.tax_transfer import tax_transfer


YEARS = [2002, 2010, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_tax_transfer(input_data, raw_tax_policy_data, raw_pension_data, year):
    df = input_data[input_data["year"] == year].copy()
    tb_pens = get_pension_data_for_year(year, raw_pension_data=raw_pension_data)
    tb = get_policies_for_date(year=year, tax_data_raw=raw_tax_policy_data)
    tax_transfer(df, tb, tb_pens)
