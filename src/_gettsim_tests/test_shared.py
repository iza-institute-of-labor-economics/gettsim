import pandas as pd
import pytest

from _gettsim.shared import (
    create_nested_dict,
    dissect_string_to_dict,
    parse_input_to_nested_dict,
)


@pytest.mark.parametrize(
    "function_input, separator, expected",
    [
        ("a", "__", {"a": None}),
        ("a__b", "__", {"a": {"b": None}}),
        (["a", "b"], "__", {"a": None, "b": None}),
        (["a__b", "c__d"], "__", {"a": {"b": None}, "c": {"d": None}}),
        (["a__b", "a__c"], "__", {"a": {"b": None, "c": None}}),
        (["a.b", "a.c", "a.b.d"], ".", {"a": {"b": {"d": None}, "c": None}}),
        ({"a": "b"}, "__", {"a": "b"}),
    ],
)
def test_parse_input_to_nested_dict(function_input, separator, expected):
    assert parse_input_to_nested_dict(function_input, separator, name="_") == expected


@pytest.mark.parametrize(
    "function_input",
    [
        (pd.DataFrame()),
        (pd.Series()),
        (1),
    ],
)
def test_parse_input_to_nested_dict_type_error(function_input):
    with pytest.raises(NotImplementedError):
        parse_input_to_nested_dict(function_input, separator=".", name="_")


@pytest.mark.parametrize(
    "keys, expected",
    [
        ("a", {"a": None}),
        (["a", "b"], {"a": {"b": None}}),
        (["a", "b", "c"], {"a": {"b": {"c": None}}}),
    ],
)
def test_dissect_string_to_dict(keys, expected):
    assert dissect_string_to_dict(keys=keys) == expected


@pytest.mark.parametrize(
    "base_dict, update_dict, expected",
    [
        ({}, {"a": 1}, {"a": 1}),
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        ({"a": 1}, {"a": 2}, {"a": 2}),
        ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 1, "c": 2}}),
    ],
)
def test_create_nested_dict(base_dict, update_dict, expected):
    assert create_nested_dict(base_dict, update_dict) == expected
