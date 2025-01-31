import optree
import pandas as pd
import pytest

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.policy_environment_postprocessor import (
    _create_aggregate_by_group_functions,
    _get_qualified_source_col_name,
)


@pytest.mark.parametrize(
    (
        "functions_tree",
        "targets_tree",
        "data_tree",
        "aggregations_specs_from_env",
        "expected_tree_structure",
    ),
    [
        (
            # Aggregations derived from namespaced function arguments
            {
                "namespace1": {
                    "f": PolicyFunction(
                        lambda x_hh: x_hh,
                        leaf_name="f",
                    )
                }
            },
            {"namespace1": {"f": None}},
            {
                "namespace1": {"x": pd.Series([1, 1, 1])},
                "groupings": {"hh_id": pd.Series([0, 0, 0])},
            },
            {},
            {
                "namespace1": {
                    "x_hh": None,
                },
            },
        ),
        (
            # Aggregations derived from simple function arguments
            {
                "namespace1": {
                    "f": PolicyFunction(
                        lambda inputs__x_hh: inputs__x_hh,
                        leaf_name="f",
                    )
                }
            },
            {"namespace1": {"f": None}},
            {
                "inputs": {"x": pd.Series([1, 1, 1])},
                "groupings": {"hh_id": pd.Series([0, 0, 0])},
            },
            {},
            {
                "inputs": {
                    "x_hh": None,
                },
            },
        ),
        (
            # Aggregations derived from target
            {
                "namespace1": {
                    "f": PolicyFunction(
                        lambda x: x,
                        leaf_name="f",
                    )
                }
            },
            {"namespace1": {"f_hh": None}},
            {
                "namespace1": {"x": pd.Series([1, 1, 1])},
                "groupings": {"hh_id": pd.Series([0, 0, 0])},
            },
            {},
            {
                "namespace1": {
                    "f_hh": None,
                },
            },
        ),
        (
            # Aggregations derived from simple environment specification
            {
                "namespace1": {
                    "f": PolicyFunction(
                        lambda y_hh: y_hh,
                        leaf_name="f",
                    )
                }
            },
            {"namespace1": {"f": None}},
            {
                "namespace1": {"x": pd.Series([1, 1, 1])},
                "groupings": {"hh_id": pd.Series([0, 0, 0])},
            },
            {
                "namespace1": {
                    "y_hh": AggregateByGroupSpec(
                        source_col="namespace1__x",
                        aggr="sum",
                        target_name="y_hh",
                    ),
                },
            },
            {
                "namespace1": {
                    "y_hh": None,
                },
            },
        ),
        (
            # Aggregations derived from namespaced environment specification
            {
                "namespace1": {
                    "f": PolicyFunction(
                        lambda y_hh: y_hh,
                        leaf_name="f",
                    )
                }
            },
            {"namespace1": {"f": None}},
            {
                "inputs": {"x": pd.Series([1, 1, 1])},
                "groupings": {"hh_id": pd.Series([0, 0, 0])},
            },
            {
                "namespace1": {
                    "y_hh": AggregateByGroupSpec(
                        source_col="inputs__x",
                        aggr="sum",
                        target_name="y_hh",
                    ),
                },
            },
            {
                "namespace1": {
                    "y_hh": None,
                },
            },
        ),
    ],
)
def test_create_aggregate_by_group_functions(
    functions_tree,
    targets_tree,
    data_tree,
    aggregations_specs_from_env,
    expected_tree_structure,
):
    derived_functions = _create_aggregate_by_group_functions(
        functions_tree=functions_tree,
        targets=targets_tree,
        data=data_tree,
        aggregation_dicts_provided_by_env=aggregations_specs_from_env,
    )

    # Verify structure
    accessors = optree.tree_accessors(expected_tree_structure, none_is_leaf=True)

    # Raises key error if path does not exist
    leafs = [acc(derived_functions) for acc in accessors]

    assert all(optree.tree_is_leaf(leaf) for leaf in leafs)


def test_get_qualified_source_col_name():
    assert _get_qualified_source_col_name(["foo", "bar", "baz_hh"]) == "foo__bar__baz"
    assert _get_qualified_source_col_name(["foo", "bar", "baz_eg"]) == "foo__bar__baz"
