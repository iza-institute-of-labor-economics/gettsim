import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

OVERRIDE_COLS = [
    "ges_krankenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_pflegev_beitr_m",
    "ges_rentenv_beitr_m",
]

data = load_policy_test_data("vorsorgeaufw")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_vorsorgeaufw(
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

    assert_series_equal(
        result[column], test_data.output_df[column], atol=1, rtol=0, check_dtype=False
    )
