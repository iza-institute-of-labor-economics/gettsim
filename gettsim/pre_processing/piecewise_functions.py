import copy

import numpy as np

from gettsim.pre_processing.generic_functions import check_threholds


def piecewise_polynominal(
    value,
    lower_thresholds,
    upper_thresholds,
    rates,
    intercepts_at_lower_thresholds,
    rates_modified=False,
):
    """Return a fraction of *value* defined by a piecewise linear function.

    Args:
        value (float, >0): The value that the function is applied to.
        lower_thresholds (1-d float): The lower thresholds defining the intervals
        upper_thresholds (1-d float): The upper thresholds defining the intervals
        rates (1-d float): The slope in the interval below the corresponding element
            of *upper_thresholds*
        intercepts_at_lower_thresholds (1-d float): the fraction piecewise_linear
            calculates at the respective thresholds
        rates_modified: Boolean variable indicating, that intercepts can't be used
        anymore.


    """

    # Check if value lies within the defined range.
    if (value < lower_thresholds[0]) or (value > upper_thresholds[-1]):
        return np.nan

    index_interval = np.searchsorted(upper_thresholds, value, side="left")
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
    increment_to_calc = value - lower_thresehold_interval

    out = intercept_interval
    for pol in range(1, rates.shape[0] + 1):
        out += rates[pol - 1, index_interval] * (increment_to_calc ** pol)
    return out


def add_progressionsfaktor(param_dict, parameter):
    """
    If no quadratic rate is given, add rate according to the
    progressionsfaktor formula.
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
