"""Generic functions that are often used for the calculation of taxes and transfers.

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
    i = 1
    for i, up_thr in enumerate(np.append(0, upper_thresholds[0:-1])):
        intercepts_at_lower_thresholds[i] = fun(
            up_thr, upper_thresholds, rates, intercepts_at_lower_thresholds, side="left"
        )

    return intercepts_at_lower_thresholds


def get_dict_of_arrays_piecewise_linear(list_of_dicts):
    """Extract the relevant parameters for e_anr_frei.

        Args:
            list_of_dicts: list_of_dicts specifying upper_thresholds and
                  respective rates for a given legislature time.

        Returns:
            dict of 3 arrays for calc_e_anr_frei: upper_thresholds, rates and
            intercepts_at_lower_thresholds.
        """
    keys = sorted(key for key in list_of_dicts.keys() if type(key) == int)

    # Create and fill upper_thresholds-Array
    upper_thresholds = np.zeros(len(keys))
    for k in keys:
        upper_thresholds[k] = list_of_dicts[k]["upper_threshold"]

    # Create and fill rates-Array
    rates = np.zeros(len(keys))
    for k in keys:
        rates[k] = list_of_dicts[k]["rate"]

    # To-Do: Create and fill intercepts-Array
    # intercepts = fill_intercepts_at_lower_thresholds(
    #    upper_thresholds, rates, 0, piecewise_linear
    # )

    out = {
        "upper_thresholds": upper_thresholds,
        "rates": rates,
        # "intercepts": intercepts,
    }

    return out


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
    out = intcpt + (value - np.append(0, upper_thresholds)[idx]) * rates[idx]
    return out
