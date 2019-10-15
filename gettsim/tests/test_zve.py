import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.taxes.zve import calc_hhfreib_from2015
from gettsim.taxes.zve import calc_hhfreib_until2014
from gettsim.taxes.zve import vorsorge2010
from gettsim.taxes.zve import vorsorge_dummy
from gettsim.taxes.zve import zve
from gettsim.tests.auxiliary_test_tax import load_tb
from gettsim.tests.auxiliary_test_tax import load_test_data


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
    "m_childcare",
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
    df = load_test_data(year, file_name, input_cols)

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
    if year >= 2010:
        tb["vorsorge"] = vorsorge2010
    else:
        tb["vorsorge"] = vorsorge_dummy

    calculated = pd.DataFrame(columns=columns)
    for tu_id in df["tu_id"].unique():
        calculated = calculated.append(zve(df[df["tu_id"] == tu_id], tb)[columns])
    expected = load_test_data(year, file_name, columns)

    # allow 1€ difference, caused by strange rounding issues.
    assert_frame_equal(calculated, expected, check_less_precise=2)
