"""Some tests for the policy_environment module."""

from datetime import date, timedelta

import pandas as pd
import pytest

from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.policy_environment import (
    PolicyEnvironment,
    _load_parameter_group_from_yaml,
    load_functions_tree_for_date,
    set_up_policy_environment,
)
from _gettsim.shared import (
    tree_to_dict_with_qualified_name,
)
from _gettsim_tests import TEST_DIR


class TestPolicyEnvironment:
    def test_func_exists_in_tree(self):
        function = PolicyFunction(lambda: 1)
        environment = PolicyEnvironment({"foo": function})

        assert environment.policy_functions_tree["foo"] == function

    def test_func_does_not_exist_in_tree(self):
        environment = PolicyEnvironment({}, {})

        assert "foo" not in environment.policy_functions_tree

    @pytest.mark.parametrize(
        "environment",
        [
            PolicyEnvironment({}, {}),
            PolicyEnvironment({"foo": PolicyFunction(lambda: 1)}),
            PolicyEnvironment(
                {
                    "foo": PolicyFunction(lambda: 1),
                    "bar": PolicyFunction(lambda: 2),
                }
            ),
        ],
    )
    def test_upsert_functions(self, environment: PolicyEnvironment):
        new_function = PolicyFunction(lambda: 3)
        new_environment = environment.upsert_functions({"foo": new_function})

        assert new_environment.policy_functions_tree["foo"] == new_function

    @pytest.mark.parametrize(
        "environment",
        [
            PolicyEnvironment({}, {}),
            PolicyEnvironment({}, {"foo": {"bar": 1}}),
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
    "qualified_name, last_day, function_name_last_day, function_name_next_day",
    [
        (
            "zu_verst_eink__freibetraege__eink_st_altersfreib_y",
            date(2004, 12, 31),
            "eink_st_altersfreib_y_bis_2004",
            "eink_st_altersfreib_y_ab_2005",
        ),
        (
            "zu_verst_eink__freibetraege__alleinerz_freib_y_sn",
            date(2014, 12, 31),
            "eink_st_alleinerz_freib_y_sn_pauschal",
            "eink_st_alleinerz_freib_y_sn_nach_kinderzahl",
        ),
        (
            "zu_verst_eink__eink__sum_eink_y",
            date(2008, 12, 31),
            "sum_eink_mit_kapital_eink_y",
            "sum_eink_ohne_kapital_eink_y",
        ),
    ],
)
def test_load_functions_tree_for_date(
    qualified_name: str,
    last_day: date,
    function_name_last_day: str,
    function_name_next_day: str,
):
    functions_last_day = tree_to_dict_with_qualified_name(
        load_functions_tree_for_date(date=last_day)
    )
    functions_next_day = tree_to_dict_with_qualified_name(
        load_functions_tree_for_date(date=last_day + timedelta(days=1))
    )

    assert functions_last_day[qualified_name].__name__ == function_name_last_day
    assert functions_next_day[qualified_name].__name__ == function_name_next_day
