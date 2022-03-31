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
    "sum_ges_rente_priv_rente_m",
    "in_priv_krankenv",
    "jahr",
]


YEARS = [2002, 2010, 2018, 2019, 2020]
OUT_COLS = [
    "sozialv_beitr_gesamt_m",
    "ges_rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_krankenv_beitr_m",
    "ges_pflegev_beitr_m",
]

OVERRIDE_COLS = ["sum_ges_rente_priv_rente_m"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "sozialv_beitr.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, target", itertools.product(YEARS, OUT_COLS))
def test_soz_vers(input_data, year, target):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    results = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=OVERRIDE_COLS,
    )

    pd.testing.assert_series_equal(results[target], year_data[target])
