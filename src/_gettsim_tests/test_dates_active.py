import datetime

import pytest
from _gettsim.shared import (
    TIME_DEPENDENT_FUNCTIONS,
    ConflictingTimeDependentFunctionsError,
    dates_active,
)


@pytest.fixture(autouse=True)
def _setup_and_teardown():
    # Invoke test
    yield

    # Tear down
    TIME_DEPENDENT_FUNCTIONS.clear()


# Start date -----------------------------------------------


@pytest.mark.parametrize(
    "date_string, expected",
    [
        ("2023-01-20", datetime.date(2023, 1, 20)),
    ],
)
def test_dates_active_start_date_valid(date_string: str, expected: datetime.date):
    @dates_active(start=date_string)
    def test_func():
        pass

    assert test_func.__info__["dates_active_start"] == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "20230120",
        "20.1.2023",
        "20th January 2023",
    ],
)
def test_dates_active_start_date_invalid(date_string: str):
    with pytest.raises(ValueError):

        @dates_active(start=date_string)
        def test_func():
            pass


def test_dates_active_start_date_missing():
    @dates_active()
    def test_func():
        pass

    assert test_func.__info__["dates_active_start"] == datetime.date(1, 1, 1)


# End date -------------------------------------------------


@pytest.mark.parametrize(
    "date_string, expected",
    [
        ("2023-01-20", datetime.date(2023, 1, 20)),
    ],
)
def test_dates_active_end_date_valid(date_string: str, expected: datetime.date):
    @dates_active(end=date_string)
    def test_func():
        pass

    assert test_func.__info__["dates_active_end"] == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "20230120",
        "20.1.2023",
        "20th January 2023",
    ],
)
def test_dates_active_end_date_invalid(date_string: str):
    with pytest.raises(ValueError):

        @dates_active(end=date_string)
        def test_func():
            pass


def test_dates_active_end_date_missing():
    @dates_active()
    def test_func():
        pass

    assert test_func.__info__["dates_active_end"] == datetime.date(9999, 12, 31)


# Change name ----------------------------------------------


def test_dates_active_change_name_given():
    @dates_active(change_name="renamed_func")
    def test_func():
        pass

    assert test_func.__info__["dates_active_dag_key"] == "renamed_func"


def test_dates_active_change_name_missing():
    @dates_active()
    def test_func():
        pass

    assert test_func.__info__["dates_active_dag_key"] == "test_func"


# Empty interval -------------------------------------------


def test_dates_active_empty_interval():
    with pytest.raises(ValueError):

        @dates_active(start="2023-01-20", end="2023-01-19")
        def test_func():
            pass


# Conflicts ------------------------------------------------


@pytest.mark.parametrize(
    "dag_key_1, start_1, end_1, dag_key_2, start_2, end_2",
    [
        ("func_1", "2023-01-01", "2023-01-31", "func_2", "2023-01-01", "2023-01-31"),
        ("func_1", "2023-01-01", "2023-01-31", "func_1", "2023-02-01", "2023-02-28"),
        ("func_1", "2023-02-01", "2023-02-28", "func_1", "2023-01-01", "2023-01-31"),
    ],
)
def test_dates_active_no_conflict(  # noqa: PLR0913
    dag_key_1: str,
    start_1: str,
    end_1: str,
    dag_key_2: str,
    start_2: str,
    end_2: str,
):
    @dates_active(change_name=dag_key_1, start=start_1, end=end_1)
    def func_1():
        pass

    # Using the decorator again should not raise an error
    @dates_active(change_name=dag_key_2, start=start_2, end=end_2)
    def func_2():
        pass


@pytest.mark.parametrize(
    "start_1, end_1, start_2, end_2",
    [
        ("2023-01-01", "2023-01-31", "2023-01-01", "2023-01-31"),
        ("2023-01-01", "2023-01-31", "2022-01-02", "2023-01-30"),
        ("2023-01-02", "2023-01-30", "2022-01-01", "2023-01-31"),
        ("2023-01-01", "2023-01-31", "2022-01-02", "2023-02-01"),
        ("2023-01-02", "2023-02-01", "2022-01-01", "2023-01-31"),
    ],
)
def test_dates_active_conflict(
    start_1: str,
    end_1: str,
    start_2: str,
    end_2: str,
):
    @dates_active(change_name="func_1", start=start_1, end=end_1)
    def func_1():
        pass

    # Using the decorator again should raise an error
    with pytest.raises(ConflictingTimeDependentFunctionsError):

        @dates_active(change_name="func_1", start=start_2, end=end_2)
        def func_2():
            pass
