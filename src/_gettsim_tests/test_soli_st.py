import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

OVERRIDE_COLS_UNTIL_2008 = ["eink_st_mit_kinderfreib_y_tu"]
OVERRIDE_COLS_AFTER_2008 = ["eink_st_mit_kinderfreib_y_tu", "abgelt_st_y_tu"]

data = load_policy_test_data("soli_st")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_soli_st(
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
        columns_overriding_functions=OVERRIDE_COLS_UNTIL_2008
        if test_data.date.year <= 2008
        else OVERRIDE_COLS_AFTER_2008,
    )

    assert_series_equal(
        result[column],
        test_data.output_df[column],
        check_dtype=False,
        atol=1e-2,
        rtol=0,
    )
