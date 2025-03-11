import optree
import pandas as pd
import pytest

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.combine_functions_in_tree import (
    _annotations_for_aggregation,
    _create_aggregate_by_group_functions,
    _fail_if_targets_not_in_functions_tree,
    _get_tree_path_from_source_col_name,
)
from _gettsim.function_types import (
    DerivedFunction,
    PolicyFunction,
    policy_function,
)


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
            {"namespace1": {"f": policy_function(leaf_name="f")(lambda x_hh: x_hh)}},
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
                    "f": policy_function(leaf_name="f")(
                        lambda inputs__x_hh: inputs__x_hh
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
            {"namespace1": {"f": policy_function(leaf_name="f")(lambda x: x)}},
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
            {"namespace1": {"f": policy_function(leaf_name="f")(lambda y_hh: y_hh)}},
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
            {"namespace1": {"f": policy_function(leaf_name="f")(lambda y_hh: y_hh)}},
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
        targets_tree=targets_tree,
        data_tree=data_tree,
        aggregations_tree_provided_by_env=aggregations_specs_from_env,
    )

    # Verify structure
    existing_paths = optree.tree_paths(derived_functions)
    expected_paths = optree.tree_paths(expected_tree_structure, none_is_leaf=True)
    assert set(existing_paths) == set(expected_paths)

    assert all(
        isinstance(func, PolicyFunction | DerivedFunction)
        for func in optree.tree_leaves(derived_functions)
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
        "source_col",
        "namespace_of_function_to_derive",
        "functions_tree",
        "types_input_variables",
        "expected_return_type",
    ),
    [
        ("count", "foo", ("",), {}, {}, int),
        ("sum", "foo", ("namespace",), {}, {"namespace": {"foo": float}}, float),
        ("sum", "foo", ("namespace",), {}, {"namespace": {"foo": int}}, int),
        ("sum", "foo", ("namespace",), {}, {"namespace": {"foo": bool}}, int),
        (
            "sum",
            "foo",
            ("namespace",),
            {"namespace": {"foo": function_with_bool_return}},
            {},
            int,
        ),
        (
            "sum",
            "foo",
            ("namespace",),
            {"namespace": {"foo": function_with_int_return}},
            {},
            int,
        ),
        (
            "sum",
            "foo",
            ("namespace",),
            {"namespace": {"foo": function_with_float_return}},
            {},
            float,
        ),
        (
            "sum",
            "other_namespace__foo",
            ("namespace",),
            {"other_namespace": {"foo": function_with_bool_return}},
            {},
            int,
        ),
    ],
)
def test_annotations_for_aggregation(  # noqa: PLR0913
    aggregation_method,
    source_col,
    namespace_of_function_to_derive,
    functions_tree,
    types_input_variables,
    expected_return_type,
):
    assert (
        _annotations_for_aggregation(
            aggregation_method=aggregation_method,
            source_col=source_col,
            namespace=namespace_of_function_to_derive,
            functions_tree=functions_tree,
            types_input_variables=types_input_variables,
        )["return"]
        == expected_return_type
    )


@pytest.mark.parametrize(
    "functions, targets, expected_error_match",
    [
        ({"foo": lambda x: x}, {"bar": None}, "bar"),
        ({"foo": {"baz": lambda x: x}}, {"foo": {"bar": None}}, "foo.bar"),
    ],
)
def test_fail_if_targets_are_not_among_functions(
    functions, targets, expected_error_match
):
    with pytest.raises(ValueError) as e:
        _fail_if_targets_not_in_functions_tree(functions, targets)
    assert expected_error_match in str(e.value)
