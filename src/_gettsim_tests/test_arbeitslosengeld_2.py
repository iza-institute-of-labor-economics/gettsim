import dags.tree as dt
import pytest
from numpy.testing import assert_array_almost_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTest, load_policy_test_data

test_data = load_policy_test_data("arbeitslosengeld_2")


@pytest.mark.parametrize("test", test_data)
def test_arbeitslosengeld_2(test: PolicyTest):
    environment = cached_set_up_policy_environment(date=test.date)

    result = compute_taxes_and_transfers(
        data_tree=test.input_tree,
        environment=environment,
        targets_tree=test.target_structure,
    )

    flat_result = dt.flatten_to_qual_names(result)
    flat_expected_output_tree = dt.flatten_to_qual_names(test.expected_output_tree)

    for result, expected in zip(
        flat_result.values(), flat_expected_output_tree.values()
    ):
        assert_array_almost_equal(result, expected, decimal=2)
