import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas import DataFrame
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

OVERRIDE_COLS = []

data = load_policy_test_data("st_id")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_st_id(
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
        result[column],
        test_data.output_df[column],
        check_dtype=False,
        atol=1e-1,
        rtol=0,
    )

def test_should_raise_if_gemeinsam_veranlagt_differs():
    df = DataFrame({
        "p_id": [0, 1],
        "p_id_ehepartner": [1, 0],
        "gemeinsam_veranlagt": [True, False]
    })

    policy_params, policy_functions = cached_set_up_policy_environment(
        date="2023"
    )

    with pytest.raises(
            ValueError,
            match=r"0 and 1 are married, but have different values for "
                  r"gemeinsam_veranlagt\."
    ):
        compute_taxes_and_transfers(
            data=df,
            params=policy_params,
            functions=policy_functions,
            targets="st_id",
            columns_overriding_functions=OVERRIDE_COLS,
        )
