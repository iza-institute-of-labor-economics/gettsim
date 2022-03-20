import numpy as np
import numpy_groupies as npg


def grouped_count(group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="count")
    out_on_hh = npg.aggregate(
        group_id, np.ones(len(group_id)), func="sum", fill_value=0
    )

    out = out_on_hh[group_id]
    return out


def grouped_sum(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="sum")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="sum")

    out_on_hh = npg.aggregate(group_id, column, func="sum", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_mean(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="mean")
    fail_if_dtype_not_numeric(column, agg_func="mean")

    out_on_hh = npg.aggregate(group_id, column, func="mean", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_max(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="max")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="max")
    fill_value = (
        np.datetime64("2020") if np.issubdtype(column.dtype, np.datetime64) else 0
    )
    out_on_hh = npg.aggregate(group_id, column, func="max", fill_value=fill_value)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_min(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="min")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="min")
    fill_value = (
        np.datetime64("2020") if np.issubdtype(column.dtype, np.datetime64) else 0
    )
    out_on_hh = npg.aggregate(group_id, column, func="min", fill_value=fill_value)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_any(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="any")
    fail_if_dtype_not_boolean_or_int(column, agg_func="any")

    out_on_hh = npg.aggregate(group_id, column, func="any", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def grouped_all(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="all")
    fail_if_dtype_not_boolean_or_int(column, agg_func="all")

    out_on_hh = npg.aggregate(group_id, column, func="all", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def fail_if_dtype_not_numeric(column, agg_func):
    if not np.issubdtype(column.dtype, np.number):
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. Allowed are only numerical dtypes."
        )


def fail_if_dtype_of_group_id_not_int(group_id, agg_func):
    if group_id.dtype != "int":
        raise TypeError(
            f"The dtype of group_id must be integer. Grouped_{agg_func} was applied "
            f"to a group_id that has dtype {group_id.dtype}."
        )


def fail_if_dtype_not_numeric_or_boolean(column, agg_func):
    if not (np.issubdtype(column.dtype, np.number) or column.dtype == "bool"):
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. "
            "Allowed are only numerical or boolean dtypes."
        )


def fail_if_dtype_not_numeric_or_datetime(column, agg_func):
    if not (
        np.issubdtype(column.dtype, np.number)
        or np.issubdtype(column.dtype, np.datetime64)
    ):
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. "
            "Allowed are only numerical or datetime dtypes."
        )


def fail_if_dtype_not_boolean_or_int(column, agg_func):
    if column.dtype not in ["bool", "int"]:
        raise TypeError(
            f"grouped_{agg_func} was applied to a column "
            f"that has dtype {column.dtype}. Allowed is only boolean dtype."
        )
