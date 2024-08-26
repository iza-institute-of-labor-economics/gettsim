import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

OVERRIDE_COLS = []

data = load_policy_test_data("aggregate_by_p_id")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_aggregate_by_p_id(
    test_data: PolicyTestData,
    column: str,
):
    df = test_data.input_df
    environment = cached_set_up_policy_environment(date=test_data.date)

    result = compute_taxes_and_transfers(
        data=df, environment=environment, targets=column
    )

    assert_series_equal(
        result[column],
        test_data.output_df[column],
        check_dtype=False,
        atol=1e-1,
        rtol=0,
    )
