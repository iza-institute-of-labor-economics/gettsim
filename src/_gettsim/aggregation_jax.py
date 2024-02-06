from _gettsim.aggregation_numpy import (
    fail_if_dtype_not_boolean_or_int,
    fail_if_dtype_not_float,
    fail_if_dtype_not_numeric_or_boolean,
    fail_if_dtype_not_numeric_or_datetime,
    fail_if_dtype_of_group_id_not_int,
)

try:
    import jax.numpy as jnp
    from jax.ops import segment_max, segment_min, segment_sum
except ImportError:
    pass


def grouped_count(group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="count")
    out_on_hh = segment_sum(jnp.ones(len(group_id)), group_id)
    out = out_on_hh[group_id]
    return out


def grouped_sum(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="sum")
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="sum")
    if column.dtype in ["bool", "int"]:
        column = column.astype(float)

    out_on_hh = segment_sum(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_mean(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="mean")
    fail_if_dtype_not_float(column, agg_func="mean")
    sum_on_hh = segment_sum(column, group_id)
    sizes = segment_sum(jnp.ones(len(column)), group_id)
    mean_on_hh = sum_on_hh / sizes
    out = mean_on_hh[group_id]
    return out


def grouped_max(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="max")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="max")

    out_on_hh = segment_max(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_min(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="min")
    fail_if_dtype_not_numeric_or_datetime(column, agg_func="min")
    out_on_hh = segment_min(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_any(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="any")
    fail_if_dtype_not_boolean_or_int(column, agg_func="any")

    # Convert to boolean if necessary
    if jnp.issubdtype(column.dtype, jnp.integer):
        my_col = column.astype("bool")
    else:
        my_col = column

    out_on_hh = segment_max(my_col, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_all(column, group_id):
    fail_if_dtype_of_group_id_not_int(group_id, agg_func="all")
    fail_if_dtype_not_boolean_or_int(column, agg_func="all")

    # Convert to boolean if necessary
    if jnp.issubdtype(column.dtype, jnp.integer):
        column = column.astype("bool")

    out_on_hh = segment_min(column, group_id)
    out = out_on_hh[group_id]
    return out


def sum_values_by_index(
    column: jnp.ndarray,
    id_col: jnp.ndarray[jnp.int64],
    p_id_col: jnp.ndarray[jnp.int64],
) -> jnp.ndarray:
    fail_if_dtype_not_numeric_or_boolean(column, agg_func="sum_values_by_index")
    if column.dtype in ["bool"]:
        column = column.astype(jnp.int64)
    else:
        column = column.astype(jnp.float64)
    out = jnp.zeros_like(p_id_col, dtype=column.dtype)

    map_p_id_to_position = {p_id: position for position, p_id in enumerate(p_id_col)}

    for position, id_receiver in enumerate(id_col):
        if id_receiver >= 0:
            out = out.at[map_p_id_to_position[id_receiver]].add(column[position])
    return out
