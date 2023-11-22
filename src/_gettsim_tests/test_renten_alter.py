import itertools

import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas._testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import load_policy_test_data

YEARS = [
    2014,
    2015,
    2016,
    2017,
]

data = load_policy_test_data("renten_alter")
merged_input_df = data.merged_input_df()
merged_output_df = data.merged_output_df()
targets = merged_output_df.columns


@pytest.mark.parametrize(
    ("year", "target"),
    itertools.product(YEARS, targets),
    ids=str,
)
def test_renten_alter(
    year: int,
    target: str,
):
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=f"{year}-07-01"
    )

    calc_result = compute_taxes_and_transfers(
        data=merged_input_df,
        params=policy_params,
        functions=policy_functions,
        targets=targets,
    )
    assert_series_equal(
        calc_result[target], merged_output_df[target], atol=1e-1, rtol=0
    )
