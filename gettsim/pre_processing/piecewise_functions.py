import numpy as np


def piecewise_linear(
    value, lower_thresholds, upper_thresholds, rates, intercepts_at_lower_thresholds,
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


    """
    if (value < lower_thresholds[0]) or (value > upper_thresholds[-1]):
        out = np.nan
    else:
        index_interval = np.searchsorted(upper_thresholds, value, side="left")
        intercept_interval = intercepts_at_lower_thresholds[index_interval]
        lower_thresehold_interval = lower_thresholds[index_interval]
        rate_interval = rates[index_interval]
        out = intercept_interval + (value - lower_thresehold_interval) * rate_interval
    return out
