"""Some tests for the policy_environment module."""
import pandas as pd
import pytest
from gettsim.config import ROOT_DIR
from gettsim.policy_environment import _load_parameter_group_from_yaml
from gettsim.policy_environment import set_up_policy_environment


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
            yaml_path=ROOT_DIR / "tests" / "test_parameters",
        )


def test_access_different_date_vorjahr():
    params = _load_parameter_group_from_yaml(
        date=pd.to_datetime("01-01-2020").date(),
        group="test_access_diff_date",
        parameters=None,
        yaml_path=ROOT_DIR / "tests" / "test_parameters",
    )
    assert params["foo"] == 2020
    assert params["foo_vorjahr"] == 2019
