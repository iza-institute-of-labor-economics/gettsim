import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.taxes.kindergeld import kindergeld
from gettsim.tests.policy_for_date import get_policies_for_date


INPUT_COLS = ["hid", "tu_id", "pid", "age", "w_hours", "ineducation", "m_wage"]
OUT_COLS = ["kindergeld_basis", "kindergeld_tu_basis"]
YEARS = [2000, 2002, 2010, 2011, 2013, 2019]


@pytest.fixture
def input_data():
    file_name = "test_dfs_kindergeld.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_kindergeld(input_data, tax_policy_data, year):
    test_column = "kindergeld_tu_basis"
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    if year > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage
    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"])[INPUT_COLS + OUT_COLS].apply(kindergeld, tb=tb)

    assert_series_equal(df[test_column], year_data[test_column], check_dtype=False)
