import pandas as pd
import pytest

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.combine_functions_in_tree import (
    _annotations_for_aggregation,
    _fail_if_targets_not_in_functions_tree,
    _get_tree_path_from_source_col_name,
)
from _gettsim.function_types import (
    policy_function,
)
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import PolicyEnvironment


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
    ),
    [
        (
            # Aggregations derived from simple function arguments
            {"namespace1": {"f": policy_function(leaf_name="f")(lambda x_hh: x_hh)}},
            {"namespace1": {"f": None}},
            {
                "namespace1": {"x": pd.Series([1, 1, 1])},
                "demographics": {
                    "hh_id": pd.Series([0, 0, 0]),
                    "p_id": pd.Series([0, 1, 2]),
                },
            },
            {},
        ),
        (
            # Aggregations derived from namespaced function arguments
            {
                "namespace1": {
                    "f": policy_function(leaf_name="f")(
                        lambda inputs__x_hh: inputs__x_hh
                    )
                }
            },
            {"namespace1": {"f": None}},
            {
                "inputs": {"x": pd.Series([1, 1, 1])},
                "demographics": {
                    "hh_id": pd.Series([0, 0, 0]),
                    "p_id": pd.Series([0, 1, 2]),
                },
            },
            {},
        ),
        (
            # Aggregations derived from target
            {"namespace1": {"f": policy_function(leaf_name="f")(lambda x: x)}},
            {"namespace1": {"f_hh": None}},
            {
                "namespace1": {"x": pd.Series([1, 1, 1])},
                "demographics": {
                    "hh_id": pd.Series([0, 0, 0]),
                    "p_id": pd.Series([0, 1, 2]),
                },
            },
            {},
        ),
        (
            # Aggregations derived from simple environment specification
            {"namespace1": {"f": policy_function(leaf_name="f")(lambda y_hh: y_hh)}},
            {"namespace1": {"f": None}},
            {
                "namespace1": {"x": pd.Series([1, 1, 1])},
                "demographics": {
                    "hh_id": pd.Series([0, 0, 0]),
                    "p_id": pd.Series([0, 1, 2]),
                },
            },
            {
                "namespace1": {
                    "y_hh": AggregateByGroupSpec(
                        source_col="x",
                        aggr="sum",
                    ),
                },
            },
        ),
        (
            # Aggregations derived from namespaced environment specification
            {"namespace1": {"f": policy_function(leaf_name="f")(lambda y_hh: y_hh)}},
            {"namespace1": {"f": None}},
            {
                "inputs": {"x": pd.Series([1, 1, 1])},
                "demographics": {
                    "hh_id": pd.Series([0, 0, 0]),
                    "p_id": pd.Series([0, 1, 2]),
                },
            },
            {
                "namespace1": {
                    "y_hh": AggregateByGroupSpec(
                        source_col="inputs__x",
                        aggr="sum",
                    ),
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
):
    environment = PolicyEnvironment(
        functions_tree=functions_tree,
        aggregation_specs_tree=aggregations_specs_from_env,
    )
    compute_taxes_and_transfers(
        environment=environment,
        data_tree=data_tree,
        targets_tree=targets_tree,
    )


@pytest.mark.parametrize(
    "argument_name, current_namespace, expected",
    [
        ("foo", ("dir", "module"), ("dir", "module", "foo")),
        ("dir__module__foo", ("dir", "module"), ("dir", "module", "foo")),
    ],
)
def test_get_tree_path_from_source_col_name(argument_name, current_namespace, expected):
    assert (
        _get_tree_path_from_source_col_name(argument_name, current_namespace)
        == expected
    )


@pytest.mark.parametrize(
    (
        "aggregation_method",
        "path_to_source_col",
        "functions_tree",
        "types_input_variables",
        "expected_return_type",
    ),
    [
        ("count", ("foo",), {}, {}, int),
        ("sum", ("namespace", "foo"), {}, {"namespace": {"foo": float}}, float),
        ("sum", ("namespace", "foo"), {}, {"namespace": {"foo": int}}, int),
        ("sum", ("namespace", "foo"), {}, {"namespace": {"foo": bool}}, int),
        (
            "sum",
            ("namespace", "foo"),
            {"namespace": {"foo": function_with_bool_return}},
            {},
            int,
        ),
        (
            "sum",
            ("namespace", "foo"),
            {"namespace": {"foo": function_with_int_return}},
            {},
            int,
        ),
        (
            "sum",
            ("namespace", "foo"),
            {"namespace": {"foo": function_with_float_return}},
            {},
            float,
        ),
    ],
)
def test_annotations_for_aggregation(
    aggregation_method,
    path_to_source_col,
    functions_tree,
    types_input_variables,
    expected_return_type,
):
    assert (
        _annotations_for_aggregation(
            aggregation_method=aggregation_method,
            path_to_source_col=path_to_source_col,
            functions_tree=functions_tree,
            types_input_variables=types_input_variables,
        )["return"]
        == expected_return_type
    )


@pytest.mark.parametrize(
    "functions, targets, expected_error_match",
    [
        ({"foo": lambda x: x}, {"bar": None}, "bar"),
        ({"foo": {"baz": lambda x: x}}, {"foo": {"bar": None}}, "('foo', 'bar')"),
    ],
)
def test_fail_if_targets_are_not_among_functions(
    functions, targets, expected_error_match
):
    with pytest.raises(ValueError) as e:
        _fail_if_targets_not_in_functions_tree(functions, targets)
    assert expected_error_match in str(e.value)
