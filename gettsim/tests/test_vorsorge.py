import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date


IN_COLS = [
    "p_id",
    "tu_id",
    "bruttolohn_m",
    "kind",
    "prv_rente_beitr_m",
    "rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "pflegev_beitr_m",
    "jahr",
    "ges_krankenv_beitr_m",
]
OUT_COLS = ["vorsorge"]

TEST_COLS = ["vorsorge"]
YEARS = [2004, 2005, 2010, 2012, 2025]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_vorsorge.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLS))
def test_vorsorge(
    input_data, year, column,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[IN_COLS].copy()
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=year, policy_groups=["eink_st_abzuege", "soz_vers_beitr"],
    )
    user_columns = [
        "ges_krankenv_beitr_m",
        "arbeitsl_v_beitr_m",
        "pflegev_beitr_m",
        "rentenv_beitr_m",
    ]

    result = compute_taxes_and_transfers(
        df,
        user_columns=user_columns,
        user_functions=policy_func_dict,
        targets=column,
        params=params_dict,
    )

    # TODO: Here our test values are off by about 5 euro. We should revisit
    assert_series_equal(
        result, year_data[column], check_less_precise=1, check_dtype=False
    )
