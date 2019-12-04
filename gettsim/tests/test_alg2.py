import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.alg2 import alg2
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date

INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "head_tu",
    "child",
    "age",
    "miete",
    "heizkost",
    "wohnfl",
    "eigentum",
    "alleinerz",
    "m_wage",
    "m_pensions",
    "m_kapinc",
    "m_alg1",
    "m_transfers",
    "m_self",
    "m_vermiet",
    "incometax",
    "soli",
    "svbeit",
    "kindergeld_hh",
    "uhv",
    "year",
]
OUT_COLS = [
    "ar_base_alg2_ek",
    "ar_alg2_ek_hh",
    "alg2_grossek_hh",
    "mehrbed",
    "regelbedarf",
    "regelsatz",
    "alg2_kdu",
    "uhv_hh",
    "ekanrefrei",
]


YEARS = [2006, 2009, 2011, 2013, 2016, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_alg2.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_alg2(input_data, arbeitsl_geld_2_raw_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    arbeitsl_geld_2_params = get_policies_for_date(
        year=year, group="arbeitsl_geld_2", raw_group_data=arbeitsl_geld_2_raw_data
    )

    df = df.reindex(columns=df.columns.tolist() + OUT_COLS)

    df = df.groupby("hid", group_keys=False).apply(alg2, params=arbeitsl_geld_2_params)
    assert_frame_equal(df[OUT_COLS], year_data[OUT_COLS], check_dtype=False)
