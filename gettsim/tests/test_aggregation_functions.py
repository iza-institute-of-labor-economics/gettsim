import numpy as np
import pytest

from gettsim.shared import sum_on_group_level

# from gettsim.shared import max_on_group_level

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
    "boolean_column": (
        np.array([True, True, True, False, False]),
        np.array([0, 0, 1, 1, 1]),
        np.array([2, 2, 1, 1, 1]),
    ),
    "mixed_numerical_boolean_column": (
        np.array([True, 2, True, False, False]),
        np.array([0, 0, 1, 1, 1]),
        np.array([3, 3, 1, 1, 1]),
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


# @pytest.mark.parametrize(
#     "column_to_aggregate, group_id, exp_aggregated_column",
#     {
#         "constant_column": (
#             np.array([1, 1, 1, 1, 1]),
#             np.array([0, 0, 1, 1, 1]),
#             np.array([1, 1, 1, 1, 1]),
#         ),
#         "basic_case": (
#             np.array([0, 1, 2, 3, 4]),
#             np.array([0, 0, 1, 1, 1]),
#             np.array([1, 1, 4, 4, 4]),
#         ),
#         "group_id_unsorted": (
#             np.array([0, 1, 2, 3, 4]),
#             np.array([0, 1, 0, 1, 1]),
#             np.array([2, 4, 2, 4, 4]),
#         ),
#         "unique_group_ids_with_gaps": (
#             np.array([0, 1, 2, 3, 4]),
#             np.array([0, 0, 3, 3, 3]),
#             np.array([1, 1, 4, 4, 4]),
#         ),
#         "boolean_column": (
#             np.array([True, True, True, False, False]),
#             np.array([0, 0, 1, 1, 1]),
#             np.array([True, True, True, True, True]),
#         ),
#         "boolean_column_2": (
#             np.array([True, False, False, False, False]),
#             np.array([0, 0, 1, 1, 1]),
#             np.array([True, True, False, False, False]),
#         ),
#     },
# )
# def test_max_on_group_level(column_to_aggregate, group_id, exp_aggregated_column):

#     # Calculate result
#     result = max_on_group_level(column_to_aggregate, group_id)

#     # Check equality
#     np.testing.assert_array_equal(result, exp_aggregated_column)
