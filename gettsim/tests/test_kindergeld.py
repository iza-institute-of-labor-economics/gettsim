import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.taxes.kindergeld import kindergeld
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data


input_cols = ["hid", "tu_id", "pid", "age", "w_hours", "ineducation", "m_wage"]
out_cols = ["kindergeld_basis", "kindergeld_tu_basis"]
years = [2000, 2002, 2010, 2011, 2013, 2019]
tax_policy_data = load_tax_benefit_data()


@pytest.fixture
def input_data():
    file_name = "test_dfs_kindergeld.csv"
    out = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")
    return out


@pytest.mark.parametrize("year", years)
def test_kindergeld(input_data, year):
    test_column = "kindergeld_tu_basis"
    year_data = input_data[input_data["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    if year > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"])[input_cols + out_cols].apply(kindergeld, tb=tb)

    assert_series_equal(df[test_column], year_data[test_column], check_dtype=False)
