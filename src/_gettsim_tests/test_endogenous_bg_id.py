import pandas as pd
import pytest
from _gettsim.endogenous_bg_id import determine_bg_and_wthh_ids
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

data = load_policy_test_data("endogenous_bg_id")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_endogenous_bg_ids(
    test_data: PolicyTestData,
    column: str,
):
    """Test creation of endogenous bg_ids and wthh_id."""
    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    bg_id, wthh_id, wohngeld_günstiger_als_sgb_ii = determine_bg_and_wthh_ids(
        data=df, params=policy_params, functions=policy_functions
    )

    result = pd.DataFrame(
        {
            "bg_id": bg_id,
            "wthh_id": wthh_id,
            "wohngeld_günstiger_als_sgb_ii": wohngeld_günstiger_als_sgb_ii,
        }
    ).sort_index()

    assert_series_equal(
        result[column],
        test_data.output_df[column],
        check_dtype=False,
        check_names=False,
        check_index=False,
        atol=1e-1,
        rtol=0,
    )
