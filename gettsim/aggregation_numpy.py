import numpy as np
import numpy_groupies as npg


def mean_on_group_level(column, group_id):
    fail_if_dtype_not_numerical(column, agg_func="mean")

    out_on_hh = npg.aggregate(group_id, column, func="mean", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def max_on_group_level(column, group_id):
    fail_if_dtype_not_numerical(column, agg_func="max")

    out_on_hh = npg.aggregate(group_id, column, func="max", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def any_on_group_level(column, group_id):
    fail_if_dtype_not_boolean(column, agg_func="any")

    out_on_hh = npg.aggregate(group_id, column, func="any", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def fail_if_dtype_not_numerical(column, agg_func):
    if not np.issubdtype(column.dtype, np.number):
        raise ValueError(
            f"{agg_func}_on_group_level was applied to a column "
            f"that has dtype {column.dtype}. Allowed are only numerical dtypes."
        )


def fail_if_dtype_not_boolean(column, agg_func):
    if column.dtype != "bool":
        raise ValueError(
            f"{agg_func}_on_group_level was applied to a column "
            f"that has dtype {column.dtype}. Allowed is only boolean dtype."
        )
