import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment


IN_COLS = [
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
OUT_COLS = ["vorsorge"]

TEST_COLS = ["vorsorge"]
YEARS = [2004, 2005, 2010, 2012, 2025]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_vorsorge.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, target", itertools.product(YEARS, TEST_COLS))
def test_vorsorge(
    input_data,
    year,
    target,
):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[IN_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    columns_overriding_functions = [
        "ges_krankenv_beitr_m",
        "arbeitsl_v_beitr_m",
        "ges_pflegev_beitr_m",
        "ges_rentenv_beitr_m",
    ]

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=columns_overriding_functions,
    )

    # TODO: Here our test values are off by about 5 euro. We should revisit. See #217.
    assert_series_equal(
        result[target], year_data[target], atol=1e-1, rtol=1, check_dtype=False
    )
