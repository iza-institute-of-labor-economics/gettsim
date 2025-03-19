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


test_data = load_policy_test_data("zu_versteuerndes_einkommen")


@pytest.mark.parametrize(
    "test",
    test_data,
)
def test_zu_versteuerndes_einkommen(
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
