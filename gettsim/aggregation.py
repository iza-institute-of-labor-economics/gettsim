from gettsim.aggregation_jax import grouped_all as grouped_all_jax
from gettsim.aggregation_jax import grouped_any as grouped_any_jax
from gettsim.aggregation_jax import grouped_count as grouped_count_jax
from gettsim.aggregation_jax import grouped_max as grouped_max_jax
from gettsim.aggregation_jax import grouped_mean as grouped_mean_jax
from gettsim.aggregation_jax import grouped_min as grouped_min_jax
from gettsim.aggregation_jax import grouped_sum as grouped_sum_jax
from gettsim.aggregation_numpy import grouped_all as grouped_all_numpy
from gettsim.aggregation_numpy import grouped_any as grouped_any_numpy
from gettsim.aggregation_numpy import grouped_count as grouped_count_numpy
from gettsim.aggregation_numpy import grouped_max as grouped_max_numpy
from gettsim.aggregation_numpy import grouped_mean as grouped_mean_numpy
from gettsim.aggregation_numpy import grouped_min as grouped_min_numpy
from gettsim.aggregation_numpy import grouped_sum as grouped_sum_numpy
from gettsim.config import IS_JAX_INSTALLED


def grouped_count(column, group_id):
    if IS_JAX_INSTALLED:
        return grouped_count_jax(column, group_id)
    else:
        return grouped_count_numpy(column, group_id)


def grouped_sum(column, group_id):
    if IS_JAX_INSTALLED:
        return grouped_sum_jax(column, group_id)
    else:
        return grouped_sum_numpy(column, group_id)


def grouped_mean(column, group_id):
    if IS_JAX_INSTALLED:
        return grouped_mean_jax(column, group_id)
    else:
        return grouped_mean_numpy(column, group_id)


def grouped_max(column, group_id):
    if IS_JAX_INSTALLED:
        return grouped_max_jax(column, group_id)
    else:
        return grouped_max_numpy(column, group_id)


def grouped_min(column, group_id):
    if IS_JAX_INSTALLED:
        return grouped_min_jax(column, group_id)
    else:
        return grouped_min_numpy(column, group_id)


def grouped_any(column, group_id):
    if IS_JAX_INSTALLED:
        return grouped_any_jax(column, group_id)
    else:
        return grouped_any_numpy(column, group_id)


def grouped_all(column, group_id):
    if IS_JAX_INSTALLED:
        return grouped_all_jax(column, group_id)
    else:
        return grouped_all_numpy(column, group_id)
