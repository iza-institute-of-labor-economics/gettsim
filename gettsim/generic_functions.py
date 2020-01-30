"""Generic functions that are often used for the calculation o taxes and transfers.

"""
import numpy as np


def fill_intercepts_at_lower_thresholds(
    upper_thresholds, rates, intercept_at_lowest_threshold, fun
):
    """Return an array with intercepts at the lower thresholds so that the
    piecewise *fun* is smooth.

    Args:

        upper_thresholds (1-d float): The upper thresholds defining the intervals
        rates (1-d float): The slope in the interval below the corresponding element
            of *upper_thresholds*
        intercept_at_lowest_threshold (float):
        fun: function handle (currently only piecewise_linear, will need to think about
            whether we can have a generic function with a different interface or make
            it specific )

    The lowest threshold is implicit as 0.

    """

    intercepts_at_lower_thresholds = np.zeros(upper_thresholds.shape) * np.nan
    intercepts_at_lower_thresholds[0] = intercept_at_lowest_threshold
    for i, up_thr in enumerate(upper_thresholds[1:]):
        intercepts_at_lower_thresholds[i] = fun(
            up_thr, upper_thresholds, intercepts_at_lower_thresholds, "left"
        )

    return intercepts_at_lower_thresholds


def piecewise_linear(
    value, upper_thresholds, rates, intercepts_at_lower_thresholds, side
):
    """Return a fraction of *value* defined by a piecewise linear function.

    Args:
        value (float, >0): The value that the function is applied to.
        upper_thresholds (1-d float): The upper thresholds defining the intervals
        rates (1-d float): The slope in the interval below the corresponding element
            of *upper_thresholds*
        intercepts_at_lower_thresholds (1-d float):

    The lowest threshold is implicit as 0.

    All three arrays must the same length and sorted by upper_thresholds. None of this
    is checked here.

    Todo: This should be checked upon creation of the arrays!

    """

    idx = np.searchsorted(upper_thresholds, value, side=side)
    intcpt = intercepts_at_lower_thresholds[idx]
    out = intcpt + (value - intcpt) * rates[idx]

    return out
