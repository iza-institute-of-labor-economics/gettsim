"""Some tests for the policy_environment module."""

from datetime import date, timedelta

import pandas as pd
import pytest

from _gettsim.policy_environment import (
    _load_parameter_group_from_yaml,
    load_functions_for_date,
    set_up_policy_environment,
)
from _gettsim_tests import TEST_DIR


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
    functions_last_day = load_functions_for_date(date=last_day)
    functions_next_day = load_functions_for_date(date=last_day + timedelta(days=1))

    assert functions_last_day[dag_key].__name__ == function_name_last_day
    assert functions_next_day[dag_key].__name__ == function_name_next_day
