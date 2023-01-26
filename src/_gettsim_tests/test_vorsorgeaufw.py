import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

INPUT_COLS = [
    "p_id",
    "tu_id",
    "hh_id",
    "bruttolohn_m",
    "kind",
    "priv_rentenv_beitr_m",
    "ges_rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_pflegev_beitr_m",
    "jahr",
    "ges_krankenv_beitr_m",
]
OUT_COLS = ["vorsorgeaufw_tu"]

YEARS = [2004, 2005, 2010, 2018, 2020, 2021, 2022, 2023]

OVERRIDE_COLS = [
    "ges_krankenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_pflegev_beitr_m",
    "ges_rentenv_beitr_m",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "vorsorgeaufw.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year, target", itertools.product(YEARS, OUT_COLS))
def test_vorsorgeaufw(
    input_data,
    year,
    target,
):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=OVERRIDE_COLS,
    )

    assert_series_equal(
        result[target], year_data[target], atol=1, rtol=0, check_dtype=False
    )
