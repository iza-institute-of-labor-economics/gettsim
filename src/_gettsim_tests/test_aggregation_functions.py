import copy
from collections import ChainMap

import numpy as np
import pytest
from _gettsim.aggregation_jax import grouped_all as grouped_all_jax
from _gettsim.aggregation_jax import grouped_any as grouped_any_jax
from _gettsim.aggregation_jax import grouped_count as grouped_count_jax
from _gettsim.aggregation_jax import grouped_max as grouped_max_jax
from _gettsim.aggregation_jax import grouped_mean as grouped_mean_jax
from _gettsim.aggregation_jax import grouped_min as grouped_min_jax
from _gettsim.aggregation_jax import grouped_sum as grouped_sum_jax
from _gettsim.aggregation_numpy import grouped_all as grouped_all_numpy
from _gettsim.aggregation_numpy import grouped_any as grouped_any_numpy
from _gettsim.aggregation_numpy import grouped_count as grouped_count_numpy
from _gettsim.aggregation_numpy import grouped_cumsum as grouped_cumsum_numpy
from _gettsim.aggregation_numpy import grouped_max as grouped_max_numpy
from _gettsim.aggregation_numpy import grouped_mean as grouped_mean_numpy
from _gettsim.aggregation_numpy import grouped_min as grouped_min_numpy
from _gettsim.aggregation_numpy import grouped_sum as grouped_sum_numpy
from _gettsim.config import USE_JAX


def parameterize_based_on_dict(test_cases, keys_of_test_cases=None):
    """Apply pytest.mark.parametrize based on a dictionary."""
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
            if all(e in v for e in keys_of_test_cases)
        }

    # Return parametrization
    return pytest.mark.parametrize(
        argnames=(argnames := sorted({k for v in test_cases.values() for k in v})),
        argvalues=[[v.get(k) for k in argnames] for v in test_cases.values()],
        ids=test_cases.keys(),
    )


available_backends = ["numpy", "jax"] if USE_JAX else ["numpy"]
test_grouped_specs = [
    {
        f"constant_column_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([1, 1, 1, 1, 1]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "expected_res_sum": np.array([2, 2, 3, 3, 3]),
            "expected_res_max": np.array([1, 1, 1, 1, 1]),
            "expected_res_min": np.array([1, 1, 1, 1, 1]),
            "expected_res_count": np.array([2, 2, 3, 3, 3]),
            "expected_res_any": np.array([True, True, True, True, True]),
            "expected_res_all": np.array([True, True, True, True, True]),
            "expected_res_cumsum": np.array([1, 2, 1, 2, 3]),
        },
        f"constant_column_group_id_unsorted_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([1.0, 1.0, 1.0, 1.0, 1.0]),
            "group_id": np.array([0, 1, 0, 1, 0]),
            "expected_res_sum": np.array([3, 2, 3, 2, 3]),
            "expected_res_mean": np.array([1, 1, 1, 1, 1]),
            "expected_res_max": np.array([1, 1, 1, 1, 1]),
            "expected_res_min": np.array([1, 1, 1, 1, 1]),
            "expected_res_count": np.array([3, 2, 3, 2, 3]),
            "expected_res_cumsum": np.array([1, 1, 2, 2, 3]),
        },
        f"basic_case_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0, 1, 2, 3, 4]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "expected_res_sum": np.array([1, 1, 9, 9, 9]),
            "expected_res_max": np.array([1, 1, 4, 4, 4]),
            "expected_res_min": np.array([0, 0, 2, 2, 2]),
            "expected_res_any": np.array([True, True, True, True, True]),
            "expected_res_all": np.array([False, False, True, True, True]),
            "expected_res_cumsum": np.array([0, 1, 2, 5, 9]),
        },
        f"unique_group_ids_with_gaps_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
            "group_id": np.array([0, 0, 3, 3, 3]),
            "expected_res_sum": np.array([1, 1, 9, 9, 9]),
            "expected_res_mean": np.array([0.5, 0.5, 3, 3, 3]),
            "expected_res_max": np.array([1, 1, 4, 4, 4]),
            "expected_res_min": np.array([0, 0, 2, 2, 2]),
            "expected_res_count": np.array([2, 2, 3, 3, 3]),
            "expected_res_cumsum": np.array([0, 1, 2, 5, 9]),
        },
        f"float_column_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0, 1.5, 2, 3, 4]),
            "group_id": np.array([0, 0, 3, 3, 3]),
            "expected_res_sum": np.array([1.5, 1.5, 9, 9, 9]),
            "expected_res_mean": np.array([0.75, 0.75, 3, 3, 3]),
            "expected_res_max": np.array([1.5, 1.5, 4, 4, 4]),
            "expected_res_min": np.array([0, 0, 2, 2, 2]),
            "expected_res_cumsum": np.array([0, 1.5, 2, 5, 9]),
        },
        f"more_than_two_groups{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
            "group_id": np.array([1, 0, 1, 1, 3]),
            "expected_res_sum": np.array([5, 1, 5, 5, 4]),
            "expected_res_mean": np.array([5 / 3, 1, 5 / 3, 5 / 3, 4]),
            "expected_res_max": np.array([3, 1, 3, 3, 4]),
            "expected_res_min": np.array([0, 1, 0, 0, 4]),
            "expected_res_count": np.array([3, 1, 3, 3, 1]),
            "expected_res_cumsum": np.array([0, 1, 2, 5, 4]),
        },
        f"basic_case_bool_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, False, True, False, False]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "expected_res_any": np.array([True, True, True, True, True]),
            "expected_res_all": np.array([False, False, False, False, False]),
            "expected_res_sum": np.array([1, 1, 1, 1, 1]),
            "expected_res_cumsum": np.array([1, 1, 1, 1, 1]),
        },
        f"group_id_unsorted_bool_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, False, True, True, True]),
            "group_id": np.array([0, 1, 0, 1, 0]),
            "expected_res_any": np.array([True, True, True, True, True]),
            "expected_res_all": np.array([True, False, True, False, True]),
            "expected_res_sum": np.array([3, 1, 3, 1, 3]),
            "expected_res_cumsum": np.array([1, 0, 2, 1, 3]),
        },
        f"unique_group_ids_with_gaps_bool_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, False, False, False, False]),
            "group_id": np.array([0, 0, 3, 3, 3]),
            "expected_res_any": np.array([True, True, False, False, False]),
            "expected_res_all": np.array([False, False, False, False, False]),
            "expected_res_sum": np.array([1, 1, 0, 0, 0]),
            "expected_res_cumsum": np.array([1, 1, 0, 0, 0]),
        },
    }
    for backend in available_backends
] + [
    {
        f"datetime_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array(
                [
                    np.datetime64("2000"),
                    np.datetime64("2001"),
                    np.datetime64("2002"),
                    np.datetime64("2003"),
                    np.datetime64("2004"),
                ]
            ),
            "group_id": np.array([1, 0, 1, 1, 1]),
            "expected_res_max": np.array(
                [
                    np.datetime64("2004"),
                    np.datetime64("2001"),
                    np.datetime64("2004"),
                    np.datetime64("2004"),
                    np.datetime64("2004"),
                ]
            ),
            "expected_res_min": np.array(
                [
                    np.datetime64("2000"),
                    np.datetime64("2001"),
                    np.datetime64("2000"),
                    np.datetime64("2000"),
                    np.datetime64("2000"),
                ]
            ),
        },
    }
    for backend in available_backends
    if backend != "jax"
]
test_grouped_specs_dict = dict(ChainMap(*test_grouped_specs))


test_grouped_raises_specs = [
    {
        f"dtype_boolean_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, True, True, False, False]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error_mean": TypeError,
            "error_max": TypeError,
            "error_min": TypeError,
            "exception_match": "grouped_",
        },
        f"dtype_string_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array(["0", "1", "2", "3", "4"]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error_sum": TypeError,
            "error_mean": TypeError,
            "error_max": TypeError,
            "error_min": TypeError,
            "error_any": TypeError,
            "error_all": TypeError,
            "error_cumsum": TypeError,
            "exception_match": "grouped_",
        },
        f"float_group_id_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([0, 1, 2, 3, 4]),
            "group_id": np.array([0, 0, 3.5, 3.5, 3.5]),
            "error_sum": TypeError,
            "error_mean": TypeError,
            "error_max": TypeError,
            "error_min": TypeError,
            "error_cumsum": TypeError,
            "exception_match": "The dtype of group_id must be integer.",
        },
        f"dtype_float_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([1.5, 2, 3.5, 4, 5]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error_any": TypeError,
            "error_all": TypeError,
            "exception_match": "grouped_",
        },
        f"dtype_integer_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([1, 2, 3, 4, 5]),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error_mean": TypeError,
            "exception_match": "grouped_",
        },
        f"float_group_id_bool_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array([True, True, True, False, False]),
            "group_id": np.array([0, 0, 3.5, 3.5, 3.5]),
            "error_any": TypeError,
            "error_all": TypeError,
            "exception_match": "The dtype of group_id must be integer.",
        },
        f"datetime_{backend}": {
            "backend": backend,
            "column_to_aggregate": np.array(
                [
                    np.datetime64("2000"),
                    np.datetime64("2001"),
                    np.datetime64("2002"),
                    np.datetime64("2003"),
                    np.datetime64("2004"),
                ]
            ),
            "group_id": np.array([0, 0, 1, 1, 1]),
            "error_sum": TypeError,
            "error_mean": TypeError,
            "error_any": TypeError,
            "error_all": TypeError,
            "exception_match": "grouped_",
        },
    }
    for backend in available_backends
]
test_grouped_raises_specs_dict = dict(ChainMap(*test_grouped_raises_specs))


@parameterize_based_on_dict(
    test_grouped_specs_dict,
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
    np.testing.assert_array_almost_equal(result, expected_res_sum)


@parameterize_based_on_dict(
    test_grouped_specs_dict,
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
    np.testing.assert_array_almost_equal(result, expected_res_mean)


@parameterize_based_on_dict(
    test_grouped_specs_dict,
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
    test_grouped_specs_dict,
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
    test_grouped_specs_dict,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "expected_res_cumsum",
    ],
)
def test_grouped_cumsum(backend, column_to_aggregate, group_id, expected_res_cumsum):
    # Calculate result
    if backend == "jax":
        pass
    elif backend == "numpy":
        result = grouped_cumsum_numpy(column_to_aggregate, group_id)
        # Check equality
        np.testing.assert_array_almost_equal(result, expected_res_cumsum)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(
    test_grouped_specs_dict,
    keys_of_test_cases=["backend", "group_id", "expected_res_count"],
)
def test_grouped_count(backend, group_id, expected_res_count):
    # Calculate result
    if backend == "jax":
        result = grouped_count_jax(group_id)
    elif backend == "numpy":
        result = grouped_count_numpy(group_id)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")

    # Check equality
    np.testing.assert_array_almost_equal(result, expected_res_count)


@parameterize_based_on_dict(
    test_grouped_specs_dict,
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
    np.testing.assert_array_almost_equal(result, expected_res_any)


@parameterize_based_on_dict(
    test_grouped_specs_dict,
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
    np.testing.assert_array_almost_equal(result, expected_res_all)


@parameterize_based_on_dict(
    test_grouped_raises_specs_dict,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "error_sum",
        "exception_match",
    ],
)
def test_grouped_sum_raises(
    backend, column_to_aggregate, group_id, error_sum, exception_match
):

    with pytest.raises(
        error_sum,
        match=exception_match,
    ):
        if backend == "jax":
            grouped_sum_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_sum_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(
    test_grouped_raises_specs_dict,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "error_mean",
        "exception_match",
    ],
)
def test_grouped_mean_raises(
    backend, column_to_aggregate, group_id, error_mean, exception_match
):

    with pytest.raises(
        error_mean,
        match=exception_match,
    ):
        if backend == "jax":
            grouped_mean_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_mean_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(
    test_grouped_raises_specs_dict,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "error_max",
        "exception_match",
    ],
)
def test_grouped_max_raises(
    backend, column_to_aggregate, group_id, error_max, exception_match
):

    with pytest.raises(
        error_max,
        match=exception_match,
    ):
        if backend == "jax":
            grouped_max_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_max_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(
    test_grouped_raises_specs_dict,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "error_min",
        "exception_match",
    ],
)
def test_grouped_min_raises(
    backend, column_to_aggregate, group_id, error_min, exception_match
):

    with pytest.raises(
        error_min,
        match=exception_match,
    ):
        if backend == "jax":
            grouped_min_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_min_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(
    test_grouped_raises_specs_dict,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "error_any",
        "exception_match",
    ],
)
def test_grouped_any_raises(
    backend, column_to_aggregate, group_id, error_any, exception_match
):

    with pytest.raises(
        error_any,
        match=exception_match,
    ):
        if backend == "jax":
            grouped_any_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_any_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(
    test_grouped_raises_specs_dict,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "error_all",
        "exception_match",
    ],
)
def test_grouped_all_raises(
    backend, column_to_aggregate, group_id, error_all, exception_match
):

    with pytest.raises(
        error_all,
        match=exception_match,
    ):
        if backend == "jax":
            grouped_all_jax(column_to_aggregate, group_id)
        elif backend == "numpy":
            grouped_all_numpy(column_to_aggregate, group_id)
        else:
            raise ValueError(f"Backend {backend} not supported in this test.")


@parameterize_based_on_dict(
    test_grouped_raises_specs_dict,
    keys_of_test_cases=[
        "backend",
        "column_to_aggregate",
        "group_id",
        "error_cumsum",
        "exception_match",
    ],
)
def test_grouped_cumsum_raises(
    backend, column_to_aggregate, group_id, error_cumsum, exception_match
):

    if backend == "jax":
        pass
    elif backend == "numpy":
        with pytest.raises(
            error_cumsum,
            match=exception_match,
        ):
            grouped_cumsum_numpy(column_to_aggregate, group_id)
    else:
        raise ValueError(f"Backend {backend} not supported in this test.")
