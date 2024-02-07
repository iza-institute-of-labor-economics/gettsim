from _gettsim.aggregation_jax import grouped_all as grouped_all_jax
from _gettsim.aggregation_jax import grouped_any as grouped_any_jax
from _gettsim.aggregation_jax import grouped_count as grouped_count_jax
from _gettsim.aggregation_jax import grouped_max as grouped_max_jax
from _gettsim.aggregation_jax import grouped_mean as grouped_mean_jax
from _gettsim.aggregation_jax import grouped_min as grouped_min_jax
from _gettsim.aggregation_jax import grouped_sum as grouped_sum_jax
from _gettsim.aggregation_jax import sum_values_by_index as sum_values_by_index_jax
from _gettsim.aggregation_numpy import grouped_all as grouped_all_numpy
from _gettsim.aggregation_numpy import grouped_any as grouped_any_numpy
from _gettsim.aggregation_numpy import grouped_count as grouped_count_numpy
from _gettsim.aggregation_numpy import grouped_cumsum as grouped_cumsum_numpy
from _gettsim.aggregation_numpy import grouped_max as grouped_max_numpy
from _gettsim.aggregation_numpy import grouped_mean as grouped_mean_numpy
from _gettsim.aggregation_numpy import grouped_min as grouped_min_numpy
from _gettsim.aggregation_numpy import grouped_sum as grouped_sum_numpy
from _gettsim.aggregation_numpy import sum_values_by_index as sum_values_by_index_numpy
from _gettsim.config import USE_JAX


def grouped_count(group_id):
    if USE_JAX:
        return grouped_count_jax(group_id)
    else:
        return grouped_count_numpy(group_id)


def grouped_sum(column, group_id):
    if USE_JAX:
        return grouped_sum_jax(column, group_id)
    else:
        return grouped_sum_numpy(column, group_id)


def grouped_mean(column, group_id):
    if USE_JAX:
        return grouped_mean_jax(column, group_id)
    else:
        return grouped_mean_numpy(column, group_id)


def grouped_max(column, group_id):
    if USE_JAX:
        return grouped_max_jax(column, group_id)
    else:
        return grouped_max_numpy(column, group_id)


def grouped_min(column, group_id):
    if USE_JAX:
        return grouped_min_jax(column, group_id)
    else:
        return grouped_min_numpy(column, group_id)


def grouped_any(column, group_id):
    if USE_JAX:
        return grouped_any_jax(column, group_id)
    else:
        return grouped_any_numpy(column, group_id)


def grouped_all(column, group_id):
    if USE_JAX:
        return grouped_all_jax(column, group_id)
    else:
        return grouped_all_numpy(column, group_id)


def grouped_cumsum(column, group_id):
    # Not yet implemented for jax
    return grouped_cumsum_numpy(column, group_id)


def sum_values_by_index(column, id_col, p_id_col):
    if USE_JAX:
        return sum_values_by_index_jax(column, id_col, p_id_col)
    else:
        return sum_values_by_index_numpy(column, id_col, p_id_col)
