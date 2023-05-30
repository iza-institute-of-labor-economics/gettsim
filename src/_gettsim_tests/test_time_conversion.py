import pytest
from _gettsim.time_conversion import (
    d_to_y,
    m_to_d,
    m_to_w,
    m_to_y,
    w_to_d,
    w_to_m,
    w_to_y,
    y_to_d,
    y_to_m,
    y_to_w, d_to_m, d_to_w,
)


@pytest.mark.parametrize(
    ("yearly_value", "monthly_value"),
    [
        (0, 0),
        (12, 1),
    ]
)
def test_y_to_m(yearly_value: float, monthly_value: float) -> None:
    assert y_to_m(yearly_value) == monthly_value


@pytest.mark.parametrize(
    ("yearly_value", "weekly_value"),
    [
        (0, 0),
        (365.25, 7),
    ]
)
def test_y_to_w(yearly_value: float, weekly_value: float) -> None:
    assert y_to_w(yearly_value) == weekly_value


@pytest.mark.parametrize(
    ("yearly_value", "daily_value"),
    [
        (0, 0),
        (365.25, 1),
    ]
)
def test_y_to_d(yearly_value: float, daily_value: float) -> None:
    assert y_to_d(yearly_value) == daily_value


@pytest.mark.parametrize(
    ("monthly_value", "yearly_value"),
    [
        (0, 0),
        (1, 12),
    ]
)
def test_m_to_y(monthly_value: float, yearly_value: float) -> None:
    assert m_to_y(monthly_value) == yearly_value


@pytest.mark.parametrize(
    ("monthly_value", "weekly_value"),
    [
        (0, 0),
        (365.25, 84),
    ]
)
def test_m_to_w(monthly_value: float, weekly_value: float) -> None:
    assert m_to_w(monthly_value) == weekly_value


@pytest.mark.parametrize(
    ("monthly_value", "daily_value"),
    [
        (0, 0),
        (365.25, 12),
    ]
)
def test_m_to_d(monthly_value: float, daily_value: float) -> None:
    assert m_to_d(monthly_value) == daily_value


@pytest.mark.parametrize(
    ("weekly_value", "yearly_value"),
    [
        (0, 0),
        (7, 365.25),
    ]
)
def test_w_to_y(weekly_value: float, yearly_value: float) -> None:
    assert w_to_y(weekly_value) == yearly_value


@pytest.mark.parametrize(
    ("weekly_value", "monthly_value"),
    [
        (0, 0),
        (84, 365.25),
    ]
)
def test_w_to_m(weekly_value: float, monthly_value: float) -> None:
    assert w_to_m(weekly_value) == monthly_value


@pytest.mark.parametrize(
    ("weekly_value", "daily_value"),
    [
        (0, 0),
        (7, 1),
    ]
)
def test_w_to_d(weekly_value: float, daily_value: float) -> None:
    assert w_to_d(weekly_value) == daily_value


@pytest.mark.parametrize(
    ("daily_value", "yearly_value"),
    [
        (0, 0),
        (1, 365.25),
    ]
)
def test_d_to_y(daily_value: float, yearly_value: float) -> None:
    assert d_to_y(daily_value) == yearly_value


@pytest.mark.parametrize(
    ("daily_value", "monthly_value"),
    [
        (0, 0),
        (12, 365.25),
    ]
)
def test_d_to_m(daily_value: float, monthly_value: float) -> None:
    assert d_to_m(daily_value) == monthly_value


@pytest.mark.parametrize(
    ("daily_value", "weekly_value"),
    [
        (0, 0),
        (1, 7),
    ]
)
def test_d_to_w(daily_value: float, weekly_value: float) -> None:
    assert d_to_w(daily_value) == weekly_value
