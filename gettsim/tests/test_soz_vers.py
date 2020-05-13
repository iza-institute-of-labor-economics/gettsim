import datetime
import itertools

import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_m",
    "wohnort_ost",
    "alter",
    "selbstständig",
    "hat_kinder",
    "eink_selbst_m",
    "ges_rente_m",
    "prv_krankenv",
    "jahr",
]


YEARS = [2002, 2010, 2018, 2019, 2020]
OUT_COLS = [
    "sozialv_beitr_m",
    "rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_krankenv_beitr_m",
    "pflegev_beitr_m",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_ssc.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_soc_ins_contrib(input_data, year, column, soz_vers_beitr_raw_data):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = datetime.date(year, 1, 1)
    soz_vers_beitr_params = get_policies_for_date(
        policy_date=policy_date,
        group="soz_vers_beitr",
        raw_group_data=soz_vers_beitr_raw_data,
    )

    results = compute_taxes_and_transfers(
        dict(df), targets=column, params=soz_vers_beitr_params
    )

    pd.testing.assert_series_equal(results, year_data[column])
