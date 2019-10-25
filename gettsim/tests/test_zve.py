import numpy as np
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
out_cols = [
    "zve_nokfb",
    "zve_abg_nokfb",
    "zve_kfb",
    "zve_abg_kfb",
    "kifreib",
    "gross_e1",
    "gross_e4",
    "gross_e5",
    "gross_e6",
    "gross_e7",
    "gross_e1_tu",
    "gross_e4_tu",
    "gross_e5_tu",
    "gross_e6_tu",
    "gross_e7_tu",
    "ertragsanteil",
    "sonder",
    "hhfreib",
    "altfreib",
    "vorsorge",
]

years = [2005, 2009, 2010, 2012, 2018]


@pytest.mark.parametrize("year", years)
def test_zve(year):
    file_name = "test_dfs_zve.ods"
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

    for col in out_cols:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(zve, tb=tb)
    expected = load_test_data(year, file_name, columns)

    # allow 1€ difference, caused by strange rounding issues.
    assert_frame_equal(df[columns], expected, check_less_precise=2)
