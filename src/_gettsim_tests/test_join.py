import numpy as np
import pytest
from _gettsim.shared import join_numpy


@pytest.mark.parametrize(
    "foreign_key, primary_key, target, value_for_unresolved_foreign_key, expected",
    [
        (
            np.array([1, 2, 3]),
            np.array([1, 2, 3]),
            np.array(["a", "b", "c"]),
            "d",
            np.array(["a", "b", "c"]),
        ),
        (
            np.array([3, 2, 1]),
            np.array([1, 2, 3]),
            np.array(["a", "b", "c"]),
            "d",
            np.array(["c", "b", "a"]),
        ),
        (
            np.array([1, 1, 1]),
            np.array([1, 2, 3]),
            np.array(["a", "b", "c"]),
            "d",
            np.array(["a", "a", "a"]),
        ),
        (
            np.array([-1]),
            np.array([1]),
            np.array(["a"]),
            "d",
            np.array(["d"]),
        ),
    ],
)
def test_join_numpy(
    foreign_key: np.ndarray[int],
    primary_key: np.ndarray[int],
    target: np.ndarray[str],
    value_for_unresolved_foreign_key: str,
    expected: np.ndarray[str],
):
    assert np.array_equal(
        join_numpy(foreign_key, primary_key, target, value_for_unresolved_foreign_key),
        expected,
    )


def test_join_numpy_raises_duplicate_primary_key():
    with pytest.raises(ValueError, match="Duplicate primary keys:"):
        join_numpy(
            np.array([1, 1, 1]),
            np.array([1, 1, 1]),
            np.array(["a", "b", "c"]),
            "default",
        )


def test_join_numpy_raises_invalid_foreign_key():
    with pytest.raises(ValueError, match="Invalid foreign keys:"):
        join_numpy(np.array([2]), np.array([1]), np.array(["a"]), "d")
