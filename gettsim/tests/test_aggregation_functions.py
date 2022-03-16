import copy
from collections import ChainMap

import numpy as np
import pytest

from gettsim.aggregation_jax import grouped_all as grouped_all_jax
from gettsim.aggregation_jax import grouped_any as grouped_any_jax
from gettsim.aggregation_jax import grouped_max as grouped_max_jax
from gettsim.aggregation_jax import grouped_mean as grouped_mean_jax
from gettsim.aggregation_jax import grouped_min as grouped_min_jax
from gettsim.aggregation_jax import grouped_sum as grouped_sum_jax
from gettsim.aggregation_numpy import grouped_all as grouped_all_numpy
from gettsim.aggregation_numpy import grouped_any as grouped_any_numpy
from gettsim.aggregation_numpy import grouped_max as grouped_max_numpy
from gettsim.aggregation_numpy import grouped_mean as grouped_mean_numpy
from gettsim.aggregation_numpy import grouped_min as grouped_min_numpy
from gettsim.aggregation_numpy import grouped_sum as grouped_sum_numpy
from gettsim.config import IS_JAX_INSTALLED


def parameterize_based_on_dict(test_cases, keys_of_test_cases=None):
    """Apply pytest.mark.parametrize based on a dictionary"""
    test_cases = copy.copy(test_cases)
    if keys_of_test_cases:

        # Only use requested keys
        test_cases = {
            k: {
                k_inner: v_inner
                for k_inner, v_inner in v.items()
                if k_inner in keys_of_test_cases
            }
            for k, v in test_cases.items()
        }

        # Check that all requested keys are part of the dictionary
        for test_name, test_spec in test_cases.items():
            for key in keys_of_test_cases:
                assert (
                    key in test_spec.keys()
                ), f"{key} is missing in test_case {test_name}."

    # Return parametrization
    return pytest.mark.parametrize(
        argnames=(
            argnames := sorted({k for v in test_cases.values() for k in v.keys()})
        ),
        argvalues=[[v.get(k) for k in argnames] for v in test_cases.values()],
        ids=test_cases.keys(),
    )


available_backends = ["numpy", "jax"] if IS_JAX_INSTALLED else ["numpy"]
test_grouped_numeric_specs = [
    {
        f"constant_column_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([1, 1, 1, 1, 1]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "expected_res_sum": np.array([2, 2, 3, 3, 3]),
            "expected_res_mean": np.array([1, 1, 1, 1, 1]),
            "expected_res_max": np.array([1, 1, 1, 1, 1]),
            "expected_res_min": np.array([1, 1, 1, 1, 1]),
        },
        f"constant_column_group_id_unsorted_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([1, 1, 1, 1, 1]),
            "group_id": np.array([0, 1, 0, 1, 0]),
            "expected_res_sum": np.array([3, 2, 3, 2, 3]),
            "expected_res_mean": np.array([1, 1, 1, 1, 1]),
            "expected_res_max": np.array([1, 1, 1, 1, 1]),
            "expected_res_min": np.array([1, 1, 1, 1, 1]),
        },
        f"basic_case_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0, 1, 2, 3, 4]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "expected_res_sum": np.array([1, 1, 9, 9, 9]),
            "expected_res_mean": np.array([0.5, 0.5, 3, 3, 3]),
            "expected_res_max": np.array([1, 1, 4, 4, 4]),
            "expected_res_min": np.array([0, 0, 2, 2, 2]),
        },
        f"unique_group_ids_with_gaps_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0, 1, 2, 3, 4]),
            "group_id": np.array([0, 0, 3, 3, 3]),
            "expected_res_sum": np.array([1, 1, 9, 9, 9]),
            "expected_res_mean": np.array([0.5, 0.5, 3, 3, 3]),
            "expected_res_max": np.array([1, 1, 4, 4, 4]),
            "expected_res_min": np.array([0, 0, 2, 2, 2]),
        },
        f"float_column_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0, 1.5, 2, 3, 4]),
            "group_id": np.array([0, 0, 3, 3, 3]),
            "expected_res_sum": np.array([1.5, 1.5, 9, 9, 9]),
            "expected_res_mean": np.array([0.75, 0.75, 3, 3, 3]),
            "expected_res_max": np.array([1.5, 1.5, 4, 4, 4]),
            "expected_res_min": np.array([0, 0, 2, 2, 2]),
        },
    }
    for backend in available_backends
]
test_grouped_numeric_specs = dict(ChainMap(*test_grouped_numeric_specs))

test_grouped_bool_specs = [
    {
        f"basic_case_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, False, True, False, False]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "expected_res_any": np.array([True, True, True, True, True]),
            "expected_res_all": np.array([False, False, False, False, False]),
        },
        f"group_id_unsorted_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, False, True, True, True]),
            "group_id": np.array([0, 1, 0, 1, 0]),
            "expected_res_any": np.array([True, True, True, True, True]),
            "expected_res_all": np.array([True, False, True, False, True]),
        },
        f"unique_group_ids_with_gaps_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, False, False, False, False]),
            "group_id": np.array([0, 0, 3, 3, 3]),
            "expected_res_any": np.array([True, True, False, False, False]),
            "expected_res_all": np.array([False, False, False, False, False]),
        },
    }
    for backend in available_backends
]
test_grouped_bool_specs = dict(ChainMap(*test_grouped_bool_specs))

test_grouped_numeric_raises_specs = [
    {
        f"dtype_boolean_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, True, True, False, False]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error": ValueError,
            "exception_match": "grouped_",
        },
        f"dtype_string_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array(["0", "1", "2", "3", "4"]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error": ValueError,
            "exception_match": "grouped_",
        },
        f"float_group_id_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0, 1, 2, 3, 4]),
            "group_id": np.array([0, 0, 3.5, 3.5, 3.5]),
            "error": TypeError,
            "exception_match": "group_idx must be of integer type",
        },
    }
    for backend in available_backends
]
test_grouped_numeric_raises_specs = dict(ChainMap(*test_grouped_numeric_raises_specs))

test_grouped_bool_raises_specs = [
    {
        f"dtype_numeric_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([1, 2, 3, 4, 5]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error": ValueError,
            "exception_match": "grouped_",
        },
        f"dtype_string_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array(["0", "1", "2", "3", "4"]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error": ValueError,
            "exception_match": "grouped_",
        },
        f"float_group_id_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, True, True, False, False]),
            "group_id": np.array([0, 0, 3.5, 3.5, 3.5]),
            "error": TypeError,
            "exception_match": "group_idx must be of integer type",
        },
    }
    for backend in available_backends
]
test_grouped_bool_raises_specs = dict(ChainMap(*test_grouped_bool_raises_specs))


@parameterize_based_on_dict(
    test_grouped_numeric_specs,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "expected_res_sum",
    ],
)
def test_grouped_sum(backend, column_to_aggregate, group_id, expected_res_sum):

    # Calculate result
    if backend == "jax":
        result = grouped_sum_jax(column_to_aggregate, group_id)
    elif backend == "numpy":
        result = grouped_sum_numpy(column_to_aggregate, group_id)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")

    # Check equality
    np.testing.assert_array_equal(result, expected_res_sum)


@parameterize_based_on_dict(
    test_grouped_numeric_specs,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "expected_res_mean",
    ],
)
def test_grouped_mean(backend, column_to_aggregate, group_id, expected_res_mean):

    # Calculate result
    if backend == "jax":
        result = grouped_mean_jax(column_to_aggregate, group_id)
    elif backend == "numpy":
        result = grouped_mean_numpy(column_to_aggregate, group_id)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")

    # Check equality
    np.testing.assert_array_equal(result, expected_res_mean)


@parameterize_based_on_dict(
    test_grouped_numeric_specs,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "expected_res_max",
    ],
)
def test_grouped_max(backend, column_to_aggregate, group_id, expected_res_max):

    # Calculate result
    if backend == "jax":
        result = grouped_max_jax(column_to_aggregate, group_id)
    elif backend == "numpy":
        result = grouped_max_numpy(column_to_aggregate, group_id)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")

    # Check equality
    np.testing.assert_array_equal(result, expected_res_max)


@parameterize_based_on_dict(
    test_grouped_numeric_specs,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "expected_res_min",
    ],
)
def test_grouped_min(backend, column_to_aggregate, group_id, expected_res_min):

    # Calculate result
    if backend == "jax":
        result = grouped_min_jax(column_to_aggregate, group_id)
    elif backend == "numpy":
        result = grouped_min_numpy(column_to_aggregate, group_id)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")

    # Check equality
    np.testing.assert_array_equal(result, expected_res_min)


@parameterize_based_on_dict(
    test_grouped_bool_specs,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "expected_res_any",
    ],
)
def test_grouped_any(backend, column_to_aggregate, group_id, expected_res_any):

    # Calculate result
    if backend == "jax":
        result = grouped_any_jax(column_to_aggregate, group_id)
    elif backend == "numpy":
        result = grouped_any_numpy(column_to_aggregate, group_id)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")

    # Check equality
    np.testing.assert_array_equal(result, expected_res_any)


@parameterize_based_on_dict(
    test_grouped_bool_specs,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "expected_res_all",
    ],
)
def test_grouped_all(backend, column_to_aggregate, group_id, expected_res_all):

    # Calculate result
    if backend == "jax":
        result = grouped_all_jax(column_to_aggregate, group_id)
    elif backend == "numpy":
        result = grouped_all_numpy(column_to_aggregate, group_id)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")

    # Check equality
    np.testing.assert_array_equal(result, expected_res_all)


@parameterize_based_on_dict(test_grouped_numeric_raises_specs)
def test_grouped_sum_raises(
    backend, column_to_aggregate, group_id, error, exception_match
):

    # Calculate result
    with pytest.raises(
        error, match=exception_match,
    ):
        # Calculate result
        if backend == "jax":
            grouped_sum_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_sum_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(test_grouped_numeric_raises_specs)
def test_grouped_mean_raises(
    backend, column_to_aggregate, group_id, error, exception_match
):

    # Calculate result
    with pytest.raises(
        error, match=exception_match,
    ):
        # Calculate result
        if backend == "jax":
            grouped_mean_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_mean_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(test_grouped_numeric_raises_specs)
def test_grouped_max_raises(
    backend, column_to_aggregate, group_id, error, exception_match
):

    # Calculate result
    with pytest.raises(
        error, match=exception_match,
    ):
        # Calculate result
        if backend == "jax":
            grouped_max_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_max_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(test_grouped_numeric_raises_specs)
def test_grouped_min_raises(
    backend, column_to_aggregate, group_id, error, exception_match
):

    # Calculate result
    with pytest.raises(
        error, match=exception_match,
    ):
        # Calculate result
        if backend == "jax":
            grouped_min_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_min_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(test_grouped_bool_raises_specs)
def test_grouped_any_raises(
    backend, column_to_aggregate, group_id, error, exception_match
):

    # Calculate result
    with pytest.raises(
        error, match=exception_match,
    ):
        # Calculate result
        if backend == "jax":
            grouped_any_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_any_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(test_grouped_bool_raises_specs)
def test_grouped_all_raises(
    backend, column_to_aggregate, group_id, error, exception_match
):

    # Calculate result
    with pytest.raises(
        error, match=exception_match,
    ):
        # Calculate result
        if backend == "jax":
            grouped_all_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_all_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")
