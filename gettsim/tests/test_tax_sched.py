import numpy as np
import pytest
from pandas.testing import assert_frame_equal

from gettsim.taxes.calc_taxes import tarif
from gettsim.taxes.calc_taxes import tax_sched
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data
from gettsim.tests.auxiliary_test_tax import load_test_data

input_cols = [
    "pid",
    "hid",
    "tu_id",
    "child",
    "zve_nokfb",
    "zve_kfb",
    "zve_abg_kfb",
    "zve_abg_nokfb",
    "gross_e5",
    "zveranl",
    "gross_e5_tu",
]

years = [2009, 2012, 2015, 2018]
tax_policy_data = load_tax_benefit_data()


@pytest.mark.parametrize("year", years)
def test_tax_sched(year):
    file_name = "test_dfs_tax_sched.ods"
    columns = ["tax_nokfb", "tax_kfb", "abgst", "soli", "soli_tu"]
    df = load_test_data(year, file_name, input_cols)
    tb = get_policies_for_date(tax_policy_data, year=year)
    # list of tax bases
    tb["zve_list"] = ["nokfb", "kfb"]
    out_cols = (
        [f"tax_{inc}" for inc in tb["zve_list"]]
        + [f"tax_{inc}_tu" for inc in tb["zve_list"]]
        + ["abgst_tu", "abgst", "soli", "soli_tu"]
    )

    # name of tax tariff function
    tb["tax_schedule"] = tarif
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(tax_sched, tb=tb)
    expected = load_test_data(year, file_name, columns)
    assert_frame_equal(df[columns], expected, check_exact=False, check_less_precise=0)
