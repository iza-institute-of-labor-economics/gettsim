import inspect

import pytest
from optree import tree_paths

from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.time_conversion import (
    _create_function_for_time_unit,
    create_time_conversion_functions,
    d_to_m,
    d_to_w,
    d_to_y,
    m_to_d,
    m_to_w,
    m_to_y,
    w_to_d,
    w_to_m,
    w_to_y,
    y_to_d,
    y_to_m,
    y_to_w,
)


@pytest.mark.parametrize(
    ("yearly_value", "monthly_value"),
    [
        (0, 0),
        (12, 1),
    ],
)
def test_y_to_m(yearly_value: float, monthly_value: float) -> None:
    assert y_to_m(yearly_value) == monthly_value


@pytest.mark.parametrize(
    ("yearly_value", "weekly_value"),
    [
        (0, 0),
        (365.25, 7),
    ],
)
def test_y_to_w(yearly_value: float, weekly_value: float) -> None:
    assert y_to_w(yearly_value) == weekly_value


@pytest.mark.parametrize(
    ("yearly_value", "daily_value"),
    [
        (0, 0),
        (365.25, 1),
    ],
)
def test_y_to_d(yearly_value: float, daily_value: float) -> None:
    assert y_to_d(yearly_value) == daily_value


@pytest.mark.parametrize(
    ("monthly_value", "yearly_value"),
    [
        (0, 0),
        (1, 12),
    ],
)
def test_m_to_y(monthly_value: float, yearly_value: float) -> None:
    assert m_to_y(monthly_value) == yearly_value


@pytest.mark.parametrize(
    ("monthly_value", "weekly_value"),
    [
        (0, 0),
        (365.25, 84),
    ],
)
def test_m_to_w(monthly_value: float, weekly_value: float) -> None:
    assert m_to_w(monthly_value) == weekly_value


@pytest.mark.parametrize(
    ("monthly_value", "daily_value"),
    [
        (0, 0),
        (365.25, 12),
    ],
)
def test_m_to_d(monthly_value: float, daily_value: float) -> None:
    assert m_to_d(monthly_value) == daily_value


@pytest.mark.parametrize(
    ("weekly_value", "yearly_value"),
    [
        (0, 0),
        (7, 365.25),
    ],
)
def test_w_to_y(weekly_value: float, yearly_value: float) -> None:
    assert w_to_y(weekly_value) == yearly_value


@pytest.mark.parametrize(
    ("weekly_value", "monthly_value"),
    [
        (0, 0),
        (84, 365.25),
    ],
)
def test_w_to_m(weekly_value: float, monthly_value: float) -> None:
    assert w_to_m(weekly_value) == monthly_value


@pytest.mark.parametrize(
    ("weekly_value", "daily_value"),
    [
        (0, 0),
        (7, 1),
    ],
)
def test_w_to_d(weekly_value: float, daily_value: float) -> None:
    assert w_to_d(weekly_value) == daily_value


@pytest.mark.parametrize(
    ("daily_value", "yearly_value"),
    [
        (0, 0),
        (1, 365.25),
    ],
)
def test_d_to_y(daily_value: float, yearly_value: float) -> None:
    assert d_to_y(daily_value) == yearly_value


@pytest.mark.parametrize(
    ("daily_value", "monthly_value"),
    [
        (0, 0),
        (12, 365.25),
    ],
)
def test_d_to_m(daily_value: float, monthly_value: float) -> None:
    assert d_to_m(daily_value) == monthly_value


@pytest.mark.parametrize(
    ("daily_value", "weekly_value"),
    [
        (0, 0),
        (1, 7),
    ],
)
def test_d_to_w(daily_value: float, weekly_value: float) -> None:
    assert d_to_w(daily_value) == weekly_value


class TestCreateFunctionsForTimeUnits:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("test_y", ["test_m", "test_w", "test_d"]),
            ("test_y_hh", ["test_m_hh", "test_w_hh", "test_d_hh"]),
            ("test_y_sn", ["test_m_sn", "test_w_sn", "test_d_sn"]),
            ("test_m", ["test_y", "test_w", "test_d"]),
            ("test_m_hh", ["test_y_hh", "test_w_hh", "test_d_hh"]),
            ("test_m_sn", ["test_y_sn", "test_w_sn", "test_d_sn"]),
            ("test_w", ["test_y", "test_m", "test_d"]),
            ("test_w_hh", ["test_y_hh", "test_m_hh", "test_d_hh"]),
            ("test_w_sn", ["test_y_sn", "test_m_sn", "test_d_sn"]),
            ("test_d", ["test_y", "test_m", "test_w"]),
            ("test_d_hh", ["test_y_hh", "test_m_hh", "test_w_hh"]),
            ("test_d_sn", ["test_y_sn", "test_m_sn", "test_w_sn"]),
        ],
    )
    def test_should_create_functions_for_other_time_units_for_functions(
        self, name: str, expected: list[str]
    ) -> None:
        time_conversion_functions = create_time_conversion_functions(
            {name: PolicyFunction(function=lambda: 1, leaf_name="test")}, {}
        )

        for expected_name in expected:
            assert expected_name in time_conversion_functions

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("test_y", ["test_m", "test_w", "test_d"]),
            ("test_y_hh", ["test_m_hh", "test_w_hh", "test_d_hh"]),
            ("test_y_sn", ["test_m_sn", "test_w_sn", "test_d_sn"]),
            ("test_m", ["test_y", "test_w", "test_d"]),
            ("test_m_hh", ["test_y_hh", "test_w_hh", "test_d_hh"]),
            ("test_m_sn", ["test_y_sn", "test_w_sn", "test_d_sn"]),
            ("test_w", ["test_y", "test_m", "test_d"]),
            ("test_w_hh", ["test_y_hh", "test_m_hh", "test_d_hh"]),
            ("test_w_sn", ["test_y_sn", "test_m_sn", "test_d_sn"]),
            ("test_d", ["test_y", "test_m", "test_w"]),
            ("test_d_hh", ["test_y_hh", "test_m_hh", "test_w_hh"]),
            ("test_d_sn", ["test_y_sn", "test_m_sn", "test_w_sn"]),
        ],
    )
    def test_should_create_functions_for_other_time_units_for_data_cols(
        self, name: str, expected: list[str]
    ) -> None:
        time_conversion_functions = create_time_conversion_functions({}, {name: None})

        for expected_name in expected:
            assert expected_name in time_conversion_functions

    def test_should_not_create_functions_automatically_that_exist_already(self) -> None:
        time_conversion_functions = create_time_conversion_functions(
            {"test1_d": PolicyFunction(function=lambda: 1, leaf_name="test1_d")},
            {"test2_y": None},
        )

        assert "test1_d" not in time_conversion_functions
        assert "test2_y" not in time_conversion_functions

    def test_should_overwrite_functions_with_data_cols_that_only_differ_in_time_period(
        self,
    ) -> None:
        time_conversion_functions = create_time_conversion_functions(
            {"test_d": PolicyFunction(function=lambda: 1, leaf_name="test_d")},
            {"test_y": None},
        )

        assert "test_d" in time_conversion_functions

    @pytest.mark.parametrize(
        "functions_tree, expected",
        [
            (
                {
                    "module1": {
                        "function1_y": PolicyFunction(
                            function=lambda: 1, leaf_name="function1_y"
                        )
                    }
                },
                {
                    "module1": {
                        "function1_m": PolicyFunction(
                            function=lambda: 1, leaf_name="function1_m"
                        ),
                        "function1_w": PolicyFunction(
                            function=lambda: 1, leaf_name="function1_w"
                        ),
                        "function1_d": PolicyFunction(
                            function=lambda: 1, leaf_name="function1_d"
                        ),
                    },
                },
            ),
            (
                {
                    "module1": {
                        "module2": {
                            "function1_y_hh": PolicyFunction(
                                function=lambda: 1, leaf_name="function1_y_hh"
                            )
                        }
                    }
                },
                {
                    "module1": {
                        "module2": {
                            "function1_m_hh": PolicyFunction(
                                function=lambda: 1, leaf_name="function1_m_hh"
                            ),
                            "function1_w_hh": PolicyFunction(
                                function=lambda: 1, leaf_name="function1_w_hh"
                            ),
                            "function1_d_hh": PolicyFunction(
                                function=lambda: 1, leaf_name="function1_d_hh"
                            ),
                        },
                    },
                },
            ),
        ],
    )
    def test_should_return_nested_dict(self, functions_tree, expected) -> None:
        time_conversion_functions = create_time_conversion_functions(functions_tree, {})

        expected_path = tree_paths(expected)
        result_path = tree_paths(time_conversion_functions)

        assert expected_path == result_path


class TestCreateFunctionForTimeUnit:
    def test_should_rename_parameter(self):
        function = _create_function_for_time_unit("test", d_to_m)

        parameter_spec = inspect.getfullargspec(function)
        assert parameter_spec.args == ["test"]

    def test_should_not_set_info_if_none(self):
        function = _create_function_for_time_unit("test", d_to_m)

        assert not hasattr(function, "__info__")

    def test_should_apply_converter(self):
        function = _create_function_for_time_unit("test", d_to_w)

        assert function(1) == 7


# https://github.com/iza-institute-of-labor-economics/gettsim/issues/621
def test_should_not_create_cycle():
    time_conversion_functions = create_time_conversion_functions(
        {"test_d": PolicyFunction(function=lambda test_m: test_m, leaf_name="test_d")},
        {},
    )

    assert "test_m" not in time_conversion_functions
