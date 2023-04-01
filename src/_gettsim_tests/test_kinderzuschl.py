import pytest
from pandas.testing import assert_series_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import load_policy_test_data, PolicyTestData

OVERRIDE_COLS = [
    "_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh",
    "kindergeld_m_hh",
    "unterhaltsvors_m",
    "kinderzuschl_bruttoeink_eltern_m",
    "kinderzuschl_eink_eltern_m",
    "kindergeld_anspruch",
]

data = load_policy_test_data("kinderzuschl")

@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_kinderzuschl(
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
        result[column], test_data.output_df[column], check_dtype=False, atol=0, rtol=0
    )
