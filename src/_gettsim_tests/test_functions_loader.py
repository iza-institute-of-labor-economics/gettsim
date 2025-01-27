from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING

import numpy
import pytest

from _gettsim.config import RESOURCE_DIR
from _gettsim.functions.loader import (
    _load_module,
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
    ) = _create_derived_functions(environment, targets, [])

    derived_functions = reduce(
        merge_nested_dicts,
        [
            time_conversion_functions,
            aggregate_by_group_functions,
            aggregate_by_p_id_functions,
        ],
        environment.functions_tree,
    )

    target_names = tree_flatten_with_qualified_name(targets)[0]
    potential_targets = tree_flatten_with_qualified_name(derived_functions)[0]

    for name in target_names:
        assert name in potential_targets


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
