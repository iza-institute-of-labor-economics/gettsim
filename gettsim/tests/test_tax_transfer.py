import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.tax_transfer import tax_transfer


INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "m_wage",
    "east",
    "age",
    "selfemployed",
    "haskids",
    "m_self",
    "m_pensions",
    "pkv",
    "year",
]


YEARS = [2002, 2010, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_soc_ins_contrib(input_data, tax_policy_data, year):
    df = input_data[input_data["year"] == year].copy()
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["zve_list"] = ["nokfb", "kfb"]
    tax_transfer(df, tb, tb_pens)
