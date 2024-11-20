from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

import numpy
import pytest

from _gettsim.config import RESOURCE_DIR
from _gettsim.functions.loader import (
    _load_functions,
)
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.policy_environment import PolicyEnvironment
from _gettsim.policy_environment_postprocessor import (
    _create_derived_functions,
    _vectorize_func,
)
from _gettsim.shared import policy_info

if TYPE_CHECKING:
    from collections.abc import Callable


def test_load_path():
    assert _load_functions(
        RESOURCE_DIR / "social_insurance_contributions" / "ges_krankenv.py",
        RESOURCE_DIR,
    )


def test_load_paths():
    assert _load_functions(
        [RESOURCE_DIR / "social_insurance_contributions" / "ges_krankenv.py"],
        RESOURCE_DIR,
    )


def test_special_attribute_module_is_set(tmp_path):
    py_file = """
    def func():
        pass
    """

    file_path = tmp_path.joinpath("functions.py")
    file_path.write_text(textwrap.dedent(py_file))

    out = _load_functions(file_path, file_path)
    assert len(out) == 1
    assert out[0].__name__ == "func"
    assert out[0].__module__ == "functions"


def test_special_attribute_module_is_set_for_internal_functions():
    a_few_functions = _load_functions(
        RESOURCE_DIR / "social_insurance_contributions" / "eink_grenzen.py",
        RESOURCE_DIR,
    )
    function = next(iter(a_few_functions))
    assert function.__module__ == "_gettsim.social_insurance_contributions.eink_grenzen"


@pytest.mark.parametrize(
    ("functions", "targets"),
    [
        ({"foo_y": lambda: 1}, ["foo_d_hh"]),
        ({"foo_y": lambda: 1}, ["foo_d", "foo_d_hh"]),
    ],
)
def test_create_derived_functions(
    functions: dict[str, Callable], targets: list[str]
) -> None:
    environment = PolicyEnvironment(
        [
            PolicyFunction(
                function_name=name,
                function=func,
            )
            for name, func in functions.items()
        ]
    )

    (
        time_conversion_functions,
        aggregate_by_group_functions,
        aggregate_by_p_id_functions,
    ) = _create_derived_functions(environment, targets, [])

    derived_functions = {
        **time_conversion_functions,
        **aggregate_by_group_functions,
        **aggregate_by_p_id_functions,
    }

    for name in targets:
        assert name in derived_functions


# vectorize_func --------------------------------------------------------------


def scalar_func(x: int) -> int:
    return x * 2


@policy_info(skip_vectorization=True)
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
