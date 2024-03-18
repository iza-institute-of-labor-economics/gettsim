import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

data = load_policy_test_data("zu_verst_eink")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_zu_verst_eink(
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

    assert_series_equal(
        result[column],
        test_data.output_df[column],
        check_dtype=False,
        atol=1e-1,
        rtol=0,
    )


def sum_test_data_sn(column, year_data):
    return (
        year_data[column]
        .groupby(year_data["sn_id"])
        .transform("sum")
        .rename(column + "_sn")
    )
