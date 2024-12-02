import pytest

from _gettsim.shared import (
    create_dict_from_list,
    merge_nested_dicts,
)


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
