import dags.tree as dt
import pytest

from _gettsim.config import TYPES_INPUT_VARIABLES
from _gettsim.gettsim_typing import check_series_has_expected_type
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTest, load_policy_test_data

test_data = load_policy_test_data("full_taxes_and_transfers")


@pytest.mark.parametrize("test", test_data)
def test_full_taxes_transfers(test: PolicyTest):
    environment = cached_set_up_policy_environment(date=test.date)

    compute_taxes_and_transfers(
        data_tree=test.input_tree,
        environment=environment,
        targets_tree=test.target_structure,
    )


@pytest.mark.parametrize("test", test_data)
def test_data_types(test: PolicyTest):
    environment = cached_set_up_policy_environment(date=test.date)

    result = compute_taxes_and_transfers(
        data_tree=test.input_tree,
        environment=environment,
        targets_tree=test.target_structure,
    )

    flat_types_input_variables = dt.flatten_to_qual_names(TYPES_INPUT_VARIABLES)
    flat_functions = dt.flatten_to_qual_names(environment.functions_tree)

    for column_name, result_array in dt.flatten_to_qual_names(result).items():
        if column_name in flat_types_input_variables:
            internal_type = flat_types_input_variables[column_name]
        elif column_name in flat_functions:
            internal_type = flat_functions[column_name].__annotations__["return"]
        else:
            # TODO (@hmgaudecker): Implement easy way to find out expected type of
            #     aggregated functions
            # https://github.com/iza-institute-of-labor-economics/gettsim/issues/604
            if column_name.endswith(("_sn", "_hh", "_fg", "_bg", "_eg", "_ehe")):
                internal_type = None
            else:
                raise ValueError(f"Column name {column_name} unknown.")
        if internal_type:
            assert check_series_has_expected_type(result_array, internal_type)


@pytest.mark.parametrize("test", test_data)
def test_allow_none_as_target_tree(test: PolicyTest):
    environment = cached_set_up_policy_environment(date=test.date)

    compute_taxes_and_transfers(
        data_tree=test.input_tree,
        environment=environment,
        targets_tree=None,
    )
