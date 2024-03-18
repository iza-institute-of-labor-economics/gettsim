import datetime

import pandas as pd
import pytest
import yaml
from pandas._testing import assert_series_equal

from _gettsim.config import (
    INTERNAL_PARAMS_GROUPS,
    PATHS_TO_INTERNAL_FUNCTIONS,
    RESOURCE_DIR,
)
from _gettsim.config import numpy_or_jax as np
from _gettsim.functions_loader import _load_functions
from _gettsim.interface import (
    _add_rounding_to_functions,
    _add_rounding_to_one_function,
    compute_taxes_and_transfers,
)
from _gettsim.policy_environment import load_functions_for_date
from _gettsim.shared import add_rounding_spec

rounding_specs_and_exp_results = [
    (1, "up", None, [100.24, 100.78], [101.0, 101.0]),
    (1, "down", None, [100.24, 100.78], [100.0, 100.0]),
    (1, "nearest", None, [100.24, 100.78], [100.0, 101.0]),
    (5, "up", None, [100.24, 100.78], [105.0, 105.0]),
    (0.1, "down", None, [100.24, 100.78], [100.2, 100.7]),
    (0.001, "nearest", None, [100.24, 100.78], [100.24, 100.78]),
    (1, "up", 10, [100.24, 100.78], [111.0, 111.0]),
    (1, "down", 10, [100.24, 100.78], [110.0, 110.0]),
    (1, "nearest", 10, [100.24, 100.78], [110.0, 111.0]),
]


def test_decorator():
    @add_rounding_spec(params_key="params_key_test")
    def test_func():
        return 0

    assert test_func.__info__["rounding_params_key"] == "params_key_test"


@pytest.mark.parametrize(
    "rounding_specs",
    [
        {},
        {"params_key_test": {}},
        {"params_key_test": {"rounding": {}}},
        {"params_key_test": {"rounding": {"test_func": {}}}},
    ],
)
def test_no_rounding_specs(rounding_specs):
    with pytest.raises(KeyError):

        @add_rounding_spec(params_key="params_key_test")
        def test_func():
            return 0

        compute_taxes_and_transfers(
            data=pd.DataFrame([{"p_id": 1}, {"p_id": 2}]),
            params=rounding_specs,
            functions=[test_func],
            targets=["test_func"],
        )


@pytest.mark.parametrize(
    "base, direction, to_add_after_rounding",
    [
        (1, "upper", 0),
        ("0.1", "down", 0),
        (5, "closest", 0),
        (5, "up", "0"),
    ],
)
def test_rounding_specs_wrong_format(base, direction, to_add_after_rounding):
    with pytest.raises(ValueError):

        @add_rounding_spec(params_key="params_key_test")
        def test_func():
            return 0

        rounding_specs = {
            "params_key_test": {
                "rounding": {
                    "test_func": {
                        "base": base,
                        "direction": direction,
                        "to_add_after_rounding": to_add_after_rounding,
                    }
                }
            }
        }

        compute_taxes_and_transfers(
            data=pd.DataFrame([{"p_id": 1}, {"p_id": 2}]),
            params=rounding_specs,
            functions=[test_func],
            targets=["test_func"],
        )


@pytest.mark.parametrize(
    "base, direction, to_add_after_rounding, input_values, exp_output",
    rounding_specs_and_exp_results,
)
def test_rounding(base, direction, to_add_after_rounding, input_values, exp_output):
    """Check if rounding is correct."""

    # Define function that should be rounded
    @add_rounding_spec(params_key="params_key_test")
    def test_func(income):
        return income

    data = pd.DataFrame([{"p_id": 1}, {"p_id": 2}])
    data["income"] = input_values
    rounding_specs = {
        "params_key_test": {
            "rounding": {
                "test_func": {
                    "base": base,
                    "direction": direction,
                }
            }
        }
    }

    if to_add_after_rounding:
        rounding_specs["params_key_test"]["rounding"]["test_func"][
            "to_add_after_rounding"
        ] = to_add_after_rounding

    calc_result = compute_taxes_and_transfers(
        data=data, params=rounding_specs, functions=[test_func], targets=["test_func"]
    )
    assert_series_equal(calc_result["test_func"], pd.Series(exp_output), check_names=False)


@pytest.mark.parametrize(
    "base, direction, to_add_after_rounding, input_values_exp_output, _ignore",
    rounding_specs_and_exp_results,
)
def test_no_rounding(
    base, direction, to_add_after_rounding, input_values_exp_output, _ignore
):
    # Define function that should be rounded
    @add_rounding_spec(params_key="params_key_test")
    def test_func(income):
        return income

    data = pd.DataFrame([{"p_id": 1}, {"p_id": 2}])
    data["income"] = input_values_exp_output
    rounding_specs = {
        "params_key_test": {
            "rounding": {"test_func": {"base": base, "direction": direction}}
        }
    }

    if to_add_after_rounding:
        rounding_specs["params_key_test"]["rounding"]["test_func"][
            "to_add_after_rounding"
        ] = to_add_after_rounding

    calc_result = compute_taxes_and_transfers(
        data=data,
        params=rounding_specs,
        functions=[test_func],
        targets=["test_func"],
        rounding=False
    )
    assert_series_equal(calc_result["test_func"], pd.Series(input_values_exp_output), check_names=False)


@pytest.mark.parametrize(
    "base, direction, to_add_after_rounding, input_values, exp_output",
    rounding_specs_and_exp_results,
)
def test_rounding_callable(
    base, direction, to_add_after_rounding, input_values, exp_output
):
    """Check if callable is rounded correctly.

    Tests `_add_rounding_to_one_function` directly.
    """

    def test_func(income):
        return income

    func_with_rounding = _add_rounding_to_one_function(
        base=base,
        direction=direction,
        to_add_after_rounding=to_add_after_rounding if to_add_after_rounding else 0,
    )(test_func)

    assert_series_equal(func_with_rounding(pd.Series(input_values)), pd.Series(exp_output), check_names=False)


def test_decorator_for_all_functions_with_rounding_spec():
    """Check if all functions for which rounding parameters are specified have an
    attribute which indicates rounding."""

    # Find all functions for which rounding parameters are specified
    params_dict = {
        group: yaml.safe_load(
            (RESOURCE_DIR / "parameters" / f"{group}.yaml").read_text(encoding="utf-8")
        )
        for group in INTERNAL_PARAMS_GROUPS
    }
    params_keys_with_rounding_spec = [
        k for k in params_dict if "rounding" in params_dict[k]
    ]
    function_names_with_rounding_spec = [
        fn for k in params_keys_with_rounding_spec for fn in params_dict[k]["rounding"]
    ]

    # Load mapping of time dependent functions. This will be much nicer after #334 is
    # addressed.
    time_dependent_functions = {}
    for year in range(1990, 2023):
        year_functions = load_functions_for_date(
            datetime.date(year=year, month=1, day=1)
        )
        new_dict = {func.__name__: key for key, func in year_functions.items()}
        time_dependent_functions = {**time_dependent_functions, **new_dict}

    # Add time dependent functions for which rounding specs for new name exist
    # and remove new name from list
    function_names_to_check = function_names_with_rounding_spec + [
        k
        for k, v in time_dependent_functions.items()
        if v in function_names_with_rounding_spec
    ]
    function_names_to_check = [
        fn
        for fn in function_names_to_check
        if fn not in time_dependent_functions.values()
    ]

    # Loop over these functions and check if attribute
    # __info__["rounding_params_key"] exists
    all_functions = _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)
    for fn in function_names_to_check:
        assert hasattr(all_functions[fn], "__info__"), (
            f"For the function {fn}, rounding parameters are specified. But the "
            "function is missing the add_rounding_spec decorator. The attribute "
            "__info__ is not found."
        )
        assert "rounding_params_key" in all_functions[fn].__info__, (
            f"For the function {fn}, rounding parameters are specified. But the "
            "function is missing the add_rounding_spec decorator. The key "
            "'rounding_params_key' is not found in the __info__ dict."
        )


@pytest.mark.parametrize(
    "params, match",
    [
        ({}, "Rounding specifications for function"),
        ({"eink_st": {}}, "Rounding specifications for function"),
        ({"eink_st": {"rounding": {}}}, "Rounding specifications for function"),
        (
            {"eink_st": {"rounding": {"eink_st_func": {}}}},
            "Both 'base' and 'direction' are expected",
        ),
    ],
)
def test_raise_if_missing_rounding_spec(params, match):
    @add_rounding_spec(params_key="eink_st")
    def eink_st_func(arg_1: float) -> float:
        return arg_1

    with pytest.raises(KeyError, match=match):
        _add_rounding_to_functions(
            functions={"eink_st_func": eink_st_func}, params=params
        )
