import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from tests.auxiliary_test import load_tax_transfer_input_data as load_input
from tests.auxiliary_test import load_tax_transfer_output_data as load_output
from tests.auxiliary_test import load_tb
from src.analysis.tax_transfer_funcs.zve import (
    zve,
    calc_hhfreib_until2014,
    calc_hhfreib_from2015,
)
from src.analysis.tax_transfer_funcs.taxes import (
    kg_eligibility_wage,
    kg_eligibility_hours,
)


input_cols = [
    "pid",
    "hid",
    "tu_id",
    "m_wage",
    "m_self",
    "m_kapinc",
    "m_vermiet",
    "renteneintritt",
    "m_pensions",
    "w_hours",
    "ineducation",
    "zveranl",
    "child",
    "handcap_degree",
    "rvbeit",
    "avbeit",
    "pvbeit",
    "alleinerz",
    "age",
    "child_num_tu",
    "year",
    "east",
    "gkvbeit",
]
years = [2005, 2009, 2010, 2012, 2018]


@pytest.mark.parametrize("year", years)
def test_zve(year):
    file_name = "test_dfs_zve.xlsx"
    columns = ["zve_nokfb", "zve_kfb"]
    df = load_input(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    if year <= 2014:
        tb["calc_hhfreib"] = calc_hhfreib_until2014
    else:
        tb["calc_hhfreib"] = calc_hhfreib_from2015
    if year > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage

    calculated = pd.DataFrame(columns=columns)
    for tu_id in df["tu_id"].unique():
        calculated = calculated.append(zve(df[df["tu_id"] == tu_id], tb)[columns])
    expected = load_output(year, file_name, columns)

    print(calculated)
    print(expected)

    # allow 1€ difference, caused by strange rounding issues.
    assert_frame_equal(calculated, expected, check_less_precise=2)
