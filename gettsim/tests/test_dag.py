import pytest

from gettsim.dag import fail_if_user_columns_are_not_in_data
from gettsim.dag import fail_if_user_functions_and_user_columns_overlap


def test_fail_if_user_columns_are_not_in_data():
    data = {}
    user_columns = ["a"]

    with pytest.raises(ValueError):
        fail_if_user_columns_are_not_in_data(data, user_columns)


def test_fail_if_user_functions_and_user_columns_overlap():
    func_dict = {"a": None}
    data = {"a": None}

    with pytest.raises(ValueError):
        fail_if_user_functions_and_user_columns_overlap(data, func_dict)
