import numpy as np
import pytest

from gettsim.shared import any_on_group_level
from gettsim.shared import max_on_group_level
from gettsim.shared import mean_on_group_level
from gettsim.shared import sum_on_group_level

test_sum_on_group_level_specs = {
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
    "float_group_id": (
        np.array([0, 1, 2, 3, 4]),
        np.array([0, 0, 3.5, 3.5, 3.5]),
        np.array([1, 1, 9, 9, 9]),
    ),
}

test_mean_on_group_level_specs = {
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


test_max_on_group_level_specs = {
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
test_any_on_group_level_specs = {
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

test_sum_on_group_level_raises_specs = {
    "dtype_boolean": (
        np.array([True, True, True, False, False]),
        np.array([0, 0, 1, 1, 1]),
        "sum_on_group_level was applied",
    ),
    "dtype_string": (
        np.array(["0", "1", "2", "3", "4"]),
        np.array([0, 0, 1, 1, 1]),
        "sum_on_group_level was applied",
    ),
}
test_max_on_group_level_raises_specs = {
    "dtype_boolean": (
        np.array([True, True, True, False, False]),
        np.array([0, 0, 1, 1, 1]),
        "max_on_group_level was applied",
    ),
    "dtype_string": (
        np.array(["0", "1", "2", "3", "4"]),
        np.array([0, 0, 1, 1, 1]),
        "max_on_group_level was applied",
    ),
}

test_any_on_group_level_raises_specs = {
    "dtype_numerical": (
        np.array([1, 2, 3, 4, 5]),
        np.array([0, 0, 1, 1, 1]),
        "any_on_group_level was applied",
    ),
    "dtype_string": (
        np.array(["0", "1", "2", "3", "4"]),
        np.array([0, 0, 1, 1, 1]),
        "any_on_group_level was applied",
    ),
}


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_sum_on_group_level_specs.values(),
    ids=test_sum_on_group_level_specs.keys(),
)
def test_sum_on_group_level(column_to_aggregate, group_id, exp_aggregated_column):

    # Calculate result
    result = sum_on_group_level(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_mean_on_group_level_specs.values(),
    ids=test_mean_on_group_level_specs.keys(),
)
def test_mean_on_group_level(column_to_aggregate, group_id, exp_aggregated_column):
    # Calculate result
    result = mean_on_group_level(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_max_on_group_level_specs.values(),
    ids=test_max_on_group_level_specs.keys(),
)
def test_max_on_group_level(column_to_aggregate, group_id, exp_aggregated_column):
    # Calculate result
    result = max_on_group_level(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exp_aggregated_column",
    test_any_on_group_level_specs.values(),
    ids=test_any_on_group_level_specs.keys(),
)
def test_any_on_group_level(column_to_aggregate, group_id, exp_aggregated_column):
    # Calculate result
    result = any_on_group_level(column_to_aggregate, group_id)

    # Check equality
    np.testing.assert_array_equal(result, exp_aggregated_column)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exception_match",
    test_sum_on_group_level_raises_specs.values(),
    ids=test_sum_on_group_level_raises_specs.keys(),
)
def test_sum_on_group_level_raises(column_to_aggregate, group_id, exception_match):
    with pytest.raises(
        ValueError, match=exception_match,
    ):
        # Calculate result
        sum_on_group_level(column_to_aggregate, group_id)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exception_match",
    test_max_on_group_level_raises_specs.values(),
    ids=test_max_on_group_level_raises_specs.keys(),
)
def test_max_on_group_level_raises(column_to_aggregate, group_id, exception_match):
    with pytest.raises(
        ValueError, match=exception_match,
    ):
        # Calculate result
        max_on_group_level(column_to_aggregate, group_id)


@pytest.mark.parametrize(
    "column_to_aggregate, group_id, exception_match",
    test_any_on_group_level_raises_specs.values(),
    ids=test_any_on_group_level_raises_specs.keys(),
)
def test_any_on_group_level_raises(column_to_aggregate, group_id, exception_match):
    with pytest.raises(
        ValueError, match=exception_match,
    ):
        # Calculate result
        any_on_group_level(column_to_aggregate, group_id)
