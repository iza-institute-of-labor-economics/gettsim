import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.tax_transfer import calculate_tax_and_transfers


YEARS = [2002, 2010, 2012, 2013, 2014, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_calc_tax_and_transfers(
    input_data, year,
):
    df = input_data[input_data["year"] == year].copy()
    calculate_tax_and_transfers(
        df, year,
    )
