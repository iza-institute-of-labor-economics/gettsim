import itertools

import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas._testing import assert_frame_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]

data = load_policy_test_data("renten_alter")


@pytest.mark.parametrize(
    ("year", "test_data"),
    itertools.product(YEARS, data.test_data),
    ids=str,
)
def test_renten_alter(
    year: int,
    test_data: PolicyTestData,
):
    output_columns = test_data.output_df.columns

    df = test_data.input_df

    policy_params, policy_functions = cached_set_up_policy_environment(
        date=f"{year}-07-01"
    )

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=output_columns,
    )
    assert_frame_equal(
        calc_result[output_columns], test_data.output_df, atol=1e-1, rtol=0
    )
