"""Some tests for the policy_environment module."""

from datetime import date, timedelta
from typing import Any

import optree
import pandas as pd
import pytest

from _gettsim.function_types import policy_function
from _gettsim.gettsim_typing import NestedFunctionDict
from _gettsim.policy_environment import (
    PolicyEnvironment,
    _fail_if_name_of_last_branch_element_not_leaf_name_of_function,
    _load_parameter_group_from_yaml,
    load_functions_tree_for_date,
    set_up_policy_environment,
)
from _gettsim_tests import TEST_DIR


class TestPolicyEnvironment:
    def test_func_exists_in_tree(self):
        function = policy_function(leaf_name="foo")(lambda: 1)
        environment = PolicyEnvironment({"foo": function})

        assert environment.functions_tree["foo"] == function

    def test_func_does_not_exist_in_tree(self):
        environment = PolicyEnvironment({}, {})

        assert "foo" not in environment.functions_tree

    @pytest.mark.parametrize(
        "environment",
        [
            PolicyEnvironment({}, {}),
            PolicyEnvironment({"foo": policy_function(leaf_name="foo")(lambda: 1)}),
            PolicyEnvironment(
                {
                    "foo": policy_function(leaf_name="foo")(lambda: 1),
                    "bar": policy_function(leaf_name="bar")(lambda: 2),
                }
            ),
        ],
    )
    def test_upsert_functions(self, environment: PolicyEnvironment):
        new_function = policy_function(leaf_name="foo")(lambda: 3)
        new_environment = environment.upsert_policy_functions({"foo": new_function})

        assert new_environment.functions_tree["foo"] == new_function

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


@pytest.mark.xfail(reason="Needs renamings PR.")
@pytest.mark.parametrize(
    "tree, last_day, function_name_last_day, function_name_next_day",
    [
        (
            {"einkommensteuer": {"freibeträge": {"altersfreibetrag_y": None}}},
            date(2004, 12, 31),
            "einkommensteuer__freibeträge__altersfreibetrag_y_bis_2004",
            "einkommensteuer__freibeträge__altersfreibetrag_y_ab_2005",
        ),
        (
            {"einkommensteuer": {"freibeträge": {"alleinerziehend_betrag_y": None}}},
            date(2014, 12, 31),
            "einkommensteuer__freibeträge__alleinerziehend_betrag_y_pauschal",
            "einkommensteuer__freibeträge__alleinerziehend_betrag_y_nach_kinderzahl",
        ),
        (
            {"einkommensteuer": {"einkünfte": {"gesamteinkünfte_y": None}}},
            date(2008, 12, 31),
            "einkommensteuer__einkommen__gesamteinkünfte_mit_kapitaleinkünfte_y",
            "einkommensteuer__einkommen__gesamteinkünfte_ohne_kapitaleinkünfte_y",
        ),
    ],
)
def test_load_functions_tree_for_date(
    tree: dict[str, Any],
    last_day: date,
    function_name_last_day: str,
    function_name_next_day: str,
):
    functions_last_day = load_functions_tree_for_date(date=last_day)
    functions_next_day = load_functions_tree_for_date(date=last_day + timedelta(days=1))

    accessor = optree.tree_accessors(tree, none_is_leaf=True)[0]

    assert accessor(functions_last_day).__name__ == function_name_last_day
    assert accessor(functions_next_day).__name__ == function_name_next_day


@pytest.mark.parametrize(
    "functions_tree",
    [
        {"foo": policy_function(leaf_name="bar")(lambda: 1)},
    ],
)
def test_fail_if_name_of_last_branch_element_not_leaf_name_of_function(
    functions_tree: NestedFunctionDict,
):
    with pytest.raises(KeyError):
        _fail_if_name_of_last_branch_element_not_leaf_name_of_function(functions_tree)
