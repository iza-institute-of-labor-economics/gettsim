import copy

import numpy as np

from gettsim.pre_processing.generic_functions import check_threholds


def piecewise_polynomial(
    x,
    lower_thresholds,
    upper_thresholds,
    rates,
    intercepts_at_lower_thresholds,
    rates_modified=False,
):
    """Calculate value of the piecewise function at x. The function is defined by the
    other input arrays.

    Args:
        x (float, >0): The value that the function is applied to.
        lower_thresholds (1-d array): The lower thresholds of each interval.
        upper_thresholds (1-d array): The upper thresholds each interval.
        rates (n-d arry): The slope in each interval. Where n is the degree of the
        polynomial function.
        intercepts_at_lower_thresholds (1-d array): The intercepts at the lower
        threshold of each interval.
        rates_modified: Boolean variable indicating, that intercepts can't be used
        anymore.


    """

    # Check if value lies within the defined range.
    if (x < lower_thresholds[0]) or (x > upper_thresholds[-1]):
        return np.nan

    index_interval = np.searchsorted(upper_thresholds, x, side="left")
    if rates_modified:
        # Calculate new intercept
        intercept_interval = 0
        for interval in range(index_interval):
            for pol in range(1, rates.shape[0] + 1):
                intercept_interval += (rates[pol - 1, interval] ** pol) * (
                    upper_thresholds[interval] - lower_thresholds[interval]
                )

    else:
        intercept_interval = intercepts_at_lower_thresholds[index_interval]

    # Select threshold and calculate corresponding increment into interval
    lower_thresehold_interval = lower_thresholds[index_interval]
    increment_to_calc = x - lower_thresehold_interval

    out = intercept_interval
    for pol in range(1, rates.shape[0] + 1):
        out += rates[pol - 1, index_interval] * (increment_to_calc ** pol)
    return out


def add_progressionsfaktor(param_dict, parameter):
    """
    The german tax tarif is defined on several income intervals with distinct
    marginal tax rates at the thresholds. To ensure an almost linear increase of
    the average tax rate, the german tax tarif is defined as a quadratic function,
    where the quadratic rate is the so called linear Progressionsfaktor. For its
    calculation one needs the lower (low_thres) and upper (upper_thres) of the
    interval as well as the marginal tax rate of the interval (rate_iv) and of the
    following interval (rate_fiv). The formula is then given by:

    (rate_fiv - rate_iv) / (2 * (upper_thres - low_thres))

    """
    out_dict = copy.deepcopy(param_dict)
    interval_keys = sorted(key for key in out_dict.keys() if type(key) == int)
    # Check and extract lower thresholds.
    lower_thresholds, upper_thresholds = check_threholds(
        param_dict, parameter, interval_keys
    )
    for key in interval_keys:
        if "rate_quadratic" not in out_dict[key]:
            out_dict[key]["rate_quadratic"] = (
                out_dict[key + 1]["rate_linear"] - out_dict[key]["rate_linear"]
            ) / (2 * (upper_thresholds[key] - lower_thresholds[key]))
    return out_dict
