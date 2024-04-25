from _gettsim.aggregation_jax import all_by_p_id as all_by_p_id_jax
from _gettsim.aggregation_jax import any_by_p_id as any_by_p_id_jax
from _gettsim.aggregation_jax import count_by_p_id as count_by_p_id_jax
from _gettsim.aggregation_jax import grouped_all as grouped_all_jax
from _gettsim.aggregation_jax import grouped_any as grouped_any_jax
from _gettsim.aggregation_jax import grouped_count as grouped_count_jax
from _gettsim.aggregation_jax import grouped_max as grouped_max_jax
from _gettsim.aggregation_jax import grouped_mean as grouped_mean_jax
from _gettsim.aggregation_jax import grouped_min as grouped_min_jax
from _gettsim.aggregation_jax import grouped_sum as grouped_sum_jax
from _gettsim.aggregation_jax import max_by_p_id as max_by_p_id_jax
from _gettsim.aggregation_jax import mean_by_p_id as mean_by_p_id_jax
from _gettsim.aggregation_jax import min_by_p_id as min_by_p_id_jax
from _gettsim.aggregation_jax import sum_by_p_id as sum_by_p_id_jax
from _gettsim.aggregation_numpy import all_by_p_id as all_by_p_id_numpy
from _gettsim.aggregation_numpy import any_by_p_id as any_by_p_id_numpy
from _gettsim.aggregation_numpy import count_by_p_id as count_by_p_id_numpy
from _gettsim.aggregation_numpy import grouped_all as grouped_all_numpy
from _gettsim.aggregation_numpy import grouped_any as grouped_any_numpy
from _gettsim.aggregation_numpy import grouped_count as grouped_count_numpy
from _gettsim.aggregation_numpy import grouped_max as grouped_max_numpy
from _gettsim.aggregation_numpy import grouped_mean as grouped_mean_numpy
from _gettsim.aggregation_numpy import grouped_min as grouped_min_numpy
from _gettsim.aggregation_numpy import grouped_sum as grouped_sum_numpy
from _gettsim.aggregation_numpy import max_by_p_id as max_by_p_id_numpy
from _gettsim.aggregation_numpy import mean_by_p_id as mean_by_p_id_numpy
from _gettsim.aggregation_numpy import min_by_p_id as min_by_p_id_numpy
from _gettsim.aggregation_numpy import sum_by_p_id as sum_by_p_id_numpy
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


def count_by_p_id(p_id_to_aggregate_by, p_id_to_store_by):
    if USE_JAX:
        return count_by_p_id_jax(p_id_to_aggregate_by, p_id_to_store_by)
    else:
        return count_by_p_id_numpy(p_id_to_aggregate_by, p_id_to_store_by)


def sum_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    if USE_JAX:
        return sum_by_p_id_jax(column, p_id_to_aggregate_by, p_id_to_store_by)
    else:
        return sum_by_p_id_numpy(column, p_id_to_aggregate_by, p_id_to_store_by)


def mean_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    if USE_JAX:
        return mean_by_p_id_jax(column, p_id_to_aggregate_by, p_id_to_store_by)
    else:
        return mean_by_p_id_numpy(column, p_id_to_aggregate_by, p_id_to_store_by)


def max_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    if USE_JAX:
        return max_by_p_id_jax(column, p_id_to_aggregate_by, p_id_to_store_by)
    else:
        return max_by_p_id_numpy(column, p_id_to_aggregate_by, p_id_to_store_by)


def min_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    if USE_JAX:
        return min_by_p_id_jax(column, p_id_to_aggregate_by, p_id_to_store_by)
    else:
        return min_by_p_id_numpy(column, p_id_to_aggregate_by, p_id_to_store_by)


def any_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    if USE_JAX:
        return any_by_p_id_jax(column, p_id_to_aggregate_by, p_id_to_store_by)
    else:
        return any_by_p_id_numpy(column, p_id_to_aggregate_by, p_id_to_store_by)


def all_by_p_id(column, p_id_to_aggregate_by, p_id_to_store_by):
    if USE_JAX:
        return all_by_p_id_jax(column, p_id_to_aggregate_by, p_id_to_store_by)
    else:
        return all_by_p_id_numpy(column, p_id_to_aggregate_by, p_id_to_store_by)
