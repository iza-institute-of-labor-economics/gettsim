"""Generic functions that are often used for the calculation of taxes and transfers.

"""
import numpy as np


def fill_intercepts_at_lower_thresholds(
    lower_thresholds, upper_thresholds, rates, intercept_at_lowest_threshold, fun
):
    """Return an array with intercepts at the lower thresholds so that the
    piecewise *fun* is smooth.

    Args:
        lower_thresholds (1-d float): The lower thresholds defining the intervals
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
    for i, up_thr in enumerate(lower_thresholds):
        intercepts_at_lower_thresholds[i] = fun(
            up_thr,
            lower_thresholds,
            upper_thresholds,
            rates,
            intercepts_at_lower_thresholds,
            side="left",
        )
    return intercepts_at_lower_thresholds


def get_dict_of_arrays_piecewise_linear(list_of_dicts):
    """Extracts parameters from a YAML-File and returns them as Python-dictionary.

        Args:
            list_of_dicts: list_of_dicts specifying upper_thresholds and
                  respective rates for a given legislature time.

        Returns:
            dict of 4 arrays for calc_e_anr_frei: lower_thresholds,
                upper_thresholds, rates and
                intercepts_at_lower_thresholds.
        """
    keys = sorted(key for key in list_of_dicts.keys() if type(key) == int)
    # Check if keys are consecutive numbers and starting at 0.
    if keys[0] != 0:
        raise ValueError(
            "The keys of the passed list of dictionaries do not start with 0."
        )
    for n in keys:
        if n == len(keys) - 1:
            break
        if keys[n] != keys[n + 1] - 1:
            raise ValueError(
                "The keys of the passed list of dictionaries are not consecutive numbers."
            )

    # Extract lower thresholds.
    lower_thresholds = np.zeros(len(keys))

    # Check if lowest threshold exists.
    if list_of_dicts[0]["lower_threshold"] is None:
        raise ValueError(
            "The first dictionary of the passed list needs to contain a lower_threshold value."
        )

    for interval in keys:
        if "lower_threshold" in list_of_dicts[interval]:
            lower_thresholds[interval] = list_of_dicts[interval]["lower_threshold"]
        elif "upper_threshold" in list_of_dicts[interval - 1]:
            lower_thresholds[interval] = list_of_dicts[interval - 1]["upper_threshold"]
        else:
            raise ValueError(
                f"Current Key: {interval}. Either this dictionary needs to "
                f"contain a lower_thresholds value or the previous dictionary "
                f"needs to contain an upper_threshold value."
            )

    # Create and fill upper_thresholds-Array
    upper_thresholds = np.zeros(len(keys))
    for interval in keys:
        if "upper_threshold" in list_of_dicts[interval]:
            upper_thresholds[interval] = list_of_dicts[interval]["upper_threshold"]
        elif "lower_threshold" in list_of_dicts[interval + 1]:
            upper_thresholds[interval] = list_of_dicts[interval + 1]["lower_threshold"]
        else:
            raise ValueError(
                f"Current Key: {interval}. Either this dictionary needs to "
                f"contain an upper_threshold value or the next dictionary "
                f"needs to contain a lower_threshold value."
            )

    # Create and fill rates-Array
    rates = np.zeros(len(keys))
    for interval in keys:
        if "rate" in list_of_dicts[interval]:
            rates[interval] = list_of_dicts[interval]["rate"]
        else:
            raise ValueError(
                f"Current Key: {interval}. The current dictionary has no rate specified."
            )

    # Create and fill intercepts-Array
    intercepts = fill_intercepts_at_lower_thresholds(
        lower_thresholds, upper_thresholds, rates, 0, piecewise_linear
    )

    # Check if created intercepts-Array has the same size as the other three.
    if len(lower_thresholds) != len(intercepts):
        raise ValueError(
            "The generated intercepts array doesn't have "
            "the same length as the other arrays."
        )

    out = {
        "lower_thresholds": lower_thresholds,
        "upper_thresholds": upper_thresholds,
        "rates": rates,
        "intercepts": intercepts,
    }

    return out


def piecewise_linear(
    value,
    lower_thresholds,
    upper_thresholds,
    rates,
    intercepts_at_lower_thresholds,
    side,
):
    """Return a fraction of *value* defined by a piecewise linear function.

    Args:
        value (float, >0): The value that the function is applied to.
        lower_thresholds (1-d float): The lower thresholds defining the intervals
        upper_thresholds (1-d float): The upper thresholds defining the intervals
        rates (1-d float): The slope in the interval below the corresponding element
            of *upper_thresholds*
        intercepts_at_lower_thresholds (1-d float):
        side: Parameter is passed to the searchsorted-function.

    The lowest threshold is implicit as 0.

    All 4 arrays must the same length and sorted by upper_thresholds. None of this
    is checked here.

    Todo: This should be checked upon creation of the arrays!

    """
    if (value < lower_thresholds[0]) or (value > upper_thresholds[-1]):
        out = np.nan
    else:
        idx = np.searchsorted(upper_thresholds, value, side=side)
        intcpt = intercepts_at_lower_thresholds[idx]
        out = intcpt + (value - lower_thresholds[idx]) * rates[idx]
    return out
