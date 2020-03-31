import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.kinderzuschlag import kiz
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date


INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "alter",
    "arbeitsstunden_w",
    "bruttolohn_m",
    "in_ausbildung",
    "kaltmiete_m",
    "heizkost_m",
    "alleinerziehend",
    "kindergeld_anspruch",
    "mehrbed",
    "anz_erw_tu",
    "anz_kinder_tu",
    "arbeitsl_geld_2_brutto_eink_hh",
    "sum_arbeitsl_geld_2_eink_hh",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "jahr",
]
OUT_COLS = ["kinderzuschlag_temp", "kinderzuschlag_eink_spanne"]
YEARS = [2006, 2009, 2011, 2013, 2016, 2017, 2019, 2020]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_kiz.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_kiz(
    input_data,
    year,
    kinderzuschlag_raw_data,
    arbeitsl_geld_2_raw_data,
    kindergeld_raw_data,
):
    columns = ["kinderzuschlag_temp"]
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    kinderzuschlag_params = get_policies_for_date(
        year=year, group="kinderzuschlag", raw_group_data=kinderzuschlag_raw_data
    )
    arbeitsl_geld_2_params = get_policies_for_date(
        year=year, group="arbeitsl_geld_2", raw_group_data=arbeitsl_geld_2_raw_data
    )

    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("hh_id").apply(
        kiz,
        params=kinderzuschlag_params,
        arbeitsl_geld_2_params=arbeitsl_geld_2_params,
    )
    assert_frame_equal(df[columns], year_data[columns], check_less_precise=True)
