from gettsim.aggregation_numpy import fail_if_dtype_not_boolean
from gettsim.aggregation_numpy import fail_if_dtype_not_numeric

try:
    import jax.numpy as jnp
    from jax.ops import segment_max
    from jax.ops import segment_min
    from jax.ops import segment_sum
except ImportError:
    pass


def grouped_sum(column, group_id):
    fail_if_dtype_not_numeric(column, agg_func="sum")
    out_on_hh = segment_sum(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_mean(column, group_id):
    fail_if_dtype_not_numeric(column, agg_func="mean")
    sum_on_hh = segment_sum(column, group_id)
    sizes = segment_sum(jnp.ones(len(column)), group_id)
    mean_on_hh = sum_on_hh / sizes
    out = mean_on_hh[group_id]
    return out


def grouped_max(column, group_id):
    fail_if_dtype_not_numeric(column, agg_func="max")
    out_on_hh = segment_max(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_min(column, group_id):
    fail_if_dtype_not_numeric(column, agg_func="min")
    out_on_hh = segment_min(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_any(column, group_id):
    fail_if_dtype_not_boolean(column, agg_func="any")
    out_on_hh = segment_max(column, group_id)
    out = out_on_hh[group_id]
    return out


def grouped_all(column, group_id):
    fail_if_dtype_not_boolean(column, agg_func="all")
    out_on_hh = segment_min(column, group_id)
    out = out_on_hh[group_id]
    return out
