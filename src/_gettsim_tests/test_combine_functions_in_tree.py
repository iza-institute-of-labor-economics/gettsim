import optree
import pandas as pd
import pytest

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.combine_functions_in_tree import (
    _annotations_for_aggregation,
    _create_aggregate_by_group_functions,
    _fail_if_targets_not_in_functions_tree,
    _get_path_from_argument_name,
)
from _gettsim.functions.derived_function import DerivedFunction
from _gettsim.functions.policy_function import PolicyFunction, policy_function


@pytest.fixture
@policy_function(leaf_name="foo")
def function_with_bool_return(x: bool) -> bool:
    return x


@pytest.fixture
@policy_function(leaf_name="bar")
def function_with_int_return(x: int) -> int:
    return x


@pytest.fixture
@policy_function(leaf_name="baz")
def function_with_float_return(x: int) -> float:
    return x


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
            # Aggregations derived from simple function arguments
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
            # Aggregations derived from namespaced function arguments
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
                        source_col="x",
                        aggr="sum",
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
    assert all(isinstance(func, PolicyFunction | DerivedFunction) for func in leafs)


@pytest.mark.parametrize(
    "argument_name, current_namespace, expected",
    [
        ("foo", ["dir", "module"], ("dir", "module", "foo")),
        ("dir__module__foo", ["dir", "module"], ("dir", "module", "foo")),
    ],
)
def test_get_path_from_argument_name(argument_name, current_namespace, expected):
    assert _get_path_from_argument_name(argument_name, current_namespace) == expected


@pytest.mark.parametrize(
    (
        "aggregation_method",
        "source_col",
        "functions_tree",
        "types_input_variables",
        "expected_return_type",
    ),
    [
        ("count", "foo", {}, {}, int),
        ("sum", "foo", {}, {"foo": float}, float),
        ("sum", "foo", {}, {"foo": int}, int),
        ("sum", "foo", {}, {"foo": bool}, int),
        ("sum", "foo", {"foo": function_with_bool_return}, {}, int),
        ("sum", "foo", {"foo": function_with_int_return}, {}, int),
        ("sum", "foo", {"foo": function_with_float_return}, {}, float),
    ],
)
def test_annotations_for_aggregation(
    aggregation_method,
    source_col,
    functions_tree,
    types_input_variables,
    expected_return_type,
):
    assert (
        _annotations_for_aggregation(
            aggregation_method, source_col, functions_tree, types_input_variables
        )["return"]
        == expected_return_type
    )


@pytest.mark.parametrize(
    "functions, targets, expected_error_match",
    [
        ({"foo": lambda x: x}, {"bar": None}, "bar"),
        ({"foo": {"baz": lambda x: x}}, {"foo": {"bar": None}}, "foo__bar"),
    ],
)
def test_fail_if_targets_are_not_among_functions(
    functions, targets, expected_error_match
):
    with pytest.raises(ValueError) as e:
        _fail_if_targets_not_in_functions_tree(functions, targets)
    assert expected_error_match in str(e.value)
