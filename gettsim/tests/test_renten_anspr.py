from datetime import date

import pandas as pd
import pytest
from numpy.testing import assert_array_almost_equal

from gettsim.config import ROOT_DIR
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.renten_anspr import pensions
from gettsim.renten_anspr import update_earnings_points

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_m",
    "wohnort_ost",
    "alter",
    "jahr",
    "geburtsjahr",
    "entgeltpunkte",
]


YEARS = [2010, 2012, 2015]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_pensions.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_pension(input_data, year, renten_daten, soz_vers_beitr_raw_data):
    column = "rente_anspr_m"
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    soz_vers_beitr_params = get_policies_for_date(
        policy_date=policy_date,
        group="soz_vers_beitr",
        raw_group_data=soz_vers_beitr_raw_data,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=INPUT_COLS,
        out_cols=[column],
        func_kwargs={
            "renten_daten": renten_daten,
            "soz_vers_beitr_params": soz_vers_beitr_params,
        },
    )
    assert_array_almost_equal(df[column], year_data[column])


@pytest.mark.parametrize("year", YEARS)
def test_update_earning_points(input_data, renten_daten, year):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    soz_vers_beitr_params = get_policies_for_date(
        policy_date=policy_date, group="soz_vers_beitr"
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=update_earnings_points,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=INPUT_COLS,
        out_cols=[],
        func_kwargs={
            "renten_daten": renten_daten,
            "soz_vers_beitr_params": soz_vers_beitr_params,
        },
    )
    assert_array_almost_equal(df["entgeltpunkte"], year_data["EP_end"].values)
