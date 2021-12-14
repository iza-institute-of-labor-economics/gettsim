import numpy as np
import pandas as pd
import pytest

from gettsim import compute_taxes_and_transfers
from gettsim import set_up_policy_environment
from gettsim.shared import add_rounding_spec


@pytest.mark.parametrize(
    "base, direction", [(1, "up"), (0.1, "down"), (5, "nearest")],
)
def test_attribute_for_rounding(base, direction):
    @add_rounding_spec(base, direction)
    def func():
        return 0

    assert func.__roundingspec__["base"] == base
    assert func.__roundingspec__["direction"] == direction


@pytest.mark.parametrize(
    "base, direction", [(1, "upper"), ("0.1", "down"), (5, "closest")],
)
def test_fail_if_wrong_attribute_for_rounding(base, direction):
    """Wrong inputs"""
    with pytest.raises(ValueError):

        @add_rounding_spec(base, direction)
        def func():
            return 0


@pytest.mark.parametrize(
    "base, direction, input_values, exp_output",
    [
        (1, "up", [100.24, 100.78], [101.0, 101.0]),
        (1, "down", [100.24, 100.78], [100.0, 100.0]),
        (1, "nearest", [100.24, 100.78], [100.0, 101.0]),
        (5, "up", [100.24, 100.78], [105.0, 105.0]),
        (0.1, "down", [100.24, 100.78], [100.2, 100.7]),
        (0.001, "nearest", [100.24, 100.78], [100.24, 100.78]),
    ],
)
def test_rounding(base, direction, input_values, exp_output):
    """Check if rounding is correct"""
    # Define function that should be rounded
    @add_rounding_spec(base=base, direction=direction)
    def foo(income):
        return income

    # Check if function is rounded as expected
    data = pd.DataFrame([{"p_id": 1}, {"p_id": 2}])
    data["income"] = input_values
    policy_params, policy_functions = set_up_policy_environment("2020")

    calc_result = compute_taxes_and_transfers(
        data=data,
        functions=[policy_functions, foo],
        params=policy_params,
        targets=["foo"],
    )
    np.array_equal(calc_result["foo"].values, np.array(exp_output))


@pytest.mark.parametrize(
    "base, direction, input_values, exp_output",
    [
        (5, "up", [100.24, 100.78], [100.24, 100.78]),
        (1, "down", [100.24, 100.78], [100.24, 100.78]),
        (1, "nearest", [100.24, 100.78], [100.24, 100.78]),
    ],
)
def test_no_rounding(base, direction, input_values, exp_output):
    """Check if no rounding if disabled"""
    # Define function that should be rounded
    @add_rounding_spec(base=base, direction=direction)
    def foo(income):
        return income

    # Check if function is not rounded as expected
    data = pd.DataFrame([{"p_id": 1}, {"p_id": 2}])
    data["income"] = input_values
    policy_params, policy_functions = set_up_policy_environment("2020")

    calc_result = compute_taxes_and_transfers(
        data=data,
        functions=[policy_functions, foo],
        params=policy_params,
        targets=["foo"],
        rounding=False,
    )
    np.array_equal(calc_result["foo"].values, np.array(exp_output))


def test_fail_if_wrong_attribute_during_rounding():
    def foo(income):
        return income

    # assign wrong attribute
    foo.__roundingspec__ = {"base": 0.1, "direction": "wrong_direction"}

    # Check if function failes as expected
    data = pd.DataFrame([{"p_id": 1}, {"p_id": 2}])
    data["income"] = 1
    policy_params, policy_functions = set_up_policy_environment("2020")
    with pytest.raises(
        ValueError, match="direction must be one ",
    ):
        compute_taxes_and_transfers(
            data=data,
            functions=[policy_functions, foo],
            params=policy_params,
            targets=["foo"],
        )


def test_fail_if_incomplete_attributes_during_rounding():
    def foo(income):
        return income

    # assign incomplete attribute
    foo.__roundingspec__ = {"base": 0.1}

    # Check if function failes as expected
    data = pd.DataFrame([{"p_id": 1}, {"p_id": 2}])
    data["income"] = 1
    policy_params, policy_functions = set_up_policy_environment("2020")
    with pytest.raises(
        ValueError, match="If roundingspec is set to a function, both",
    ):
        compute_taxes_and_transfers(
            data=data,
            functions=[policy_functions, foo],
            params=policy_params,
            targets=["foo"],
        )
