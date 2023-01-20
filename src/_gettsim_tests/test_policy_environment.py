"""Some tests for the policy_environment module."""
from datetime import date, timedelta
from typing import Callable

import pandas as pd
import pytest

from _gettsim.policy_environment import _load_parameter_group_from_yaml, load_functions_for_date
from _gettsim.policy_environment import set_up_policy_environment
from _gettsim.taxes.zu_verst_eink.eink import sum_eink_mit_kapital, sum_eink_ohne_kapital
from _gettsim.taxes.zu_verst_eink.freibetraege import eink_st_altersfreib_ab_2005, eink_st_altersfreib_bis_2004, \
    eink_st_alleinerz_freib_tu_bis_2014, eink_st_alleinerz_freib_tu_ab_2015
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
        group="test_access_diff_date",
        parameters=None,
        yaml_path=TEST_DIR / "test_parameters",
    )
    assert params["foo"] == 2020
    assert params["foo_vorjahr"] == 2019


# Passing callables as arguments to pytest.mark.parametrize fails with ValueError
# "parametrize() call in test_load_functions_for_date got an unexpected scope value",
# so I created individual test functions for each test case.

def test_load_functions_for_date_sum_eink():
    _helper_load_functions_for_date("sum_eink", date(2008, 12, 31), sum_eink_mit_kapital, sum_eink_ohne_kapital)


def test_load_functions_for_date_alleinerz_freib_tu():
    _helper_load_functions_for_date(
        "alleinerz_freib_tu",
        date(2014, 12, 31),
        eink_st_alleinerz_freib_tu_bis_2014,
        eink_st_alleinerz_freib_tu_ab_2015
    )


def test_load_functions_for_date_altersfreib():
    _helper_load_functions_for_date(
        "eink_st_altersfreib",
        date(2004, 12, 31),
        eink_st_altersfreib_bis_2004,
        eink_st_altersfreib_ab_2005
    )


def _helper_load_functions_for_date(
        function_name: str,
        last_day: date,
        function_last_day: Callable,
        function_next_day: Callable
):
    functions_last_day = load_functions_for_date(date=last_day)
    functions_next_day = load_functions_for_date(date=last_day + timedelta(days=1))

    assert functions_last_day[function_name] == function_last_day
    assert functions_next_day[function_name] == function_next_day
