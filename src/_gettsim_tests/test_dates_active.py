import datetime

import pytest

from _gettsim.functions.loader import (
    ConflictingTimeDependentFunctionsError,
    _fail_if_multiple_policy_functions_are_active_at_the_same_time,
)
from _gettsim.functions.policy_function import policy_function

# Start date -----------------------------------------------


@pytest.mark.parametrize(
    "date_string, expected",
    [
        ("2023-01-20", datetime.date(2023, 1, 20)),
    ],
)
def test_start_date_valid(date_string: str, expected: datetime.date):
    @policy_function(start_date=date_string)
    def test_func():
        pass

    assert test_func.start_date == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "20230120",
        "20.1.2023",
        "20th January 2023",
    ],
)
def test_start_date_invalid(date_string: str):
    with pytest.raises(ValueError):

        @policy_function(start_date=date_string)
        def test_func():
            pass


def test_start_date_missing():
    @policy_function()
    def test_func():
        pass

    assert test_func.start_date == datetime.date(1900, 1, 1)


# End date -------------------------------------------------


@pytest.mark.parametrize(
    "date_string, expected",
    [
        ("2023-01-20", datetime.date(2023, 1, 20)),
    ],
)
def test_end_date_valid(date_string: str, expected: datetime.date):
    @policy_function(end_date=date_string)
    def test_func():
        pass

    assert test_func.end_date == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "20230120",
        "20.1.2023",
        "20th January 2023",
    ],
)
def test_end_date_invalid(date_string: str):
    with pytest.raises(ValueError):

        @policy_function(end_date=date_string)
        def test_func():
            pass


def test_end_date_missing():
    @policy_function()
    def test_func():
        pass

    assert test_func.end_date == datetime.date(2100, 12, 31)


# Change name ----------------------------------------------


def test_dates_active_change_name_given():
    @policy_function(leaf_name="renamed_func")
    def test_func():
        pass

    assert test_func.leaf_name == "renamed_func"


def test_dates_active_change_name_missing():
    @policy_function()
    def test_func():
        pass

    assert test_func.leaf_name == "test_func"


# Empty interval -------------------------------------------


def test_dates_active_empty_interval():
    with pytest.raises(ValueError):

        @policy_function(start_date="2023-01-20", end_date="2023-01-19")
        def test_func():
            pass


# Conflicts ------------------------------------------------


@pytest.mark.parametrize(
    "functions",
    [
        [
            policy_function(
                start_date="2023-01-01",
                end_date="2023-01-31",
                leaf_name="f",
            )(lambda x: x),
            policy_function(
                start_date="2023-02-01",
                end_date="2023-02-28",
                leaf_name="f",
            )(lambda x: x),
        ],
        [
            policy_function(
                start_date="2023-01-01",
                end_date="2023-01-31",
                leaf_name="f",
            )(lambda x: x),
            policy_function(
                start_date="2023-01-01",
                end_date="2023-02-28",
                leaf_name="g",
            )(lambda x: x),
        ],
    ],
)
def test_dates_active_no_conflicts(functions):
    _fail_if_multiple_policy_functions_are_active_at_the_same_time(
        policy_functions=functions, module_name=""
    )


@pytest.mark.parametrize(
    "functions",
    [
        [
            policy_function(
                start_date="2023-01-01",
                end_date="2023-01-31",
                leaf_name="f",
            )(lambda x: x),
            policy_function(
                start_date="2023-01-01",
                end_date="2023-01-31",
                leaf_name="f",
            )(lambda x: x),
        ],
        [
            policy_function(
                start_date="2023-01-01",
                end_date="2023-01-31",
                leaf_name="f",
            )(lambda x: x),
            policy_function(
                start_date="2021-01-02",
                end_date="2023-02-01",
                leaf_name="f",
            )(lambda x: x),
        ],
        [
            policy_function(
                start_date="2023-01-02",
                end_date="2023-02-01",
                leaf_name="f",
            )(lambda x: x),
            policy_function(
                start_date="2022-01-01",
                end_date="2023-01-31",
                leaf_name="f",
            )(lambda x: x),
        ],
    ],
)
def test_dates_active_with_conflicts(functions):
    with pytest.raises(ConflictingTimeDependentFunctionsError):
        _fail_if_multiple_policy_functions_are_active_at_the_same_time(
            policy_functions=functions, module_name=""
        )
