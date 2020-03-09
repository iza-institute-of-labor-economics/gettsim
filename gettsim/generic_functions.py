"""Generic functions that are often used for the calculation of taxes and transfers.


"""
import numpy as np


def fill_intercepts_at_lower_thresholds(
    lower_thresholds, upper_thresholds, rates, intercept_at_lowest_threshold, fun
):
    """Return an array with intercepts at the lower thresholds, i.e. the output
    piecewise_linear calculates for each threshold as input value respectively.

    Args:
        lower_thresholds (1-d float): The lower thresholds defining the intervals
        upper_thresholds (1-d float): The upper thresholds defining the intervals
        rates (1-d float): The slope in the interval below the corresponding element
            of *upper_thresholds*
        intercept_at_lowest_threshold (float): intecept at the lowest threshold
        fun: function handle (currently only piecewise_linear, will need to think about
            whether we can have a generic function with a different interface or make
            it specific )


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


def get_dict_of_arrays_piecewise_linear(parameter_dict):
    """Extract parameters from a YAML-File that define the piecewise_linear function
    and return them as Python-dictionary.

        Args:
            parameter_dict: dictionary specifying the intervals and parameters
                            for a given legislature time. Keys are the ennumerated
                            intervals of the function starting with 0. Values are
                            dictionaries specifying lower_threshold, upper_threshold
                            (each threshold must be defined by at least one
                            of them) and rate of the respective interval. Either only
                            the first interval intercept_at_lower_threshold or all of
                            them need to be given.


        Returns:
            dictionary of 4 arrays as input for piecewise_linear:
                lower_thresholds,
                upper_thresholds,
                rates and
                intercepts_at_lower_thresholds.


        """
    keys = sorted(key for key in parameter_dict.keys() if type(key) == int)
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
    if "lower_threshold" not in parameter_dict[0]:
        raise ValueError(
            "The first dictionary of the passed list needs to contain a lower_threshold value."
        )

    for interval in keys:
        if "lower_threshold" in parameter_dict[interval]:
            lower_thresholds[interval] = parameter_dict[interval]["lower_threshold"]
        elif "upper_threshold" in parameter_dict[interval - 1]:
            lower_thresholds[interval] = parameter_dict[interval - 1]["upper_threshold"]
        else:
            raise ValueError(
                f"Current Key: {interval}. Either this dictionary needs to "
                f"contain a lower_thresholds value or the previous dictionary "
                f"needs to contain an upper_threshold value."
            )

    # Create and fill upper_thresholds-Array
    upper_thresholds = np.zeros(len(keys))

    # Check if highest upper_threshold exists.
    if "upper_threshold" not in parameter_dict[keys[-1]]:
        raise ValueError(
            "The last dictionary needs to contain a upper_threshold value."
        )

    for interval in keys:
        if "upper_threshold" in parameter_dict[interval]:
            upper_thresholds[interval] = parameter_dict[interval]["upper_threshold"]
        elif "lower_threshold" in parameter_dict[interval + 1]:
            upper_thresholds[interval] = parameter_dict[interval + 1]["lower_threshold"]
        else:
            raise ValueError(
                f"Current Key: {interval}. Either this dictionary needs to "
                f"contain an upper_threshold value or the next dictionary "
                f"needs to contain a lower_threshold value."
            )

    # Create and fill rates-Array
    rates = np.zeros(len(keys))
    for interval in keys:
        if "rate" in parameter_dict[interval]:
            rates[interval] = parameter_dict[interval]["rate"]
        else:
            raise ValueError(
                f"Current Key: {interval}. The current dictionary has no rate specified."
            )

    # Create and fill intercepts-Array
    intercepts = np.zeros(len(keys))
    all_intercepts_supplied = True

    if "intercept_at_lower_threshold" not in parameter_dict[0]:
        raise ValueError(
            "The first dictionary needs an intercept, because either "
            "the lowest intercept or all intercepts must be passed."
        )

    # Check if all intercepts are supplied.
    for interval in keys:
        if "intercept_at_lower_threshold" not in parameter_dict[interval]:
            all_intercepts_supplied = False

    # If all intercepts are supplied, take the supplied ones.
    if all_intercepts_supplied:
        for interval in keys:
            intercepts[interval] = parameter_dict[interval][
                "intercept_at_lower_threshold"
            ]
    else:
        for interval in keys:
            if (
                interval != 0
                and "intercept_at_lower_threshold" in parameter_dict[interval]
            ):
                raise ValueError(
                    "More than one, but not all intercepts are supplied. "
                    "The dictionaries should contain either only the lowest intercept "
                    "or all intercepts."
                )

    # If only the first intercept is supplied, use fill_intercepts_at_lower_thresholds
    # to fill the missing ones.
    if not all_intercepts_supplied:
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
        intercepts_at_lower_thresholds (1-d float): the fraction piecewise_linear
            calculates at the respective thresholds
        side: Parameter is passed to the searchsorted-function.


    """
    if (value < lower_thresholds[0]) or (value > upper_thresholds[-1]):
        out = np.nan
    else:
        idx = np.searchsorted(upper_thresholds, value, side=side)
        intcpt = intercepts_at_lower_thresholds[idx]
        out = intcpt + (value - lower_thresholds[idx]) * rates[idx]
    return out
