import warnings

import numpy
import numpy.typing as npt
import numpy_groupies as npg


def grouped_count(group_id):
    fail_if_dtype_not_int(group_id, agg_func="count")
    out_on_hh = npg.aggregate(
        group_id, numpy.ones(len(group_id)), func="sum", fill_value=0
    )

    out = out_on_hh[group_id]
    return out


def grouped_sum(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="sum")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="sum")

    out_on_hh = npg.aggregate(group_id, column, func="sum", fill_value=0)

    # Expand to individual level
    out = out_on_hh[group_id]
    return out


def grouped_mean(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="mean")
    fail_if_dtype_not_float(column, agg_func="mean")

    out_on_hh = npg.aggregate(group_id, column, func="mean", fill_value=0)

    # Expand to individual level
    out = out_on_hh[group_id]
    return out


def grouped_max(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="max")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="max")

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
    fail_if_dtype_not_int(group_id, agg_func="min")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="min")

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
    fail_if_dtype_not_int(group_id, agg_func="any")
    fail_if_dtype_not_boolean_or_int(column, agg_func="any")

    out_on_hh = npg.aggregate(group_id, column, func="any", fill_value=0)

    # Expand to individual level
    out = out_on_hh[group_id]
    return out


def grouped_all(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="all")
    fail_if_dtype_not_boolean_or_int(column, agg_func="all")

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
    fail_if_dtype_not_int(group_id, agg_func="sum")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="sum")
    if column.dtype == bool:
        column = column.astype(int)
    out = npg.aggregate(group_id, column, func="cumsum", fill_value=0)

    return out


def sum_values_by_index(
    column: npt.NDArray[numpy.int64 | numpy.float64 | numpy.bool_],
    id_col: npt.NDArray[numpy.int64],
    p_id_col: npt.NDArray[numpy.int64],
) -> numpy.ndarray:
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="sum_values_by_index")
    fail_if_dtype_not_int(id_col, agg_func="sum_values_by_index")
    if column.dtype == bool:
        column = column.astype(int)
    out = numpy.zeros_like(p_id_col, dtype=column.dtype)

    map_p_id_to_position = {p_id: position for position, p_id in enumerate(p_id_col)}

    for position, id_receiver in enumerate(id_col):
        if id_receiver >= 0:
            out[map_p_id_to_position[id_receiver]] += column[position]

    return out


def fail_if_dtype_not_numeric(column, agg_func):
    if not numpy.issubdtype(column.dtype, numpy.number):
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. Allowed are only numerical dtypes."
        )


def fail_if_dtype_not_float(column, agg_func):
    if not numpy.issubdtype(column.dtype, numpy.floating):
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. Allowed is only float."
        )


def fail_if_dtype_not_int(id_col, agg_func):
    if not numpy.issubdtype(id_col.dtype, numpy.integer):
        raise TypeError(
            f"The dtype of group_id must be integer. Grouped_{agg_func} was applied "
            f"to a group_id that has dtype {id_col.dtype}."
        )


def fail_if_dtype_not_numeric_or_boolean(column, agg_func):
    if not (numpy.issubdtype(column.dtype, numpy.number) or column.dtype == "bool"):
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. "
            "Allowed are only numerical or Boolean dtypes."
        )


def fail_if_dtype_not_numeric_or_datetime(column, agg_func):
    if not (
        numpy.issubdtype(column.dtype, numpy.number)
        or numpy.issubdtype(column.dtype, numpy.datetime64)
    ):
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. "
            "Allowed are only numerical or datetime dtypes."
        )


def fail_if_dtype_not_boolean_or_int(column, agg_func):
    if not (
        numpy.issubdtype(column.dtype, numpy.integer)
        or numpy.issubdtype(column.dtype, numpy.bool_)
    ):
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. Allowed are only Boolean and int dtypes."
        )
