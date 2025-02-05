from __future__ import annotations

from typing import TYPE_CHECKING

import numpy
import pytest

from _gettsim.config import RESOURCE_DIR
from _gettsim.functions.loader import (
    ConflictingTimeDependentFunctionsError,
    _fail_if_multiple_policy_functions_are_active_at_the_same_time,
    _load_module,
    _simplify_tree_path_when_module_name_equals_dir_name,
)
from _gettsim.functions.policy_function import (
    PolicyFunction,
    _vectorize_func,
    policy_function,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def test_load_path():
    assert _load_module(
        RESOURCE_DIR / "social_insurance_contributions" / "ges_krankenv.py",
        RESOURCE_DIR,
    )


def test_fail_if_multiple_policy_functions_are_active_at_the_same_time():
    active_functions = [
        PolicyFunction(
            leaf_name="foo",
            qualified_name="foo",
            function=lambda: 1,
        ),
        PolicyFunction(
            leaf_name="foo",
            qualified_name="foo",
            function=lambda: 2,
        ),
    ]

    with pytest.raises(ConflictingTimeDependentFunctionsError):
        _fail_if_multiple_policy_functions_are_active_at_the_same_time(
            active_functions, module_name=""
        )


def scalar_func(x: int) -> int:
    return x * 2


@policy_function(skip_vectorization=True)
def already_vectorized_func(x: numpy.ndarray) -> numpy.ndarray:
    return numpy.asarray([xi * 2 for xi in x])


@pytest.mark.parametrize(
    "vectorized_function",
    [
        _vectorize_func(scalar_func),
        already_vectorized_func,
    ],
)
def test_vectorize_func(vectorized_function: Callable) -> None:
    assert numpy.array_equal(
        vectorized_function(numpy.array([1, 2, 3])), numpy.array([2, 4, 6])
    )


@pytest.mark.parametrize(
    (
        "path",
        "expected_tree_path",
    ),
    [
        (("foo", "bar", "bar"), ("foo", "bar")),
        (("foo", "bar", "baz"), ("foo", "bar", "baz")),
        (("foo", "bar", "bar", "bar"), ("foo", "bar", "bar")),
        (("foo", "bar", "bar", "baz"), ("foo", "bar", "bar", "baz")),
    ],
)
def test_remove_recurring_branch_names(
    path: str, expected_tree_path: tuple[str, ...]
) -> None:
    assert (
        _simplify_tree_path_when_module_name_equals_dir_name(path) == expected_tree_path
    )
