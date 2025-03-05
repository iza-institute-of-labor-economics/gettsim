import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

OVERRIDE_COLS = []

data = load_policy_test_data("groupings")


@pytest.mark.xfail(reason="Needs renamings PR.")
@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_groupings(
    test_data: PolicyTestData,
    column: str,
):
    df = test_data.input_df
    environment = cached_set_up_policy_environment(date=test_data.date)

    result = compute_taxes_and_transfers(
        data=df,
        environment=environment,
        targets=column,
    )

    assert_series_equal(
        result[column],
        test_data.output_df[column],
        check_dtype=False,
        atol=1e-1,
        rtol=0,
    )


@pytest.mark.xfail(reason="Needs renamings PR.")
def test_fail_to_compute_sn_id_if_married_but_einkommensteuer__gemeinsam_veranlagt_differs():
    data = pd.DataFrame(
        {
            "p_id": [0, 1],
            "demograpics__p_id_ehepartner": [1, 0],
            "einkommensteuer__gemeinsam_veranlagt": [False, True],
        }
    )

    environment = cached_set_up_policy_environment(date="2023")

    with pytest.raises(
        ValueError,
        match="have different values for einkommensteuer__gemeinsam_veranlagt",
    ):
        compute_taxes_and_transfers(
            data=data,
            environment=environment,
            targets=["sn_id"],
        )
