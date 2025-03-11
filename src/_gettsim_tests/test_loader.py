from __future__ import annotations

from typing import TYPE_CHECKING

import numpy
import pytest

from _gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS, RESOURCE_DIR
from _gettsim.function_types import (
    policy_function,
)
from _gettsim.function_types.policy_function import _vectorize_func
from _gettsim.loader import (
    _convert_path_to_tree_path,
    _find_python_files_recursively,
    _load_module,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def test_load_path():
    assert _load_module(
        RESOURCE_DIR
        / "taxes"
        / "sozialversicherungsbeiträge"
        / "krankenversicherung"
        / "beitragssatz.py",
        RESOURCE_DIR,
    )


def test_dont_load_init_py():
    """Don't load __init__.py files as sources for PolicyFunctions and
    AggregationSpecs."""
    all_files = _find_python_files_recursively(PATHS_TO_INTERNAL_FUNCTIONS)
    assert "__init__.py" not in [file.name for file in all_files]


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
        "package_root",
        "expected_tree_path",
    ),
    [
        (RESOURCE_DIR / "foo" / "bar.py", RESOURCE_DIR, ("foo",)),
        (RESOURCE_DIR / "foo" / "spam" / "bar.py", RESOURCE_DIR, ("foo", "spam")),
        (RESOURCE_DIR / "taxes" / "foo" / "bar.py", RESOURCE_DIR, ("foo",)),
        (RESOURCE_DIR / "transfers" / "foo" / "bar.py", RESOURCE_DIR, ("foo",)),
    ],
)
def test_convert_path_to_tree_path(
    path: Path, package_root: Path, expected_tree_path: tuple[str, ...]
) -> None:
    assert (
        _convert_path_to_tree_path(path=path, package_root=package_root)
        == expected_tree_path
    )
