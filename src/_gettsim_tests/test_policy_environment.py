"""Some tests for the policy_environment module."""

from datetime import date, timedelta

import pandas as pd
import pytest

from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.policy_environment import (
    _load_parameter_group_from_yaml,
    load_functions_for_date,
    set_up_policy_environment, PolicyEnvironment,
)
from _gettsim_tests import TEST_DIR


class TestPolicyEnvironment:
    def test_get_function_by_name_exists(self):
        function = PolicyFunction(lambda x: 1, function_name="foo")
        environment = PolicyEnvironment([function])

        assert environment.get_function_by_name("foo") == function

    def test_get_function_by_name_does_not_exist(self):
        environment = PolicyEnvironment([], {})

        assert environment.get_function_by_name("foo") is None

    @pytest.mark.parametrize(
        "environment",
        [
            PolicyEnvironment([], {}),
            PolicyEnvironment([
                PolicyFunction(lambda x: 1, function_name="foo"),
            ]),
            PolicyEnvironment([
                PolicyFunction(lambda x: 1, function_name="foo"),
                PolicyFunction(lambda x: 2, function_name="bar"),
            ]),
        ],
    )
    def test_upsert_functions(self, environment: PolicyEnvironment):
        new_function = PolicyFunction(lambda x: 3, function_name="foo")
        new_environment = environment.upsert_functions(new_function)

        assert new_environment.get_function_by_name("foo") == new_function

    @pytest.mark.parametrize(
        "environment",
        [
            PolicyEnvironment(
                [],
                {}
            ),
            PolicyEnvironment(
                [],
                {"foo": {"bar": 1}}
            ),
        ],
    )
    def test_replace_all_parameters(self, environment: PolicyEnvironment):
        new_params = {"foo": {"bar": 2}}
        new_environment = environment.replace_all_parameters(new_params)

        assert new_environment.params == new_params


def test_leap_year_correctly_handled():
    set_up_policy_environment(date="02-29-2020")


def test_fail_if_invalid_date():
    with pytest.raises(ValueError):
        set_up_policy_environment(date="02-30-2020")


def test_fail_if_invalid_access_different_date():
    with pytest.raises(ValueError):
        _load_parameter_group_from_yaml(
            date=pd.to_datetime("01-01-2020").date(),
            group="invalid_access_diff_date",
            parameters=None,
            yaml_path=TEST_DIR / "test_parameters",
        )


def test_access_different_date_vorjahr():
    params = _load_parameter_group_from_yaml(
        date=pd.to_datetime("01-01-2020").date(),
        group="test_access_diff_date_vorjahr",
        parameters=None,
        yaml_path=TEST_DIR / "test_parameters",
    )
    assert params["foo"] == 2020
    assert params["foo_vorjahr"] == 2019


def test_access_different_date_jahresanfang():
    params = _load_parameter_group_from_yaml(
        date=pd.to_datetime("07-01-2020").date(),
        group="test_access_diff_date_jahresanfang",
        parameters=None,
        yaml_path=TEST_DIR / "test_parameters",
    )
    assert params["foo"] == 2021
    assert params["foo_jahresanfang"] == 2020


@pytest.mark.parametrize(
    "dag_key, last_day, function_name_last_day, function_name_next_day",
    [
        (
            "eink_st_altersfreib_y",
            date(2004, 12, 31),
            "eink_st_altersfreib_y_bis_2004",
            "eink_st_altersfreib_y_ab_2005",
        ),
        (
            "alleinerz_freib_y_sn",
            date(2014, 12, 31),
            "eink_st_alleinerz_freib_y_sn_pauschal",
            "eink_st_alleinerz_freib_y_sn_nach_kinderzahl",
        ),
        (
            "sum_eink_y",
            date(2008, 12, 31),
            "sum_eink_mit_kapital_eink_y",
            "sum_eink_ohne_kapital_eink_y",
        ),
    ],
)
def test_load_functions_for_date(
    dag_key: str,
    last_day: date,
    function_name_last_day: str,
    function_name_next_day: str,
):
    functions_last_day = {
        f.name_in_dag: f.function for f in load_functions_for_date(date=last_day)
    }
    functions_next_day = {
        f.name_in_dag: f.function
        for f in load_functions_for_date(date=last_day + timedelta(days=1))
    }

    assert functions_last_day[dag_key].__name__ == function_name_last_day
    assert functions_next_day[dag_key].__name__ == function_name_next_day
