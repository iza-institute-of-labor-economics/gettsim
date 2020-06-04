from contextlib import contextmanager

import pytest

from gettsim.interface import _fail_if_functions_and_columns_overlap
from gettsim.interface import _fail_if_user_columns_are_not_in_data
from gettsim.interface import _fail_if_user_columns_are_not_in_functions


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "data, user_columns, expectation",
    [
        ({}, ["not_in_data"], pytest.raises(ValueError)),
        ({"in_data": None}, ["in_data"], does_not_raise()),
    ],
)
def test_fail_if_user_columns_are_not_in_data(data, user_columns, expectation):
    with expectation:
        _fail_if_user_columns_are_not_in_data(data, user_columns)


@pytest.mark.parametrize(
    "user_columns, internal_functions, user_functions, expectation",
    [
        (["not_in_functions"], {}, {}, pytest.raises(ValueError)),
        (["in_functions"], {"in_functions": None}, {}, does_not_raise()),
        (["in_functions"], {}, {"in_functions": None}, does_not_raise()),
    ],
)
def test_fail_if_user_columns_are_not_in_functions(
    user_columns, internal_functions, user_functions, expectation
):
    with expectation:
        _fail_if_user_columns_are_not_in_functions(
            user_columns, internal_functions, user_functions
        )


@pytest.mark.parametrize(
    "data, functions, type_, user_columns, expectation",
    [
        ({"dupl": None}, {"dupl": None}, "internal", [], pytest.raises(ValueError)),
        ({}, {}, "internal", [], does_not_raise()),
        ({"dupl": None}, {"dupl": None}, "user", [], pytest.raises(ValueError)),
        ({}, {}, "user", [], does_not_raise()),
    ],
)
def test_fail_if_functions_and_columns_overlap(
    data, functions, type_, user_columns, expectation
):
    with expectation:
        _fail_if_functions_and_columns_overlap(data, functions, type_, user_columns)
