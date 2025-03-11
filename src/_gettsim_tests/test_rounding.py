import datetime

import pandas as pd
import pytest
import yaml
from optree import tree_flatten
from pandas._testing import assert_series_equal

from _gettsim.config import (
    INTERNAL_PARAMS_GROUPS,
    RESOURCE_DIR,
)
from _gettsim.function_types import policy_function
from _gettsim.interface import (
    _add_rounding_to_function,
    _apply_rounding_spec,
    compute_taxes_and_transfers,
)
from _gettsim.loader import load_functions_tree_for_date
from _gettsim.policy_environment import PolicyEnvironment

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
    @policy_function(params_key_for_rounding="params_key_test")
    def test_func():
        return 0

    assert test_func.params_key_for_rounding == "params_key_test"


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

        @policy_function(params_key_for_rounding="params_key_test")
        def test_func():
            return 0

        environment = PolicyEnvironment({"test_func": test_func}, rounding_specs)

        compute_taxes_and_transfers(
            data_tree={"groupings": {"p_id": pd.Series([1, 2])}},
            environment=environment,
            targets_tree={"test_func": None},
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

        @policy_function(params_key_for_rounding="params_key_test")
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

        environment = PolicyEnvironment({"test_func": test_func}, rounding_specs)

        compute_taxes_and_transfers(
            data_tree={"groupings": {"p_id": pd.Series([1, 2])}},
            environment=environment,
            targets_tree={"test_func": None},
        )


@pytest.mark.parametrize(
    "base, direction, to_add_after_rounding, input_values, exp_output",
    rounding_specs_and_exp_results,
)
def test_rounding(base, direction, to_add_after_rounding, input_values, exp_output):
    """Check if rounding is correct."""

    # Define function that should be rounded
    @policy_function(params_key_for_rounding="params_key_test")
    def test_func(income):
        return income

    data = {"groupings": {"p_id": pd.Series([1, 2])}}
    data["income"] = pd.Series(input_values)
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

    environment = PolicyEnvironment({"test_func": test_func}, rounding_specs)

    calc_result = compute_taxes_and_transfers(
        data_tree=data, environment=environment, targets_tree={"test_func": None}
    )
    assert_series_equal(
        pd.Series(calc_result["test_func"]), pd.Series(exp_output), check_names=False
    )


def test_rounding_with_time_conversion():
    """Check if rounding is correct for time-converted functions."""

    # Define function that should be rounded
    @policy_function(params_key_for_rounding="params_key_test")
    def test_func_m(income):
        return income

    data = {"groupings": {"p_id": pd.Series([1, 2])}, "income": pd.Series([1.2, 1.5])}
    rounding_specs = {
        "params_key_test": {
            "rounding": {
                "test_func_m": {
                    "base": 1,
                    "direction": "down",
                }
            }
        }
    }
    environment = PolicyEnvironment({"test_func_m": test_func_m}, rounding_specs)

    calc_result = compute_taxes_and_transfers(
        data_tree=data,
        environment=environment,
        targets_tree={"test_func_y": None},
    )
    assert_series_equal(
        pd.Series(calc_result["test_func_y"]),
        pd.Series([12.0, 12.0]),
        check_names=False,
    )


@pytest.mark.parametrize(
    "base, direction, to_add_after_rounding, input_values_exp_output, _ignore",
    rounding_specs_and_exp_results,
)
def test_no_rounding(
    base, direction, to_add_after_rounding, input_values_exp_output, _ignore
):
    # Define function that should be rounded
    @policy_function(params_key_for_rounding="params_key_test")
    def test_func(income):
        return income

    data = {"groupings": {"p_id": pd.Series([1, 2])}}
    data["income"] = pd.Series(input_values_exp_output)
    rounding_specs = {
        "params_key_test": {
            "rounding": {"test_func": {"base": base, "direction": direction}}
        }
    }
    environment = PolicyEnvironment({"test_func": test_func}, rounding_specs)

    if to_add_after_rounding:
        rounding_specs["params_key_test"]["rounding"]["test_func"][
            "to_add_after_rounding"
        ] = to_add_after_rounding

    calc_result = compute_taxes_and_transfers(
        data_tree=data,
        environment=environment,
        targets_tree={"test_func": None},
        rounding=False,
    )
    assert_series_equal(
        pd.Series(calc_result["test_func"]),
        pd.Series(input_values_exp_output),
        check_names=False,
    )


@pytest.mark.parametrize(
    "base, direction, to_add_after_rounding, input_values, exp_output",
    rounding_specs_and_exp_results,
)
def test_rounding_callable(
    base, direction, to_add_after_rounding, input_values, exp_output
):
    """Check if callable is rounded correctly.

    Tests `_apply_rounding_spec` directly.
    """

    def test_func(income):
        return income

    func_with_rounding = _apply_rounding_spec(
        base=base,
        direction=direction,
        to_add_after_rounding=to_add_after_rounding if to_add_after_rounding else 0,
        path=("test_func",),
    )(test_func)

    assert_series_equal(
        func_with_rounding(pd.Series(input_values)),
        pd.Series(exp_output),
        check_names=False,
    )


@pytest.mark.xfail(reason="Not able to load functions regardless of date any more.")
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
        year_functions = tree_flatten(
            load_functions_tree_for_date(datetime.date(year=year, month=1, day=1))
        )[0]
        function_name_to_leaf_name_dict = {
            func.function.__name__: func.leaf_name for func in year_functions
        }
        time_dependent_functions = {
            **time_dependent_functions,
            **function_name_to_leaf_name_dict,
        }

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

    functions_to_check = [
        f
        for f in _load_internal_functions()  # noqa: F821
        if f.original_function_name in function_names_to_check
    ]

    for f in functions_to_check:
        assert f.params_key_for_rounding, (
            f"For the function {f.original_function_name}, rounding parameters are"
            f" specified. However, its `params_key_for_rounding` attribute is not set."
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
    @policy_function(params_key_for_rounding="eink_st")
    def eink_st_func(arg_1: float) -> float:
        return arg_1

    with pytest.raises(KeyError, match=match):
        _add_rounding_to_function(
            input_function=eink_st_func, params=params, path=("eink_st_func",)
        )
