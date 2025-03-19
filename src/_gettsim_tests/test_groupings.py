from typing import TYPE_CHECKING

import dags.tree as dt
import pytest
from numpy.testing import assert_array_almost_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTest, load_policy_test_data

if TYPE_CHECKING:
    import datetime

    from _gettsim.gettsim_typing import NestedDataDict, NestedInputStructureDict


test_data = load_policy_test_data("groupings")


@pytest.mark.parametrize(
    "test",
    test_data,
)
def test_groupings(
    test: PolicyTest,
):
    date: datetime.date = test.date
    input_tree: NestedDataDict = test.input_tree
    expected_output_tree: NestedDataDict = test.expected_output_tree
    target_structure: NestedInputStructureDict = test.target_structure

    environment = cached_set_up_policy_environment(date=date)

    result = compute_taxes_and_transfers(
        data_tree=input_tree, environment=environment, targets_tree=target_structure
    )

    flat_result = dt.flatten_to_qual_names(result)
    flat_expected_output_tree = dt.flatten_to_qual_names(expected_output_tree)

    for result, expected in zip(
        flat_result.values(), flat_expected_output_tree.values()
    ):
        assert_array_almost_equal(result, expected, decimal=2)


def test_fail_to_compute_sn_id_if_married_but_gemeinsam_veranlagt_differs():
    data = {
        "demographics": {
            "p_id": [0, 1],
            "p_id_ehepartner": [1, 0],
        },
        "einkommensteuer": {
            "gemeinsam_veranlagt": [False, True],
        },
    }

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
