import pandas as pd
import pytest

from _gettsim.shared import parse_to_nested_dict


@pytest.mark.parametrize(
    "function_input, expected",
    [
        ("a", {"a": None}),
        ("a__b", {"a": {"b": None}}),
        (["a", "b"], {"a": None, "b": None}),
        (["a__b", "c__d"], {"a": {"b": None}, "c": {"d": None}}),
        (["a__b", "a__c"], {"a": {"b": None, "c": None}}),
        (["a__b", "a__c", "a__b__d"], {"a": {"b": {"d": None}, "c": None}}),
        ({"a": "b"}, {"a": "b"}),
    ],
)
def test_parse_to_nested_dict(function_input, expected):
    assert parse_to_nested_dict(function_input, name="_") == expected


@pytest.mark.parametrize(
    "input",
    [
        (pd.DataFrame()),
        (pd.Series()),
        (1),
    ],
)
def test_parse_to_nested_dict_type_error(function_input):
    with pytest.raises(NotImplementedError):
        parse_to_nested_dict(function_input, name="_")
