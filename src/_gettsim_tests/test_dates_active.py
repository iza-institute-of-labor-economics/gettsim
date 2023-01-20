import datetime

import pytest

from _gettsim.shared import dates_active


# Start date -----------------------------------------------

@pytest.mark.parametrize(
    "date_string, expected",
    [
        ("2023-01-20", datetime.datetime(2023, 1, 20)),
        ("20230120", datetime.datetime(2023, 1, 20)),
    ]
)
def test_dates_active_start_date_valid(date_string: str, expected: datetime.date):
    @dates_active(start=date_string)
    def test_func():
        pass

    assert test_func.__dates_active_start__ == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "20.1.2023",
        "20th January 2023",
    ]
)
def test_dates_active_start_date_invalid(date_string: str):
    with pytest.raises(ValueError):
        @dates_active(start=date_string)
        def test_func():
            pass


# End date -------------------------------------------------

def test_dates_active_start_date_missing():
    @dates_active()
    def test_func():
        pass

    assert test_func.__dates_active_start__ == datetime.datetime(1, 1, 1)


@pytest.mark.parametrize(
    "date_string, expected",
    [
        ("2023-01-20", datetime.datetime(2023, 1, 20)),
        ("20230120", datetime.datetime(2023, 1, 20)),
    ]
)
def test_dates_active_end_date_valid(date_string: str, expected: datetime.date):
    @dates_active(end=date_string)
    def test_func():
        pass

    assert test_func.__dates_active_end__ == expected


@pytest.mark.parametrize(
    "date_string",
    [
        "20.1.2023",
        "20th January 2023",
    ]
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

    assert test_func.__dates_active_end__ == datetime.datetime(9999, 12, 31)


# Change name ----------------------------------------------

def test_dates_active_change_name_given():
    @dates_active(change_name="renamed_func")
    def test_func():
        pass

    assert test_func.__dates_active_dag_key__ == "renamed_func"


def test_dates_active_change_name_missing():
    @dates_active()
    def test_func():
        pass

    assert test_func.__dates_active_dag_key__ == "test_func"
