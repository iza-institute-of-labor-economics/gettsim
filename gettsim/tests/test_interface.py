from contextlib import ExitStack as does_not_raise  # noqa: N813

import numpy as np
import pandas as pd
import pytest

from gettsim import compute_taxes_and_transfers
from gettsim import test
from gettsim.config import ROOT_DIR
from gettsim.functions_loader import load_user_and_internal_functions
from gettsim.interface import _expand_data
from gettsim.interface import _fail_if_columns_overriding_functions_are_not_in_data
from gettsim.interface import _fail_if_columns_overriding_functions_are_not_in_functions
from gettsim.interface import _fail_if_datatype_is_false
from gettsim.interface import _fail_if_functions_and_columns_overlap
from gettsim.interface import _partial_parameters_to_functions
from gettsim.shared import add_rounding_spec


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


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


def test_fail_if_datatype_is_false(input_data):
    with does_not_raise():
        _fail_if_datatype_is_false(input_data, [], [])
    with pytest.raises(ValueError):
        altered_data = input_data.copy(deep=True)
        altered_data["alter"] = altered_data["alter"].astype(float)
        _fail_if_datatype_is_false(altered_data, [], [])
    with pytest.raises(ValueError):
        _, functions = load_user_and_internal_functions(None)
        columns = ["abgelt_st_tu"]
        new_data = pd.DataFrame(data=[True, False], columns=columns, dtype=bool)
        _fail_if_datatype_is_false(new_data, columns, functions)


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


def test_expand_data_raise_error():
    data = {"wrong_variable_hh": pd.Series(data=np.arange(4), index=np.arange(4))}
    ids = pd.Series(
        data=np.arange(8), index=np.arange(4).repeat(2), name="hh_id"
    ).to_frame()

    with pytest.raises(KeyError):
        _expand_data(data, ids)


def test_missing_root_nodes_raises_error(minimal_input_data):
    def b(a):
        return a

    def c(b):
        return b

    with pytest.raises(
        ValueError, match="The following data columns are missing",
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
        ValueError, match="The input data must contain the column p_id",
    ):
        compute_taxes_and_transfers(data, {}, functions=[], targets=[])


def test_fail_if_non_unique_pid(minimal_input_data):
    data = minimal_input_data.copy()
    data["p_id"] = 1

    with pytest.raises(
        ValueError, match="The following p_ids are non-unique",
    ):
        compute_taxes_and_transfers(data, {}, functions=[], targets=[])


def test_fail_if_non_unique_cols(minimal_input_data):
    data = minimal_input_data.copy()
    data["temp"] = data["hh_id"]
    data = data.rename(columns={"temp": "hh_id"})
    with pytest.raises(
        ValueError, match="The following columns are non-unique",
    ):
        compute_taxes_and_transfers(data, {}, functions=[], targets=[])


def test_consecutive_internal_test_runs():
    test("--collect-only")

    with pytest.warns(UserWarning, match="Repeated execution of the test suite"):
        test("--collect-only")


def test_partial_parameters_to_functions():

    # Partial function produces correct result
    assert func_after_partial(2) == 3


def test_partial_parameters_to_functions_removes_argument():

    # Fails if params is added to partial function
    with pytest.raises(
        TypeError, match=("got multiple values for argument "),
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
