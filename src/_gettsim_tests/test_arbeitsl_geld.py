import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

data = load_policy_test_data("arbeitsl_geld")


def prep_paremetrize_data(data):
    """Mark test data for 2015 with xfail."""
    for i, args in enumerate(data):
        if args[0].date.year == 2015:
            data[i] = pytest.param(
                *args,
                marks=pytest.mark.xfail(
                    reason="Arbeitslosengeld 2015 calculation is not correct due "
                    "to change in Grundfreibetrag in July 2015."
                )
            )
    return data


@pytest.mark.parametrize(
    ("test_data", "column"),
    prep_paremetrize_data(data.parametrize_args),
    ids=str,
)
def test_arbeitsl_geld(
    test_data: PolicyTestData,
    column: str,
):
    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    result = compute_taxes_and_transfers(
        data=df, params=policy_params, functions=policy_functions, targets=column
    )

    # to prevent errors from rounding, allow deviations after the 3rd digit.
    assert_series_equal(
        result[column],
        test_data.output_df[column],
        atol=1e-2,
        rtol=0,
        check_dtype=False,
    )
