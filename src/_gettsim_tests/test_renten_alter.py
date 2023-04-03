import itertools

import pytest
from pandas.testing import assert_series_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import load_policy_test_data, PolicyTestData

YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]

data = load_policy_test_data("renten_alter")


@pytest.mark.parametrize(
    ("year", "parametrize_arg"),
    itertools.product(YEARS, data.parametrize_args),
    ids=str,
)
def test_renten_alter(
        year: int,
        parametrize_arg: tuple[PolicyTestData, str],
):
    test_data, column = parametrize_arg

    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=f"{year}-07-01"
    )

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
    )
    assert_series_equal(calc_result[column], test_data.output_df[column], atol=1e-1, rtol=0)
