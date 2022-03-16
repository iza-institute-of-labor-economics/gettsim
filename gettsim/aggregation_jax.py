import jax.numpy as jnp
import numpy as np
from jax.ops import segment_max
from jax.ops import segment_sum


def sum_on_group_level(column, group_id):
    fail_if_dtype_not_numerical(column, agg_func="sum")
    out_on_hh = segment_sum(column, group_id)
    out = out_on_hh[group_id]
    return out


def mean_on_group_level(column, group_id):
    fail_if_dtype_not_numerical(column, agg_func="mean")
    sum_on_hh = segment_sum(column, group_id)
    sizes = segment_sum(jnp.ones(len(column)), group_id)
    mean_on_hh = sum_on_hh / sizes
    out = mean_on_hh[group_id]
    return out


def max_on_group_level(column, group_id):
    fail_if_dtype_not_numerical(column, agg_func="max")
    out_on_hh = segment_max(column, group_id)
    out = out_on_hh[group_id]
    return out


def any_on_group_level(column, group_id):
    fail_if_dtype_not_boolean(column, agg_func="any")
    out_on_hh = segment_max(column, group_id)
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
