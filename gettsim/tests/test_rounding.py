import datetime

import numpy as np
import pandas as pd
import pytest
import yaml

from gettsim import compute_taxes_and_transfers
from gettsim.config import INTERNAL_PARAM_GROUPS
from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.config import ROOT_DIR
from gettsim.functions_loader import _load_functions
from gettsim.policy_environment import load_reforms_for_date
from gettsim.shared import add_rounding_spec

rounding_specs_and_exp_results = [
    (1, "up", [100.24, 100.78], [101.0, 101.0]),
    (1, "down", [100.24, 100.78], [100.0, 100.0]),
    (1, "nearest", [100.24, 100.78], [100.0, 101.0]),
    (5, "up", [100.24, 100.78], [105.0, 105.0]),
    (0.1, "down", [100.24, 100.78], [100.2, 100.7]),
    (0.001, "nearest", [100.24, 100.78], [100.24, 100.78]),
]


def test_decorator():
    @add_rounding_spec(params_key="params_key_test")
    def test_func():
        return 0

    assert test_func.__rounding_params_key__ == "params_key_test"


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
            functions=[test_func],
            params=rounding_specs,
            targets=["test_func"],
        )


@pytest.mark.parametrize(
    "base, direction", [(1, "upper"), ("0.1", "down"), (5, "closest")],
)
def test_rounding_specs_wrong_format(base, direction):
    with pytest.raises(ValueError):

        @add_rounding_spec(params_key="params_key_test")
        def test_func():
            return 0

        rounding_specs = {
            "params_key_test": {
                "rounding": {"test_func": {"base": base, "direction": direction}}
            }
        }

        compute_taxes_and_transfers(
            data=pd.DataFrame([{"p_id": 1}, {"p_id": 2}]),
            functions=[test_func],
            params=rounding_specs,
            targets=["test_func"],
        )


@pytest.mark.parametrize(
    "base, direction, input_values, exp_output", rounding_specs_and_exp_results,
)
def test_rounding(base, direction, input_values, exp_output):
    """Check if rounding is correct"""

    # Define function that should be rounded
    @add_rounding_spec(params_key="params_key_test")
    def test_func(income):
        return income

    data = pd.DataFrame([{"p_id": 1}, {"p_id": 2}])
    data["income"] = input_values
    rounding_specs = {
        "params_key_test": {
            "rounding": {"test_func": {"base": base, "direction": direction}}
        }
    }

    calc_result = compute_taxes_and_transfers(
        data=data, functions=[test_func], params=rounding_specs, targets=["test_func"],
    )
    np.array_equal(calc_result["test_func"].values, np.array(exp_output))


@pytest.mark.parametrize(
    "base, direction, input_values_exp_output, _ignore", rounding_specs_and_exp_results,
)
def test_no_rounding(base, direction, input_values_exp_output, _ignore):  # noqa: U101

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

    calc_result = compute_taxes_and_transfers(
        data=data, functions=[test_func], params=rounding_specs, targets=["test_func"],
    )
    np.array_equal(calc_result["test_func"].values, np.array(input_values_exp_output))


def test_decorator_for_all_functions_with_rounding_spec():
    """Check if all functions for which rounding parameters are specified have
    an attribute which indicates rounding
    """

    # Find all functions for which rounding parameters are specified
    params_dict = {
        group: yaml.load(
            (ROOT_DIR / "parameters" / f"{group}.yaml").read_text(encoding="utf-8"),
            Loader=yaml.CLoader,
        )
        for group in INTERNAL_PARAM_GROUPS
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
    for year in range(1990, 2021):
        year_functions = load_reforms_for_date(datetime.date(year=year, month=1, day=1))
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

    # Loop over these functions and check if attribute __rounding_params_key__ exists
    all_functions = _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)
    for fn in function_names_to_check:
        assert hasattr(all_functions[fn], "__rounding_params_key__"), (
            f"For the function {fn}, rounding parameters are specified. But the "
            "function is missing the add_rounding_spec decorator. The attribute "
            "__rounding_params_key__ is not found."
        )
