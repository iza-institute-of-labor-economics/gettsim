import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.tax_transfer import tax_transfer


YEARS = [2002, 2010, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_tax_transfer(input_data, tax_policy_data, year):
    df = input_data[input_data["year"] == year].copy()
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    tb = get_policies_for_date(year=year, tax_data_raw=tax_policy_data)
    tb["zve_list"] = ["nokfb", "kfb"]
    tax_transfer(df, tb, tb_pens)
