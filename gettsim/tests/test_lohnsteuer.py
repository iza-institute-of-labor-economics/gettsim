import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.taxes.calc_taxes import calc_lohnsteuer

INPUT_COLS = ["tu_id", "pid", "m_wage", "e_st_klasse", "child_num_kg"]

YEARS = [2020]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_lohnsteuer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_lohnsteuer(
    input_data,
    year,
    e_st_raw_data,
    e_st_abzuege_raw_data,
    soli_st_raw_data,
    abgelt_st_raw_data,
):
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

    OUT_COLS = ["lohnsteuer", "lohnsteuer_soli"]

    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("tu_id").apply(
        calc_lohnsteuer,
        params=e_st_params,
        e_st_abzuege_params=e_st_abzuege_params,
        soli_st_params=soli_st_params,
    )
    """
    e_st_abzuege_params=e_st_abzuege_params,
        soli_st_params=soli_st_params,
        abgelt_st_params=abgelt_st_params,
    """
    assert_frame_equal(df[OUT_COLS], year_data[OUT_COLS], check_dtype=False)
