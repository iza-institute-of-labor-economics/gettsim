import pytest

from _gettsim.shared import (
    create_dict_from_list,
    merge_nested_dicts,
    tree_to_dict_with_qualified_name,
    tree_update,
)


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
    "keys, expected",
    [
        ("a", {"a": None}),
        (["a", "b"], {"a": {"b": None}}),
        (["a", "b", "c"], {"a": {"b": {"c": None}}}),
    ],
)
def test_create_dict_from_list(keys, expected):
    assert create_dict_from_list(keys=keys) == expected


@pytest.mark.parametrize(
    "base_dict, update_dict, expected",
    [
        ({}, {"a": 1}, {"a": 1}),
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        ({"a": 1}, {"a": 2}, {"a": 2}),
        ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 1, "c": 2}}),
    ],
)
def test_merge_nested_dicts(base_dict, update_dict, expected):
    assert merge_nested_dicts(base_dict, update_dict) == expected


@pytest.mark.parametrize(
    "tree, expected",
    [
        ({"a": 1}, {"a": 1}),
        ({"a": {"b": 1}}, {"a__b": 1}),
        ({"a": {"b": {"c": 1}, "d": 2}}, {"a__b__c": 1, "a__d": 2}),
    ],
)
def test_tree_flatten_with_qualified_name(tree, expected):
    leafs_names_dict = tree_to_dict_with_qualified_name(tree)
    assert leafs_names_dict == expected
