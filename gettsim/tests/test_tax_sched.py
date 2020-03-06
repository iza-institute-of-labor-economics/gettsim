import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.e_st import e_st

INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "kind",
    "_zu_versteuerndes_eink_kein_kind_freib",
    "_zu_versteuerndes_eink_kind_freib",
    "_zu_versteuerndes_eink_abgelt_st_kind_freib",
    "_zu_versteuerndes_eink_abgelt_st_kein_kind_freib",
    "brutto_eink_5",
    "gem_veranlagt",
    "brutto_eink_5_tu",
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
    columns = [
        "_st_kein_kind_freib_tu",
        "_st_kind_freib_tu",
        "abgelt_st",
        "soli_st",
        "soli_st_tu",
    ]
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
        [f"_st_{inc}" for inc in e_st_abzuege_params["eink_arten"]]
        + [f"_st_{inc}_tu" for inc in e_st_abzuege_params["eink_arten"]]
        + ["abgelt_st_tu", "abgelt_st", "soli_st", "soli_st_tu"]
    )

    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hid", "tu_id"]).apply(
        e_st,
        e_st_params=e_st_params,
        e_st_abzuege_params=e_st_abzuege_params,
        soli_st_params=soli_st_params,
        abgelt_st_params=abgelt_st_params,
    )

    assert_frame_equal(
        df[columns], year_data[columns], check_dtype=False, check_less_precise=1
    )
