from contextlib import ExitStack as does_not_raise  # noqa: N813

import numpy as np
import pandas as pd
import pytest

from gettsim import compute_taxes_and_transfers
from gettsim import test
from gettsim.interface import _expand_data
from gettsim.interface import _fail_if_columns_overriding_functions_are_not_in_data
from gettsim.interface import _fail_if_columns_overriding_functions_are_not_in_functions
from gettsim.interface import _fail_if_functions_and_columns_overlap


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


def test_missing_root_nodes_raises_error():
    n_individuals = 5
    df = pd.DataFrame(index=np.arange(n_individuals))

    def b(a):
        return a

    def c(b):
        return b

    with pytest.raises(
        ValueError, match="The following data columns are missing",
    ):
        compute_taxes_and_transfers(df, targets="c", functions=[b, c])


def test_function_without_data_dependency_is_not_mistaken_for_data():
    n_individuals = 5
    df = pd.DataFrame(index=np.arange(n_individuals))

    def a():
        return pd.Series(range(n_individuals))

    def b(a):
        return a

    compute_taxes_and_transfers(df, targets="b", functions=[a, b])


def test_consecutive_internal_test_runs():
    test("--collect-only")

    with pytest.warns(UserWarning, match="Repeated execution of the test suite"):
        test("--collect-only")
