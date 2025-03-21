from datetime import timedelta

import dags.tree as dt
import pytest
from numpy.testing import assert_array_almost_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTest, load_policy_test_data

grundrente_test_data = load_policy_test_data("grundrente")
proxy_rente_test_data = load_policy_test_data("grundrente_proxy_rente")


@pytest.mark.parametrize(
    "test",
    grundrente_test_data,
)
def test_grundrente(test: PolicyTest):
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
        assert_array_almost_equal(result, expected, decimal=0)


@pytest.mark.parametrize(
    "test",
    proxy_rente_test_data,
)
def test_grundrente_proxy_rente(test: PolicyTest):
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
        assert_array_almost_equal(result, expected, decimal=0)


@pytest.mark.parametrize(
    "test",
    proxy_rente_test_data,
)
def test_grundrente_proxy_rente_vorjahr_comparison(test: PolicyTest):
    environment = cached_set_up_policy_environment(date=test.date)

    result = compute_taxes_and_transfers(
        data_tree=test.input_tree,
        environment=environment,
        targets_tree={
            "sozialversicherung": {
                "rente": {"grundrente": {"proxy_rente_vorjahr_m": None}}
            }
        },
    )

    # Calculate pension of last year
    environment = cached_set_up_policy_environment(test.date - timedelta(days=365))
    test.input_tree["demographics"]["alter"] -= 1
    result_previous_year = compute_taxes_and_transfers(
        data_tree=test.input_tree,
        environment=environment,
        targets_tree={
            "sozialversicherung": {"rente": {"altersrente": {"bruttorente_m": None}}}
        },
    )

    flat_result = dt.flatten_to_qual_names(result)
    flat_result_previous_year = dt.flatten_to_qual_names(result_previous_year)
    flat_inputs = dt.flatten_to_qual_names(test.input_tree)
    assert_array_almost_equal(
        flat_result["sozialversicherung__rente__grundrente__proxy_rente_vorjahr_m"],
        flat_result_previous_year[
            "sozialversicherung__rente__altersrente__bruttorente_m"
        ]
        + flat_inputs["sozialversicherung__rente__private_rente_betrag_m"],
        decimal=2,
    )
