import copy

import numpy
import pytest
from _gettsim.aggregation import (
    grouped_all,
    grouped_any,
    grouped_count,
    grouped_cumsum,
    grouped_max,
    grouped_mean,
    grouped_min,
    grouped_sum,
    sum_values_by_index,
)
from _gettsim.config import USE_JAX
from _gettsim.config import numpy_or_jax as np


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


test_grouped_specs = {
    "constant_column": {
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
    "constant_column_group_id_unsorted": {
        "column_to_aggregate": np.array([1.0, 1.0, 1.0, 1.0, 1.0]),
        "group_id": np.array([0, 1, 0, 1, 0]),
        "expected_res_sum": np.array([3, 2, 3, 2, 3]),
        "expected_res_mean": np.array([1, 1, 1, 1, 1]),
        "expected_res_max": np.array([1, 1, 1, 1, 1]),
        "expected_res_min": np.array([1, 1, 1, 1, 1]),
        "expected_res_count": np.array([3, 2, 3, 2, 3]),
        "expected_res_cumsum": np.array([1, 1, 2, 2, 3]),
    },
    "basic_case": {
        "column_to_aggregate": np.array([0, 1, 2, 3, 4]),
        "group_id": np.array([0, 0, 1, 1, 1]),
        "expected_res_sum": np.array([1, 1, 9, 9, 9]),
        "expected_res_max": np.array([1, 1, 4, 4, 4]),
        "expected_res_min": np.array([0, 0, 2, 2, 2]),
        "expected_res_any": np.array([True, True, True, True, True]),
        "expected_res_all": np.array([False, False, True, True, True]),
        "expected_res_cumsum": np.array([0, 1, 2, 5, 9]),
    },
    "unique_group_ids_with_gaps": {
        "column_to_aggregate": np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
        "group_id": np.array([0, 0, 3, 3, 3]),
        "expected_res_sum": np.array([1, 1, 9, 9, 9]),
        "expected_res_mean": np.array([0.5, 0.5, 3, 3, 3]),
        "expected_res_max": np.array([1, 1, 4, 4, 4]),
        "expected_res_min": np.array([0, 0, 2, 2, 2]),
        "expected_res_count": np.array([2, 2, 3, 3, 3]),
        "expected_res_cumsum": np.array([0, 1, 2, 5, 9]),
    },
    "float_column": {
        "column_to_aggregate": np.array([0, 1.5, 2, 3, 4]),
        "group_id": np.array([0, 0, 3, 3, 3]),
        "expected_res_sum": np.array([1.5, 1.5, 9, 9, 9]),
        "expected_res_mean": np.array([0.75, 0.75, 3, 3, 3]),
        "expected_res_max": np.array([1.5, 1.5, 4, 4, 4]),
        "expected_res_min": np.array([0, 0, 2, 2, 2]),
        "expected_res_cumsum": np.array([0, 1.5, 2, 5, 9]),
    },
    "more_than_two_groups": {
        "column_to_aggregate": np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
        "group_id": np.array([1, 0, 1, 1, 3]),
        "expected_res_sum": np.array([5, 1, 5, 5, 4]),
        "expected_res_mean": np.array([5 / 3, 1, 5 / 3, 5 / 3, 4]),
        "expected_res_max": np.array([3, 1, 3, 3, 4]),
        "expected_res_min": np.array([0, 1, 0, 0, 4]),
        "expected_res_count": np.array([3, 1, 3, 3, 1]),
        "expected_res_cumsum": np.array([0, 1, 2, 5, 4]),
    },
    "basic_case_bool": {
        "column_to_aggregate": np.array([True, False, True, False, False]),
        "group_id": np.array([0, 0, 1, 1, 1]),
        "expected_res_any": np.array([True, True, True, True, True]),
        "expected_res_all": np.array([False, False, False, False, False]),
        "expected_res_sum": np.array([1, 1, 1, 1, 1]),
        "expected_res_cumsum": np.array([1, 1, 1, 1, 1]),
    },
    "group_id_unsorted_bool": {
        "column_to_aggregate": np.array([True, False, True, True, True]),
        "group_id": np.array([0, 1, 0, 1, 0]),
        "expected_res_any": np.array([True, True, True, True, True]),
        "expected_res_all": np.array([True, False, True, False, True]),
        "expected_res_sum": np.array([3, 1, 3, 1, 3]),
        "expected_res_cumsum": np.array([1, 0, 2, 1, 3]),
    },
    "unique_group_ids_with_gaps_bool": {
        "column_to_aggregate": np.array([True, False, False, False, False]),
        "group_id": np.array([0, 0, 3, 3, 3]),
        "expected_res_any": np.array([True, True, False, False, False]),
        "expected_res_all": np.array([False, False, False, False, False]),
        "expected_res_sum": np.array([1, 1, 0, 0, 0]),
        "expected_res_cumsum": np.array([1, 1, 0, 0, 0]),
    },
    "sum_values_by_index": {
        "column_to_aggregate": np.array([10, 20, 30, 40, 50]),
        "id_col": np.array([-1, -1, 8, 8, 10]),
        "p_id_col": np.array([7, 8, 9, 10, 11]),
        "expected_res": np.array([0, 70, 0, 50, 0]),
    },
}
if not USE_JAX:
    test_grouped_specs["datetime"] = {
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
    }


test_grouped_raises_specs = {
    "dtype_boolean": {
        "column_to_aggregate": np.array([True, True, True, False, False]),
        "group_id": np.array([0, 0, 1, 1, 1]),
        "error_mean": TypeError,
        "error_max": TypeError,
        "error_min": TypeError,
        "exception_match": "grouped_",
    },
    "float_group_id": {
        "column_to_aggregate": np.array([0, 1, 2, 3, 4]),
        "group_id": np.array([0, 0, 3.5, 3.5, 3.5]),
        "p_id_col": np.array([0, 1, 2, 3, 4]),
        "error_sum": TypeError,
        "error_mean": TypeError,
        "error_max": TypeError,
        "error_min": TypeError,
        "error_cumsum": TypeError,
        "error_sum_values_by_index": TypeError,
        "exception_match": "The dtype of group_id must be integer.",
    },
    "dtype_float": {
        "column_to_aggregate": np.array([1.5, 2, 3.5, 4, 5]),
        "group_id": np.array([0, 0, 1, 1, 1]),
        "error_any": TypeError,
        "error_all": TypeError,
        "exception_match": "grouped_",
    },
    "dtype_integer": {
        "column_to_aggregate": np.array([1, 2, 3, 4, 5]),
        "group_id": np.array([0, 0, 1, 1, 1]),
        "error_mean": TypeError,
        "exception_match": "grouped_",
    },
    "float_group_id_bool": {
        "column_to_aggregate": np.array([True, True, True, False, False]),
        "group_id": np.array([0, 0, 3.5, 3.5, 3.5]),
        "error_any": TypeError,
        "error_all": TypeError,
        "exception_match": "The dtype of group_id must be integer.",
    },
}
if not USE_JAX:
    test_grouped_raises_specs["dtype_string"] = {
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
    }
    test_grouped_raises_specs["datetime"] = {
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
    }


@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "expected_res_sum",
    ],
)
def test_grouped_sum(column_to_aggregate, group_id, expected_res_sum):
    result = grouped_sum(column_to_aggregate, group_id)
    # Check equality
    numpy.testing.assert_array_almost_equal(result, expected_res_sum)


@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "expected_res_mean",
    ],
)
def test_grouped_mean(column_to_aggregate, group_id, expected_res_mean):
    result = grouped_mean(column_to_aggregate, group_id)
    numpy.testing.assert_array_almost_equal(result, expected_res_mean)


@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "expected_res_max",
    ],
)
def test_grouped_max(column_to_aggregate, group_id, expected_res_max):
    result = grouped_max(column_to_aggregate, group_id)
    numpy.testing.assert_array_equal(result, expected_res_max)


@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "expected_res_min",
    ],
)
def test_grouped_min(column_to_aggregate, group_id, expected_res_min):
    result = grouped_min(column_to_aggregate, group_id)
    numpy.testing.assert_array_equal(result, expected_res_min)


@pytest.mark.xfail()
@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "expected_res_cumsum",
    ],
)
def test_grouped_cumsum(column_to_aggregate, group_id, expected_res_cumsum):
    result = grouped_cumsum(column_to_aggregate, group_id)
    numpy.testing.assert_array_almost_equal(result, expected_res_cumsum)


@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=["group_id", "expected_res_count"],
)
def test_grouped_count(group_id, expected_res_count):
    result = grouped_count(group_id)
    numpy.testing.assert_array_almost_equal(result, expected_res_count)


@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "expected_res_any",
    ],
)
def test_grouped_any(column_to_aggregate, group_id, expected_res_any):
    result = grouped_any(column_to_aggregate, group_id)
    numpy.testing.assert_array_almost_equal(result, expected_res_any)


@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "expected_res_all",
    ],
)
def test_grouped_all(column_to_aggregate, group_id, expected_res_all):
    result = grouped_all(column_to_aggregate, group_id)
    numpy.testing.assert_array_almost_equal(result, expected_res_all)


@parameterize_based_on_dict(
    test_grouped_raises_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "error_sum",
        "exception_match",
    ],
)
def test_grouped_sum_raises(column_to_aggregate, group_id, error_sum, exception_match):
    with pytest.raises(
        error_sum,
        match=exception_match,
    ):
        grouped_sum(column_to_aggregate, group_id)


@parameterize_based_on_dict(
    test_grouped_raises_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "error_mean",
        "exception_match",
    ],
)
def test_grouped_mean_raises(
    column_to_aggregate, group_id, error_mean, exception_match
):
    with pytest.raises(
        error_mean,
        match=exception_match,
    ):
        grouped_mean(column_to_aggregate, group_id)


@parameterize_based_on_dict(
    test_grouped_raises_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "error_max",
        "exception_match",
    ],
)
def test_grouped_max_raises(column_to_aggregate, group_id, error_max, exception_match):
    with pytest.raises(
        error_max,
        match=exception_match,
    ):
        grouped_max(column_to_aggregate, group_id)


@parameterize_based_on_dict(
    test_grouped_raises_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "error_min",
        "exception_match",
    ],
)
def test_grouped_min_raises(column_to_aggregate, group_id, error_min, exception_match):
    with pytest.raises(
        error_min,
        match=exception_match,
    ):
        grouped_min(column_to_aggregate, group_id)


@parameterize_based_on_dict(
    test_grouped_raises_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "error_any",
        "exception_match",
    ],
)
def test_grouped_any_raises(column_to_aggregate, group_id, error_any, exception_match):
    with pytest.raises(
        error_any,
        match=exception_match,
    ):
        grouped_any(column_to_aggregate, group_id)


@parameterize_based_on_dict(
    test_grouped_raises_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "error_all",
        "exception_match",
    ],
)
def test_grouped_all_raises(column_to_aggregate, group_id, error_all, exception_match):
    with pytest.raises(
        error_all,
        match=exception_match,
    ):
        grouped_all(column_to_aggregate, group_id)


@pytest.mark.xfail()
@parameterize_based_on_dict(
    test_grouped_raises_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "error_cumsum",
        "exception_match",
    ],
)
def test_grouped_cumsum_raises(
    column_to_aggregate, group_id, error_cumsum, exception_match
):
    with pytest.raises(
        error_cumsum,
        match=exception_match,
    ):
        grouped_cumsum(column_to_aggregate, group_id)


@parameterize_based_on_dict(
    test_grouped_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "id_col",
        "p_id_col",
        "expected_res",
    ],
)
def test_sum_values_by_index(column_to_aggregate, id_col, p_id_col, expected_res):
    result = sum_values_by_index(
        column=column_to_aggregate, id_col=id_col, p_id_col=p_id_col
    )
    numpy.testing.assert_array_almost_equal(result, expected_res)


@parameterize_based_on_dict(
    test_grouped_raises_specs,
    keys_of_test_cases=[
        "column_to_aggregate",
        "group_id",
        "p_id_col",
        "error_sum_values_by_index",
        "exception_match",
    ],
)
def test_sum_values_by_index_raises(
    column_to_aggregate, group_id, p_id_col, error_sum_values_by_index, exception_match
):
    with pytest.raises(
        error_sum_values_by_index,
        match=exception_match,
    ):
        sum_values_by_index(
            column=column_to_aggregate, id_col=group_id, p_id_col=p_id_col
        )
