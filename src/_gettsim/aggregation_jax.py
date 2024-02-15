from _gettsim.aggregation_numpy import (
    fail_if_dtype_not_boolean_or_int,
    fail_if_dtype_not_float,
    fail_if_dtype_not_int,
    fail_if_dtype_not_numeric_or_boolean,
    fail_if_dtype_not_numeric_or_datetime,
)

try:
    import jax.numpy as jnp
    from jax.ops import segment_max, segment_min, segment_sum
except ImportError:
    pass


def grouped_count(group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_count")
    out_on_hh = segment_sum(jnp.ones(len(group_id)), group_id)
    out = out_on_hh[group_id]
    return out


def grouped_sum(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_sum")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="grouped_sum")
    if column.dtype in ["bool"]:
        column = column.astype(int)

    out_on_hh = segment_sum(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_mean(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_mean")
    fail_if_dtype_not_float(column, agg_func="grouped_mean")
    sum_on_hh = segment_sum(column, group_id)
    sizes = segment_sum(jnp.ones(len(column)), group_id)
    mean_on_hh = sum_on_hh / sizes
    out = mean_on_hh[group_id]
    return out


def grouped_max(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_max")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="grouped_max")

    out_on_hh = segment_max(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_min(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_min")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="grouped_min")
    out_on_hh = segment_min(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_any(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_any")
    fail_if_dtype_not_boolean_or_int(column, agg_func="grouped_any")

    # Convert to boolean if necessary
    if jnp.issubdtype(column.dtype, jnp.integer):
        my_col = column.astype("bool")
    else:
        my_col = column

    out_on_hh = segment_max(my_col, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_all(column, group_id):
    fail_if_dtype_not_int(group_id, agg_func="grouped_all")
    fail_if_dtype_not_boolean_or_int(column, agg_func="grouped_all")

    # Convert to boolean if necessary
    if jnp.issubdtype(column.dtype, jnp.integer):
        column = column.astype("bool")

    out_on_hh = segment_min(column, group_id)
    out = out_on_hh[group_id]
    return out


def count_by_p_id(id_col, p_id_col):
    fail_if_dtype_not_int(id_col, agg_func="count_by_p_id")
    fail_if_dtype_not_int(p_id_col, agg_func="count_by_p_id")

    raise NotImplementedError


def sum_by_p_id(column, id_col, p_id_col):
    fail_if_dtype_not_int(id_col, agg_func="sum_by_p_id")
    fail_if_dtype_not_int(p_id_col, agg_func="sum_by_p_id")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="sum_by_p_id")

    if column.dtype in ["bool"]:
        column = column.astype(int)
    out = jnp.zeros_like(p_id_col, dtype=column.dtype)

    map_p_id_to_position = {p_id: iloc for iloc, p_id in enumerate(p_id_col)}

    for iloc, id_receiver in enumerate(id_col):
        if id_receiver >= 0:
            out = out.at[map_p_id_to_position[id_receiver]].add(column[iloc])
    return out


def mean_by_p_id(column, id_col, p_id_col):
    fail_if_dtype_not_int(id_col, agg_func="mean_by_p_id")
    fail_if_dtype_not_int(p_id_col, agg_func="mean_by_p_id")
    fail_if_dtype_not_float(column, agg_func="mean_by_p_id")
    raise NotImplementedError


def max_by_p_id(column, id_col, p_id_col):
    fail_if_dtype_not_int(id_col, agg_func="max_by_p_id")
    fail_if_dtype_not_int(p_id_col, agg_func="max_by_p_id")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="max_by_p_id")
    raise NotImplementedError


def min_by_p_id(column, id_col, p_id_col):
    fail_if_dtype_not_int(id_col, agg_func="min_by_p_id")
    fail_if_dtype_not_int(p_id_col, agg_func="min_by_p_id")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="min_by_p_id")
    raise NotImplementedError


def any_by_p_id(column, id_col, p_id_col):
    fail_if_dtype_not_int(id_col, agg_func="any_by_p_id")
    fail_if_dtype_not_int(p_id_col, agg_func="any_by_p_id")
    fail_if_dtype_not_boolean_or_int(column, agg_func="any_by_p_id")
    raise NotImplementedError


def all_by_p_id(column, id_col, p_id_col):
    fail_if_dtype_not_int(p_id_col, agg_func="all_by_p_id")
    fail_if_dtype_not_int(id_col, agg_func="all_by_p_id")
    fail_if_dtype_not_boolean_or_int(column, agg_func="all_by_p_id")
    raise NotImplementedError
