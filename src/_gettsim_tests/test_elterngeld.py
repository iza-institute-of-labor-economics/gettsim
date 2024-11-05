import pytest
from pandas.testing import assert_series_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

data = load_policy_test_data("elterngeld")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_elterngeld(
    test_data: PolicyTestData,
    column: str,
):
    """Run tests to validate elterngeld."""
    df = test_data.input_df
    environment = cached_set_up_policy_environment(date=test_data.date)

    result = compute_taxes_and_transfers(
        data=df, environment=environment, targets=column
    )

    assert_series_equal(
        result[column],
        test_data.output_df[column],
        check_dtype=False,
        atol=1e-3,
        rtol=1e-3,
    )
