from dataclasses import dataclass

import pytest

from _gettsim.shared import (
    create_tree_from_path_and_value,
    get_group_by_id_path,
    insert_path_and_value,
    merge_trees,
    partition_tree_by_reference_tree,
    upsert_path_and_value,
    upsert_tree,
)


@dataclass
class SampleDataClass:
    a: int


@pytest.mark.parametrize(
    "base, path_to_upsert, value_to_upsert, expected",
    [
        ({}, ["a"], 1, {"a": 1}),
        ({"a": 1}, ["a"], 2, {"a": 2}),
        ({}, ["a", "b"], 2, {"a": {"b": 2}}),
        ({"a": {"b": 1}}, ["a", "c"], 2, {"a": {"b": 1, "c": 2}}),
    ],
)
def test_upsert_path_and_value(base, path_to_upsert, value_to_upsert, expected):
    result = upsert_path_and_value(
        base=base, path_to_upsert=path_to_upsert, value_to_upsert=value_to_upsert
    )
    assert result == expected


@pytest.mark.parametrize(
    "base, path_to_insert, value_to_insert, expected",
    [
        ({}, ("a",), 1, {"a": 1}),
        ({"a": 1}, ("b",), 2, {"a": 1, "b": 2}),
    ],
)
def test_insert_path_and_value(base, path_to_insert, value_to_insert, expected):
    result = insert_path_and_value(
        base=base, path_to_insert=path_to_insert, value_to_insert=value_to_insert
    )
    assert result == expected


@pytest.mark.parametrize(
    "base, path_to_insert, value_to_insert",
    [
        ({"a": 1}, ("a",), 2),
    ],
)
def test_insert_path_and_value_invalid(base, path_to_insert, value_to_insert):
    with pytest.raises(ValueError, match="Conflicting paths in trees to merge."):
        insert_path_and_value(
            base=base, path_to_insert=path_to_insert, value_to_insert=value_to_insert
        )


@pytest.mark.parametrize(
    "paths, expected",
    [
        ("a", {"a": None}),
        (("a", "b"), {"a": {"b": None}}),
        (("a", "b", "c"), {"a": {"b": {"c": None}}}),
    ],
)
def test_create_tree_from_path_and_value(paths, expected):
    assert create_tree_from_path_and_value(paths) == expected


@pytest.mark.parametrize(
    "left, right, expected",
    [
        ({}, {"a": 1}, {"a": 1}),
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 1, "c": 2}}),
        ({"a": {"b": 1}}, {"a": 3}, {"a": 3}),
        ({"a": 3}, {"a": {"b": 1}}, {"a": {"b": 1}}),
        ({"a": SampleDataClass(a=1)}, {}, {"a": SampleDataClass(a=1)}),
    ],
)
def test_merge_trees_valid(left, right, expected):
    assert merge_trees(left=left, right=right) == expected


@pytest.mark.parametrize(
    "left, right",
    [({"a": 1}, {"a": 2}), ({"a": 1}, {"a": 1}), ({"a": {"b": 1}}, {"a": {"b": 5}})],
)
def test_merge_trees_invalid(left, right):
    with pytest.raises(ValueError, match="Conflicting paths in trees to merge."):
        merge_trees(left=left, right=right)


@pytest.mark.parametrize(
    "base_dict, update_dict, expected",
    [
        ({}, {"a": 1}, {"a": 1}),
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        ({"a": 1}, {"a": 2}, {"a": 2}),
        ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 1, "c": 2}}),
        ({"a": {"b": 1}}, {"a": 3}, {"a": 3}),
        ({"a": 3}, {"a": {"b": 1}}, {"a": {"b": 1}}),
        ({"a": SampleDataClass(a=1)}, {}, {"a": SampleDataClass(a=1)}),
    ],
)
def test_upsert_tree(base_dict, update_dict, expected):
    assert upsert_tree(base=base_dict, to_upsert=update_dict) == expected


@pytest.mark.parametrize(
    "tree_to_partition, reference_tree, expected",
    [
        (
            {
                "a": {
                    "b": 1,
                    "c": 1,
                },
                "b": 1,
            },
            {
                "a": {
                    "b": 1,
                },
                "b": 1,
            },
            (
                {"a": {"b": 1}, "b": 1},
                {"a": {"c": 1}},
            ),
        ),
        (
            {
                "a": {
                    "c": 1,
                },
            },
            {},
            (
                {},
                {"a": {"c": 1}},
            ),
        ),
        (
            {
                "a": {
                    "b": None,
                    "c": None,
                },
                "b": None,
            },
            {
                "a": {
                    "b": None,
                },
                "b": None,
            },
            (
                {"a": {"b": None}, "b": None},
                {"a": {"c": None}},
            ),
        ),
    ],
)
def test_partition_tree_by_reference_tree(tree_to_partition, reference_tree, expected):
    in_reference_tree, not_in_reference_tree = partition_tree_by_reference_tree(
        tree_to_partition=tree_to_partition, reference_tree=reference_tree
    )

    assert in_reference_tree == expected[0]
    assert not_in_reference_tree == expected[1]


@pytest.mark.parametrize(
    "target_path, group_by_functions_tree, expected",
    [
        (("namespace1", "foo_hh"), {}, ("demographics", "hh_id")),
        (
            ("namespace1", "foo_hh"),
            {"namespace1": {"hh_id": None}},
            ("demographics", "hh_id"),
        ),
        (
            ("namespace1", "foo_bg"),
            {"arbeitslosengeld_2": {"bg_id": None}},
            ("arbeitslosengeld_2", "bg_id"),
        ),
        (
            ("namespace1", "foo_eg"),
            {"grundsicherung": {"eg_id": None}},
            ("grundsicherung", "eg_id"),
        ),
        (
            ("namespace1", "foo_eg"),
            {"arbeitslosengeld_2": {"eg_id": None}},
            ("arbeitslosengeld_2", "eg_id"),
        ),
    ],
)
def test_get_group_by_id_path(target_path, group_by_functions_tree, expected):
    assert get_group_by_id_path(target_path, group_by_functions_tree) == expected


@pytest.mark.parametrize(
    "target_path, group_by_functions_tree, expected_error_match",
    [
        (
            ("namespace1", "foo_bg"),
            {
                "namespace1": {
                    "bg_id": None,
                    "namespace2": {
                        "bg_id": None,
                    },
                },
            },
            "Grouping ID for target namespace1.foo_bg is ambiguous.",
        ),
    ],
)
def test_get_group_by_id_path_fails(
    target_path, group_by_functions_tree, expected_error_match
):
    with pytest.raises(ValueError) as e:
        get_group_by_id_path(target_path, group_by_functions_tree)
    assert expected_error_match in str(e.value)
