import pandas as pd
import pytest

from gettsim.taxes.calc_taxes import tarif
from gettsim.taxes.calc_taxes import tax_sched
from gettsim.tests.auxiliary_test_tax import load_tb
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


@pytest.mark.parametrize("year", years)
def test_tax_sched(year):
    file_name = "test_dfs_tax_sched.xlsx"
    columns = ["tax_nokfb", "tax_kfb", "abgst", "soli", "soli_tu"]
    df = load_test_data(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    # list of tax bases
    tb["zve_list"] = ["nokfb", "kfb"]
    # name of tax tariff function
    tb["tax_schedule"] = tarif
    calculated = pd.DataFrame(columns=columns)
    for tu_id in df["tu_id"].unique():
        calculated = calculated.append(tax_sched(df[df["tu_id"] == tu_id], tb)[columns])
    expected = load_test_data(year, file_name, columns)
    pd.testing.assert_frame_equal(
        calculated, expected, check_dtype=False, check_exact=False, check_less_precise=0
    )
