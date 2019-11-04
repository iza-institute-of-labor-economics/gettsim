import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.config import ROOT_DIR
from gettsim.taxes.calc_taxes import tarif
from gettsim.taxes.calc_taxes import tax_sched
from gettsim.tests.policy_for_date import get_policies_for_date

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


@pytest.fixture
def input_data():
    file_name = "test_dfs_tax_sched.csv"
    out = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")
    return out


@pytest.mark.parametrize("year", years)
def test_tax_sched(input_data, tax_policy_data, year):
    columns = ["tax_nokfb", "tax_kfb", "abgst", "soli", "soli_tu"]
    year_data = input_data[input_data["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
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
    # TODO: This test needs to be reviewed
    assert_frame_equal(df[columns], year_data[columns], check_less_precise=0)
