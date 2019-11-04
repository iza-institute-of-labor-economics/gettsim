import numpy as np
import pytest
from pandas.testing import assert_series_equal

from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.taxes.kindergeld import kindergeld
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data
from gettsim.tests.auxiliary_test_tax import load_test_data


input_cols = ["hid", "tu_id", "pid", "age", "w_hours", "ineducation", "m_wage"]
out_cols = ["kindergeld_basis", "kindergeld_tu_basis"]
years = [2000, 2002, 2010, 2011, 2013, 2019]
tax_policy_data = load_tax_benefit_data()


@pytest.mark.parametrize("year", years)
def test_kindergeld(year):
    filename = "test_dfs_kindergeld.ods"
    test_column = "kindergeld_tu_basis"
    df = load_test_data(year, filename, input_cols)
    tb = get_policies_for_date(tax_policy_data, year=year)
    if year > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"])[input_cols + out_cols].apply(kindergeld, tb=tb)

    expected = load_test_data(year, filename, test_column)

    assert_series_equal(df[test_column], expected, check_dtype=False)
