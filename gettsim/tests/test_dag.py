import pytest

from gettsim.dag import fail_if_functions_and_user_columns_overlap
from gettsim.dag import fail_if_user_columns_are_not_in_data


def test_fail_if_user_columns_are_not_in_data():
    data = {}
    user_columns = [
        "aaaaaaaaaaaaaaaaaaaaaaaaaa",
        "bbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "cccccccccccccccccccccc",
    ]

    with pytest.raises(ValueError):
        fail_if_user_columns_are_not_in_data(data, user_columns)


@pytest.mark.parametrize("type_", ["user", "internal"])
def test_fail_if_user_functions_and_user_columns_overlap(type_):
    dict_ = {"a": None, "b": None, "c": None, "d": None}

    with pytest.raises(ValueError):
        fail_if_functions_and_user_columns_overlap(dict_, dict_, type_, [])
