import numpy as np
import pytest

from gettsim.aggregation import grouped_all
from gettsim.aggregation import grouped_any
from gettsim.aggregation import grouped_max
from gettsim.aggregation import grouped_mean
from gettsim.aggregation import grouped_min
from gettsim.aggregation import grouped_sum

test_grouped_sum_specs = {
    "constant_column": (
        np.array([1, 1, 1, 1, 1]),
        np.array([0, 0, 1, 1, 1]),
        np.array([2, 2, 3, 3, 3]),
    ),
    "constant_column_group_id_unsorted": (
        np.array([1, 1, 1, 1, 1]),
        np.array([0, 1, 0, 1, 0]),
        np.array([3, 2, 3, 2, 3]),
    ),
    "basic_case": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 1, 1, 1]),
        np.array([1, 1, 9, 9, 9]),
    ),
    "unique_group_ids_with_gaps": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 3, 3, 3]),
        np.array([1, 1, 9, 9, 9]),
    ),
    "float_column": (
        np.array([0, 1.5, 2, 3, 4]),
        np.array([0, 0, 3, 3, 3]),
        np.array([1.5, 1.5, 9, 9, 9]),
    ),
}

test_grouped_mean_specs = {
    "constant_column": (
        np.array([1, 1, 1, 1, 1]),
        np.array([0, 0, 1, 1, 1]),
        np.array([1, 1, 1, 1, 1]),
    ),
    "constant_column_group_id_unsorted": (
        np.array([1, 1, 1, 1, 1]),
        np.array([0, 1, 0, 1, 0]),
        np.array([1, 1, 1, 1, 1]),
    ),
    "basic_case": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 1, 1, 1]),
        np.array([0.5, 0.5, 3, 3, 3]),
    ),
    "unique_group_ids_with_gaps": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 3, 3, 3]),
        np.array([0.5, 0.5, 3, 3, 3]),
    ),
}


test_grouped_max_specs = {
    "constant_column": (
        np.array([1, 1, 1, 1, 1]),
        np.array([0, 0, 1, 1, 1]),
        np.array([1, 1, 1, 1, 1]),
    ),
    "basic_case": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 1, 1, 1]),
        np.array([1, 1, 4, 4, 4]),
    ),
    "group_id_unsorted": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 1, 0, 1, 1]),
        np.array([2, 4, 2, 4, 4]),
    ),
    "unique_group_ids_with_gaps": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 3, 3, 3]),
        np.array([1, 1, 4, 4, 4]),
    ),
}
test_grouped_min_specs = {
    "constant_column": (
        np.array([1, 1, 1, 1, 1]),
        np.array([0, 0, 1, 1, 1]),
        np.array([1, 1, 1, 1, 1]),
    ),
    "basic_case": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 1, 1, 1]),
        np.array([0, 0, 2, 2, 2]),
    ),
    "group_id_unsorted": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 1, 0, 1, 1]),
        np.array([0, 1, 0, 1, 1]),
    ),
    "unique_group_ids_with_gaps": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 3, 3, 3]),
        np.array([0, 0, 2, 2, 2]),
    ),
}
test_grouped_any_specs = {
    "basic_boolean_case": (
        np.array([True, False, True, False, False]),
        np.array([0, 0, 1, 1, 1]),
        np.array([True, True, True, True, True]),
    ),
    "group_id_unsorted": (
        np.array([True, False, True, False, False]),
        np.array([0, 1, 0, 1, 0]),
        np.array([True, False, True, False, True]),
    ),
    "unique_group_ids_with_gaps": (
        np.array([True, False, False, False, False]),
        np.array([0, 0, 10, 10, 10]),
        np.array([True, True, False, False, False]),
    ),
}

test_grouped_all_specs = {
    "basic_boolean_case": (
        np.array([True, False, True, False, False]),
        np.array([0, 0, 1, 1, 1]),
        np.array([False, False, False, False, False]),
    ),
    "group_id_unsorted": (
        np.array([True, False, True, False, False]),
        np.array([0, 1, 0, 1, 0]),
        np.array([False, False, False, False, False]),
    ),
    "unique_group_ids_with_gaps": (
        np.array([True, True, False, False, False]),
        np.array([0, 0, 10, 10, 10]),
        np.array([True, True, False, False, False]),
    ),
}

test_grouped_sum_raises_specs = {
    "dtype_boolean": (
        np.array([True, True, True, False, False]),
        np.array([0, 0, 1, 1, 1]),
        ValueError,
        "grouped_sum was applied",
    ),
    "dtype_string": (
        np.array(["0", "1", "2", "3", "4"]),
        np.array([0, 0, 1, 1, 1]),
        ValueError,
        "grouped_sum was applied",
    ),
    "float_group_id": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 3.5, 3.5, 3.5]),
        TypeError,
        "group_idx must be of integer type",
    ),
}
test_grouped_max_raises_specs = {
    "dtype_boolean": (
        np.array([True, True, True, False, False]),
        np.array([0, 0, 1, 1, 1]),
        "grouped_max was applied",
    ),
    "dtype_string": (
        np.array(["0", "1", "2", "3", "4"]),
        np.array([0, 0, 1, 1, 1]),
        "grouped_max was applied",
    ),
}

test_grouped_any_raises_specs = {
    "dtype_numerical": (
        np.array([1, 2, 3, 4, 5]),
        np.array([0, 0, 1, 1, 1]),
        "grouped_any was applied",
    ),
    "dtype_string": (
        np.array(["0", "1", "2", "3", "4"]),
        np.array([0, 0, 1, 1, 1]),
        "grouped_any was applied",
    ),
}


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_grouped_sum_specs.values(),
    ids=test_grouped_sum_specs.keys(),
)
def test_grouped_sum(column_to_aggregate, group_id, exp_aggregated_column):

    # Calculate result
    result = grouped_sum(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_grouped_mean_specs.values(),
    ids=test_grouped_mean_specs.keys(),
)
def test_grouped_mean(column_to_aggregate, group_id, exp_aggregated_column):
    # Calculate result
    result = grouped_mean(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_grouped_max_specs.values(),
    ids=test_grouped_max_specs.keys(),
)
def test_grouped_max(column_to_aggregate, group_id, exp_aggregated_column):
    # Calculate result
    result = grouped_max(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_grouped_min_specs.values(),
    ids=test_grouped_min_specs.keys(),
)
def test_grouped_min(column_to_aggregate, group_id, exp_aggregated_column):
    # Calculate result
    result = grouped_min(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_grouped_any_specs.values(),
    ids=test_grouped_any_specs.keys(),
)
def test_grouped_any(column_to_aggregate, group_id, exp_aggregated_column):
    # Calculate result
    result = grouped_any(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_grouped_all_specs.values(),
    ids=test_grouped_all_specs.keys(),
)
def test_grouped_all(column_to_aggregate, group_id, exp_aggregated_column):
    # Calculate result
    result = grouped_all(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, error, exception_match",
    test_grouped_sum_raises_specs.values(),
    ids=test_grouped_sum_raises_specs.keys(),
)
def test_grouped_sum_raises(column_to_aggregate, group_id, error, exception_match):
    with pytest.raises(
        error, match=exception_match,
    ):
        # Calculate result
        grouped_sum(column_to_aggregate, group_id)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exception_match",
    test_grouped_max_raises_specs.values(),
    ids=test_grouped_max_raises_specs.keys(),
)
def test_grouped_max_raises(column_to_aggregate, group_id, exception_match):
    with pytest.raises(
        ValueError, match=exception_match,
    ):
        # Calculate result
        grouped_max(column_to_aggregate, group_id)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exception_match",
    test_grouped_any_raises_specs.values(),
    ids=test_grouped_any_raises_specs.keys(),
)
def test_grouped_any_raises(column_to_aggregate, group_id, exception_match):
    with pytest.raises(
        ValueError, match=exception_match,
    ):
        # Calculate result
        grouped_any(column_to_aggregate, group_id)
