import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.calc_taxes import tax_sched

INPUT_COLS = [
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

YEARS = [2009, 2012, 2015, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_sched.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_tax_sched(
    input_data,
    year,
    e_st_raw_data,
    e_st_abzuege_raw_data,
    soli_st_raw_data,
    abgelt_st_raw_data,
):
    columns = ["tax_nokfb", "tax_kfb", "abgst", "soli", "soli_tu"]
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    e_st_abzuege_params = get_policies_for_date(
        year=year, group="e_st_abzuege", raw_group_data=e_st_abzuege_raw_data
    )
    e_st_params = get_policies_for_date(
        year=year, group="e_st", raw_group_data=e_st_raw_data
    )
    soli_st_params = get_policies_for_date(
        year=year, group="soli_st", raw_group_data=soli_st_raw_data
    )
    abgelt_st_params = get_policies_for_date(
        year=year, group="abgelt_st", raw_group_data=abgelt_st_raw_data
    )
    OUT_COLS = (
        [f"tax_{inc}" for inc in e_st_abzuege_params["zve_list"]]
        + [f"tax_{inc}_tu" for inc in e_st_abzuege_params["zve_list"]]
        + ["abgst_tu", "abgst", "soli", "soli_tu"]
    )

    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(
        tax_sched,
        e_st_params=e_st_params,
        e_st_abzuege_params=e_st_abzuege_params,
        soli_st_params=soli_st_params,
        abgelt_st_params=abgelt_st_params,
    )

    assert_frame_equal(df[columns], year_data[columns], check_dtype=False)
