import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

OVERRIDE_COLS = [
    "soli_st_tu",
    "sozialv_beitr_m",
    "eink_st_tu",
]


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
    """Run tests to validate elterngeld.

    hh_id 7 in test cases is for the calculator on
    https://familienportal.de/familienportal/meta/egr. The calculator's result is 10
    Euro off GETTSIM's result. We need to discuss if we should adapt the calculation of
    the proxy wage of last year or anything else.

    """
    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    df["soli_st_tu"] = df["soli_st_m"].groupby(df["tu_id"]).transform("sum") * 12
    df["eink_st_tu"] = df["eink_st_m"].groupby(df["tu_id"]).transform("sum") * 12

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=OVERRIDE_COLS,
    )

    assert_series_equal(
        result[column],
        test_data.output_df[column],
        check_dtype=False,
        atol=1e-1,
        rtol=0,
    )
