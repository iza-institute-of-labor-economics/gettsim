from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING

import numpy
import pytest
from optree import tree_flatten

from _gettsim.config import RESOURCE_DIR
from _gettsim.functions.derived_function import DerivedFunction
from _gettsim.functions.loader import (
    ConflictingTimeDependentFunctionsError,
    _fail_if_dates_active_overlap,
    _load_module,
    _remove_recurring_branch_names,
)
from _gettsim.functions.policy_function import PolicyFunction, policy_function
from _gettsim.policy_environment import PolicyEnvironment
from _gettsim.policy_environment_postprocessor import (
    _create_derived_functions,
    _vectorize_func,
)
from _gettsim.shared import (
    merge_nested_dicts,
    tree_flatten_with_qualified_name,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def test_load_path():
    assert _load_module(
        RESOURCE_DIR / "social_insurance_contributions" / "ges_krankenv.py",
        RESOURCE_DIR,
    )


@pytest.mark.parametrize(
    ("functions", "targets"),
    [
        ({"foo_y": lambda: 1}, {"module": {"foo_d_hh": None}}),
        ({"foo_y": lambda: 1}, {"module": {"foo_d": None, "foo_d_hh": None}}),
    ],
)
def test_create_derived_functions(
    functions: dict[str, Callable], targets: list[str]
) -> None:
    environment = PolicyEnvironment(
        {
            "module": {
                name: PolicyFunction(
                    leaf_name=name,
                    function=func,
                )
                for name, func in functions.items()
            },
        }
    )

    (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    ) = _create_derived_functions(environment, targets, {})

    derived_functions_tree = reduce(
        merge_nested_dicts,
        [
            time_conversion_functions,
            aggregate_by_group_functions,
            aggregate_by_p_id_functions,
        ],
        environment.functions_tree,
    )

    derived_functions = tree_flatten(derived_functions_tree)[0]
    qualified_names_derived_functions = [
        func.qualified_name for func in derived_functions
    ]

    qualified_target_names = tree_flatten_with_qualified_name(targets)[0]

    for name in qualified_target_names:
        assert name in qualified_names_derived_functions

    for func in derived_functions:
        assert isinstance(func, DerivedFunction | PolicyFunction)


def test_fail_if_dates_active_overlap():
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
        _fail_if_dates_active_overlap(active_functions)


# vectorize_func --------------------------------------------------------------


def scalar_func(x: int) -> int:
    return x * 2


@policy_function(skip_vectorization=True)
def already_vectorized_func(x: numpy.ndarray) -> numpy.ndarray:
    return numpy.asarray([xi * 2 for xi in x])


@pytest.mark.parametrize(
    "function",
    [
        scalar_func,
        already_vectorized_func,
    ],
)
def test_vectorize_func(function: Callable) -> None:
    vectorized_func = _vectorize_func(function)

    assert numpy.array_equal(
        vectorized_func(numpy.array([1, 2, 3])), numpy.array([2, 4, 6])
    )


@pytest.mark.parametrize(
    (
        "path",
        "expected_string",
    ),
    [
        ("foo__bar__bar", "foo__bar"),
        ("foo__bar__baz", "foo__bar__baz"),
        ("foo__bar__bar__bar", "foo__bar__bar"),
        ("foo__bar__bar__baz", "foo__bar__bar__baz"),
    ],
)
def test_remove_recurring_branch_names(path: str, expected_string: str) -> None:
    assert _remove_recurring_branch_names(path) == expected_string
