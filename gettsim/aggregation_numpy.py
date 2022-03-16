import numpy as np
import numpy_groupies as npg


def grouped_sum(column, group_id):
    fail_if_dtype_not_numeric(column, agg_func="sum")

    out_on_hh = npg.aggregate(group_id, column, func="sum", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_mean(column, group_id):
    fail_if_dtype_not_numeric(column, agg_func="mean")

    out_on_hh = npg.aggregate(group_id, column, func="mean", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_max(column, group_id):
    fail_if_dtype_not_numeric(column, agg_func="max")

    out_on_hh = npg.aggregate(group_id, column, func="max", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_min(column, group_id):
    fail_if_dtype_not_numeric(column, agg_func="min")

    out_on_hh = npg.aggregate(group_id, column, func="min", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_any(column, group_id):
    fail_if_dtype_not_boolean(column, agg_func="any")

    out_on_hh = npg.aggregate(group_id, column, func="any", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_all(column, group_id):
    fail_if_dtype_not_boolean(column, agg_func="all")

    out_on_hh = npg.aggregate(group_id, column, func="all", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def fail_if_dtype_not_numeric(column, agg_func):
    if not np.issubdtype(column.dtype, np.number):
        raise ValueError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. Allowed are only numerical dtypes."
        )


def fail_if_dtype_not_boolean(column, agg_func):
    if column.dtype != "bool":
        raise ValueError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. Allowed is only boolean dtype."
        )
