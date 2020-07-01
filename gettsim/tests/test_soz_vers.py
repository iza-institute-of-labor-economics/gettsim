import itertools

import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment

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
def test_soc_ins_contrib(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    params_dict, policy_func_dict = set_up_policy_environment(date=year)

    results = compute_taxes_and_transfers(df, targets=column, params=params_dict)

    pd.testing.assert_series_equal(results[column], year_data[column])
