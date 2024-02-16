import warnings

import numpy
import numpy_groupies as npg


def grouped_count(group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_count")
    out_on_hh = npg.aggregate(
        group_id, numpy.ones(len(group_id)), func="sum", fill_value=0
    )

    out = out_on_hh[group_id]
    return out


def grouped_sum(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_sum")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="grouped_sum")

    out_on_hh = npg.aggregate(group_id, column, func="sum", fill_value=0)

    # Expand to individual level
    out = out_on_hh[group_id]
    return out


def grouped_mean(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_mean")
    fail_if_dtype_not_float(column, agg_func="grouped_mean")

    out_on_hh = npg.aggregate(group_id, column, func="mean", fill_value=0)

    # Expand to individual level
    out = out_on_hh[group_id]
    return out


def grouped_max(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_max")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="grouped_max")

    # For datetime, convert to integer (as numpy_groupies can handle datetime only if
    # numba is installed)
    if numpy.issubdtype(column.dtype, numpy.datetime64):
        dtype = column.dtype
        float_col = column.astype("datetime64[D]").astype(int)

        out_on_hh_float = npg.aggregate(group_id, float_col, func="max")

        out_on_hh = out_on_hh_float.astype("datetime64[D]").astype(dtype)

        # Expand to individual level
        out = out_on_hh[group_id]

    else:
        out_on_hh = npg.aggregate(group_id, column, func="max")

        # Expand to individual level
        out = out_on_hh[group_id]
    return out


def grouped_min(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_min")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="grouped_min")

    # For datetime, convert to integer (as numpy_groupies can handle datetime only if
    # numba is installed)

    if numpy.issubdtype(column.dtype, numpy.datetime64) or numpy.issubdtype(
        column.dtype, numpy.timedelta64
    ):
        dtype = column.dtype
        float_col = column.astype("datetime64[D]").astype(int)

        out_on_hh_float = npg.aggregate(group_id, float_col, func="min")

        out_on_hh = out_on_hh_float.astype("datetime64[D]").astype(dtype)

        # Expand to individual level
        out = out_on_hh[group_id]

    else:
        out_on_hh = npg.aggregate(group_id, column, func="min")

        # Expand to individual level
        out = out_on_hh[group_id]
    return out


def grouped_any(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_any")
    fail_if_dtype_not_boolean_or_int(column, agg_func="grouped_any")

    out_on_hh = npg.aggregate(group_id, column, func="any", fill_value=0)

    # Expand to individual level
    out = out_on_hh[group_id]
    return out


def grouped_all(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_all")
    fail_if_dtype_not_boolean_or_int(column, agg_func="grouped_all")

    out_on_hh = npg.aggregate(group_id, column, func="all", fill_value=0)

    # Expand to individual level
    out = out_on_hh[group_id]
    return out


def grouped_cumsum(column, group_id):
    warnings.warn(
        "'grouped_cumsum' is deprecated. It won't be supported anymore in a future "
        "version",
        DeprecationWarning,
        stacklevel=2,
    )
    fail_if_dtype_not_int(group_id, agg_func="grouped_sum")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="grouped_sum")
    if column.dtype == bool:
        column = column.astype(int)
    out = npg.aggregate(group_id, column, func="cumsum", fill_value=0)

    return out


def count_by_p_id(p_id_to_aggregate_by, p_id_to_store_by):
    fail_if_dtype_not_int(p_id_to_aggregate_by, agg_func="count_by_p_id")
    fail_if_dtype_not_int(p_id_to_store_by, agg_func="count_by_p_id")

    raise NotImplementedError


def sum_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    fail_if_dtype_not_int(p_id_to_aggregate_by, agg_func="sum_by_p_id")
    fail_if_dtype_not_int(p_id_to_store_by, agg_func="sum_by_p_id")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="sum_by_p_id")

    if column.dtype in ["bool"]:
        column = column.astype(int)
    out = numpy.zeros_like(p_id_to_store_by, dtype=column.dtype)

    map_p_id_to_position = {p_id: iloc for iloc, p_id in enumerate(p_id_to_store_by)}

    for iloc, id_receiver in enumerate(p_id_to_aggregate_by):
        if id_receiver >= 0:
            out[map_p_id_to_position[id_receiver]] += column[iloc]
    return out


def mean_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    fail_if_dtype_not_int(p_id_to_aggregate_by, agg_func="mean_by_p_id")
    fail_if_dtype_not_int(p_id_to_store_by, agg_func="mean_by_p_id")
    fail_if_dtype_not_float(column, agg_func="mean_by_p_id")
    raise NotImplementedError


def max_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    fail_if_dtype_not_int(p_id_to_aggregate_by, agg_func="max_by_p_id")
    fail_if_dtype_not_int(p_id_to_store_by, agg_func="max_by_p_id")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="max_by_p_id")
    raise NotImplementedError


def min_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    fail_if_dtype_not_int(p_id_to_aggregate_by, agg_func="min_by_p_id")
    fail_if_dtype_not_int(p_id_to_store_by, agg_func="min_by_p_id")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="min_by_p_id")
    raise NotImplementedError


def any_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    fail_if_dtype_not_int(p_id_to_aggregate_by, agg_func="any_by_p_id")
    fail_if_dtype_not_int(p_id_to_store_by, agg_func="any_by_p_id")
    fail_if_dtype_not_boolean_or_int(column, agg_func="any_by_p_id")
    raise NotImplementedError


def all_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    fail_if_dtype_not_int(p_id_to_store_by, agg_func="all_by_p_id")
    fail_if_dtype_not_int(p_id_to_aggregate_by, agg_func="all_by_p_id")
    fail_if_dtype_not_boolean_or_int(column, agg_func="all_by_p_id")
    raise NotImplementedError


def fail_if_dtype_not_numeric(column, agg_func):
    if not numpy.issubdtype(column.dtype, numpy.number):
        raise TypeError(
            f"Aggregation function {agg_func} was applied to a column "
            f"with dtype {column.dtype}. Allowed are only numerical dtypes."
        )


def fail_if_dtype_not_float(column, agg_func):
    if not numpy.issubdtype(column.dtype, numpy.floating):
        raise TypeError(
            f"Aggregation function {agg_func} was applied to a column "
            f"with dtype {column.dtype}. Allowed is only float."
        )


def fail_if_dtype_not_int(p_id_to_aggregate_by, agg_func):
    if not numpy.issubdtype(p_id_to_aggregate_by.dtype, numpy.integer):
        raise TypeError(
            f"The dtype of id columns must be integer. Aggregation function {agg_func} "
            f"was applied to a id columns that has dtype {p_id_to_aggregate_by.dtype}."
        )


def fail_if_dtype_not_numeric_or_boolean(column, agg_func):
    if not (numpy.issubdtype(column.dtype, numpy.number) or column.dtype == "bool"):
        raise TypeError(
            f"Aggregation function {agg_func} was applied to a column with dtype "
            f"{column.dtype}. Allowed are only numerical or Boolean dtypes."
        )


def fail_if_dtype_not_numeric_or_datetime(column, agg_func):
    if not (
        numpy.issubdtype(column.dtype, numpy.number)
        or numpy.issubdtype(column.dtype, numpy.datetime64)
    ):
        raise TypeError(
            f"Aggregation function {agg_func} was applied to a column with dtype "
            f"{column.dtype}. Allowed are only numerical or datetime dtypes."
        )


def fail_if_dtype_not_boolean_or_int(column, agg_func):
    if not (
        numpy.issubdtype(column.dtype, numpy.integer)
        or numpy.issubdtype(column.dtype, numpy.bool_)
    ):
        raise TypeError(
            f"Aggregation function {agg_func} was applied to a column with dtype "
            f"{column.dtype}. Allowed are only Boolean and int dtypes."
        )
