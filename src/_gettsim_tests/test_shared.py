from dataclasses import dataclass

import pytest

from _gettsim.shared import (
    create_tree_from_path,
    create_tree_from_qualified_names,
    partition_tree_by_reference_tree,
    tree_merge,
    tree_update,
)


@dataclass
class SampleDataclass:
    a: int


def test_create_tree_from_qualified_names():
    qualified_names = {"a__b__c", "a__b__d", "a__e"}
    tree = create_tree_from_qualified_names(qualified_names)
    assert tree == {"a": {"b": {"c": None, "d": None}, "e": None}}


@pytest.mark.parametrize(
    "tree, path, value, expected",
    [
        ({}, ["a"], 1, {"a": 1}),
        ({"a": 1}, ["a"], 2, {"a": 2}),
        ({}, ["a", "b"], 2, {"a": {"b": 2}}),
        ({"a": {"b": 1}}, ["a", "c"], 2, {"a": {"b": 1, "c": 2}}),
    ],
)
def test_tree_update(tree, path, value, expected):
    result = tree_update(tree, path, value)
    assert result == expected


@pytest.mark.parametrize(
    "paths, expected",
    [
        ("a", {"a": None}),
        (("a", "b"), {"a": {"b": None}}),
        (("a", "b", "c"), {"a": {"b": {"c": None}}}),
    ],
)
def test_create_tree_from_path(paths, expected):
    assert create_tree_from_path(paths) == expected


@pytest.mark.parametrize(
    "base_dict, update_dict, expected",
    [
        ({}, {"a": 1}, {"a": 1}),
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        ({"a": 1}, {"a": 2}, {"a": 2}),
        ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 1, "c": 2}}),
        ({"a": SampleDataclass(a=1)}, {}, {"a": SampleDataclass(a=1)}),
    ],
)
def test_tree_merge(base_dict, update_dict, expected):
    assert tree_merge(base_dict, update_dict) == expected


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
