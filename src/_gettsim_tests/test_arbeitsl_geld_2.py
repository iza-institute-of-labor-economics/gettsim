"""
Note:
- Values for "arbeitsl_geld_2_vor_vorrang_m_hh" and "arbeitsl_geld_2_m_hh" are
  only regression tests
- "wohngeld_vor_vermög_check_m_hh" is set to 0 to avoid testing Wohngeld-Vorrang and the
  calculation of Wohngeld here.

"""

import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

OVERRIDE_COLS = [
    "arbeitsl_geld_m",
    "soli_st_tu",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "elterngeld_m",
    "eink_st_tu",
    "sozialv_beitr_m",
    "sum_ges_rente_priv_rente_m",
    "wohngeld_vor_vermög_check_m_hh",
]

data = load_policy_test_data("arbeitsl_geld_2")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_arbeitsl_geld_2(
    test_data: PolicyTestData,
    column: str,
):
    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=OVERRIDE_COLS,
    )

    if column in [
        "arbeitsl_geld_2_vor_vorrang_m_hh",
        "arbeitsl_geld_2_m_hh",
    ]:
        result = result[column].round(2)
    else:
        result = result[column]
    assert_series_equal(
        result, test_data.output_df[column], check_dtype=False, atol=1e-1, rtol=0
    )
