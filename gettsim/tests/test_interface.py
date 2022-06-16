from contextlib import ExitStack as does_not_raise  # noqa: N813

import numpy as np
import pandas as pd
import pytest

from gettsim import compute_taxes_and_transfers
from gettsim.interface import _fail_if_columns_overriding_functions_are_not_in_data
from gettsim.interface import _fail_if_columns_overriding_functions_are_not_in_functions
from gettsim.interface import _fail_if_functions_and_columns_overlap
from gettsim.interface import _fail_if_group_variables_not_constant_within_groups
from gettsim.interface import _fail_if_pid_is_non_unique
from gettsim.interface import _partial_parameters_to_functions
from gettsim.shared import add_rounding_spec
from gettsim.typing import convert_series_to_internal_type


@pytest.fixture(scope="module")
def minimal_input_data():
    n_individuals = 5
    out = pd.DataFrame(
        {
            "p_id": np.arange(n_individuals),
            "tu_id": np.arange(n_individuals),
            "hh_id": np.arange(n_individuals),
        },
        index=np.arange(n_individuals),
    )
    return out


# Create a partial function which is used by some tests below
def func_before_partial(arg_1, arbeitsl_geld_2_params):
    return arg_1 + arbeitsl_geld_2_params["test_param_1"]


func_after_partial = _partial_parameters_to_functions(
    {"test_func": func_before_partial}, {"arbeitsl_geld_2": {"test_param_1": 1}}
)["test_func"]


@pytest.mark.parametrize(
    "data, columns_overriding_functions, expectation",
    [
        ({}, ["not_in_data"], pytest.raises(ValueError)),
        ({"in_data": None}, ["in_data"], does_not_raise()),
    ],
)
def test_fail_if_columns_overriding_functions_are_not_in_data(
    data, columns_overriding_functions, expectation
):
    with expectation:
        _fail_if_columns_overriding_functions_are_not_in_data(
            data, columns_overriding_functions
        )


@pytest.mark.parametrize(
    "columns_overriding_functions, functions, expectation",
    [
        (["not_in_functions"], {}, pytest.raises(ValueError)),
        (["in_functions"], {"in_functions": None}, does_not_raise()),
    ],
)
def test_fail_if_columns_overriding_functions_are_not_in_functions(
    columns_overriding_functions, functions, expectation
):
    with expectation:
        _fail_if_columns_overriding_functions_are_not_in_functions(
            columns_overriding_functions, functions
        )


@pytest.mark.parametrize(
    "columns, functions, type_, expectation",
    [
        ({"dupl": None}, {"dupl": None}, "internal", pytest.raises(ValueError)),
        ({}, {}, "internal", does_not_raise()),
        ({"dupl": None}, {"dupl": None}, "user", pytest.raises(ValueError)),
        ({}, {}, "user", does_not_raise()),
    ],
)
def test_fail_if_functions_and_columns_overlap(columns, functions, type_, expectation):
    with expectation:
        _fail_if_functions_and_columns_overlap(columns, functions, type_)


def test_fail_if_pid_does_not_exist():
    data = pd.Series(data=np.arange(8), name="hh_id").to_frame()

    with pytest.raises(ValueError):
        _fail_if_pid_is_non_unique(data)


def test_fail_if_pid_is_non_unique():
    data = pd.Series(data=np.arange(4).repeat(2), name="p_id").to_frame()

    with pytest.raises(ValueError):
        _fail_if_pid_is_non_unique(data)


def test_fail_if_group_variables_not_constant_within_groups():
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "arbeitsl_geld_2_m_hh": [100, 200, 300],
        }
    )

    with pytest.raises(ValueError):
        _fail_if_group_variables_not_constant_within_groups(data)


def test_missing_root_nodes_raises_error(minimal_input_data):
    def b(a):
        return a

    def c(b):
        return b

    with pytest.raises(
        ValueError,
        match="The following data columns are missing",
    ):
        compute_taxes_and_transfers(
            minimal_input_data, {}, functions=[b, c], targets="c"
        )


def test_function_without_data_dependency_is_not_mistaken_for_data(minimal_input_data):
    def a():
        return pd.Series(range(minimal_input_data.shape[0]))

    def b(a):
        return a

    compute_taxes_and_transfers(minimal_input_data, {}, functions=[a, b], targets="b")


def test_fail_if_missing_pid(minimal_input_data):
    data = minimal_input_data.drop("p_id", axis=1).copy()

    with pytest.raises(
        ValueError,
        match="The input data must contain the column p_id",
    ):
        compute_taxes_and_transfers(data, {}, functions=[], targets=[])


def test_fail_if_non_unique_pid(minimal_input_data):
    data = minimal_input_data.copy()
    data["p_id"] = 1

    with pytest.raises(
        ValueError,
        match="The following p_ids are non-unique",
    ):
        compute_taxes_and_transfers(data, {}, functions=[], targets=[])


def test_fail_if_non_unique_cols(minimal_input_data):
    data = minimal_input_data.copy()
    data["temp"] = data["hh_id"]
    data = data.rename(columns={"temp": "hh_id"})
    with pytest.raises(
        ValueError,
        match="The following columns are non-unique",
    ):
        compute_taxes_and_transfers(data, {}, functions=[], targets=[])


def test_consecutive_internal_test_runs():
    from gettsim import test

    test("--collect-only")

    with pytest.warns(UserWarning, match="Repeated execution of the test suite"):
        test("--collect-only")


def test_partial_parameters_to_functions():

    # Partial function produces correct result
    assert func_after_partial(2) == 3


def test_partial_parameters_to_functions_removes_argument():

    # Fails if params is added to partial function
    with pytest.raises(
        TypeError,
        match=("got multiple values for argument "),
    ):
        func_after_partial(2, {"test_param_1": 1})

    # No error for original function
    func_before_partial(2, {"test_param_1": 1})


def test_partial_parameters_to_functions_keep_decorator():
    """Make sure that rounding decorator is kept for partial function"""

    @add_rounding_spec(params_key="params_key_test")
    def test_func(arg_1, arbeitsl_geld_2_params):
        return arg_1 + arbeitsl_geld_2_params["test_param_1"]

    partial_func = _partial_parameters_to_functions(
        {"test_func": test_func}, {"arbeitsl_geld_2": {"test_param_1": 1}}
    )["test_func"]

    assert partial_func.__rounding_params_key__ == "params_key_test"


def test_user_provided_aggregation_specs():

    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "arbeitsl_geld_2_m": [100, 100, 100],
        }
    )
    aggregation_specs = {
        "arbeitsl_geld_2_m_hh": {
            "source_col": "arbeitsl_geld_2_m",
            "aggr": "sum",
        }
    }
    expected_res = pd.Series([200, 200, 100])

    out = compute_taxes_and_transfers(
        data,
        {},
        functions=[],
        targets="arbeitsl_geld_2_m_hh",
        aggregation_specs=aggregation_specs,
    )

    np.testing.assert_array_almost_equal(out["arbeitsl_geld_2_m_hh"], expected_res)


def test_user_provided_aggregation_specs_function():

    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "arbeitsl_geld_2_m": [200, 100, 100],
        }
    )
    aggregation_specs = {
        "arbeitsl_geld_2_m_double_hh": {
            "source_col": "arbeitsl_geld_2_m_double",
            "aggr": "max",
        }
    }
    expected_res = pd.Series([400, 400, 200])

    def arbeitsl_geld_2_m_double(arbeitsl_geld_2_m):
        return 2 * arbeitsl_geld_2_m

    out = compute_taxes_and_transfers(
        data,
        {},
        functions=[arbeitsl_geld_2_m_double],
        targets="arbeitsl_geld_2_m_double_hh",
        aggregation_specs=aggregation_specs,
    )

    np.testing.assert_array_almost_equal(
        out["arbeitsl_geld_2_m_double_hh"], expected_res
    )


@pytest.mark.parametrize(
    "input_data, expected_type, expected_output_data",
    [
        (pd.Series([0, 1, 0]), bool, pd.Series([False, True, False])),
        (pd.Series([1.0, 0.0, 1]), bool, pd.Series([True, False, True])),
        (pd.Series([200, 550, 237]), float, pd.Series([200.0, 550.0, 237.0])),
        (pd.Series([1.0, 4.0, 10.0]), int, pd.Series([1, 4, 10])),
        (pd.Series([200.0, 567.0]), int, pd.Series([200, 567])),
        (pd.Series([1.0, 0.0]), bool, pd.Series([True, False])),
    ],
)
def test_convert_series_to_internal_types(
    input_data, expected_type, expected_output_data
):
    adjusted_input = convert_series_to_internal_type(input_data, expected_type)
    pd.testing.assert_series_equal(adjusted_input, expected_output_data)


@pytest.mark.parametrize(
    "input_data, expected_type, error_match",
    [
        (
            pd.Series(["Hallo", 200, 325]),
            float,
            "Conversion from input type object to float failed.",
        ),
        (
            pd.Series([True, False]),
            float,
            "Conversion from input type bool to float failed.",
        ),
        (
            pd.Series(["a", "b", "c"]).astype("category"),
            float,
            "Conversion from input type category to float failed.",
        ),
        (
            pd.Series(["2.0", "3.0"]),
            int,
            "Conversion from input type object to int failed.",
        ),
        (
            pd.Series([1.5, 1.0, 2.9]),
            int,
            "Conversion from input type float64 to int failed.",
        ),
        (
            pd.Series(["a", "b", "c"]).astype("category"),
            int,
            "Conversion from input type category to int failed.",
        ),
        (
            pd.Series([5, 2, 3]),
            bool,
            "Conversion from input type int64 to bool failed.",
        ),
        (
            pd.Series([1.5, 1.0, 35.0]),
            bool,
            "Conversion from input type float64 to bool failed.",
        ),
        (
            pd.Series(["a", "b", "c"]).astype("category"),
            bool,
            "Conversion from input type category to bool failed.",
        ),
        (
            pd.Series(["richtig"]),
            bool,
            "Conversion from input type object to bool failed.",
        ),
        (
            pd.Series(["True", "False", ""]),
            bool,
            "Conversion from input type object to bool failed.",
        ),
        (
            pd.Series(["true"]),
            bool,
            "Conversion from input type object to bool failed.",
        ),
        (
            pd.Series(["zweitausendzwanzig"]),
            np.datetime64,
            "Conversion from input type object to datetime64 failed.",
        ),
        (
            pd.Series([True, True]),
            np.datetime64,
            "Conversion from input type bool to datetime64 failed.",
        ),
        (
            pd.Series([2020]),
            str,
            "The internal type <class 'str'> is not yet supported.",
        ),
    ],
)
def test_fail_if_cannot_be_converted_to_correct_type(
    input_data, expected_type, error_match
):
    with pytest.raises(ValueError, match=error_match):
        convert_series_to_internal_type(input_data, expected_type)
