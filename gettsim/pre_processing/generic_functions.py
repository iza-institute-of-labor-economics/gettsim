"""Generic functions that are often used for the calculation of taxes and transfers.


"""
import numpy as np


def get_piecewise_parameters(parameter_dict, parameter, piecewise_func, func_type):
    """Extract parameters from a yaml-File that define the piecewise_linear function
    and return them as dictionary."""

    keys = sorted(key for key in parameter_dict.keys() if type(key) == int)
    # Check if keys are consecutive numbers and starting at 0.

    if keys != list(range(len(keys))):
        raise ValueError(
            f"The keys of {parameter} do not start with 0 or are not consecutive"
            f" numbers."
        )

    # Extract lower thresholds.
    lower_thresholds, upper_thresholds = check_threholds(
        parameter_dict, parameter, keys
    )

    # Create and fill rates-array
    rates = check_rates(parameter_dict, parameter, keys, func_type)

    # Create and fill interecept-array
    intercepts = check_intercepts(
        parameter_dict,
        parameter,
        lower_thresholds,
        upper_thresholds,
        rates,
        keys,
        piecewise_func,
    )

    piecewise_elements = {
        "lower_thresholds": lower_thresholds,
        "upper_thresholds": upper_thresholds,
        "rates": rates,
        "intercepts_at_lower_thresholds": intercepts,
    }

    return piecewise_elements


def check_threholds(parameter_dict, parameter, keys):
    lower_thresholds = np.zeros(len(keys))
    upper_thresholds = np.zeros(len(keys))

    # Check if lowest threshold exists.
    if "lower_threshold" not in parameter_dict[0]:
        raise ValueError(
            f"The first piece of {parameter} needs to contain a lower_threshold value."
        )
    lower_thresholds[0] = parameter_dict[0]["lower_threshold"]

    # Check if highest upper_threshold exists.
    if "upper_threshold" not in parameter_dict[keys[-1]]:
        raise ValueError(
            f"The last piece of {parameter} needs to contain an upper_threshold value."
        )
    upper_thresholds[keys[-1]] = parameter_dict[keys[-1]]["upper_threshold"]

    for interval in keys[1:]:
        if "lower_threshold" in parameter_dict[interval]:
            lower_thresholds[interval] = parameter_dict[interval]["lower_threshold"]
        elif "upper_threshold" in parameter_dict[interval - 1]:
            lower_thresholds[interval] = parameter_dict[interval - 1]["upper_threshold"]
        else:
            raise ValueError(
                f"In {interval} of {parameter} is no lower upper threshold or an upper"
                f" in the piece before."
            )

    for interval in keys[:-1]:
        if "upper_threshold" in parameter_dict[interval]:
            upper_thresholds[interval] = parameter_dict[interval]["upper_threshold"]
        elif "lower_threshold" in parameter_dict[interval + 1]:
            upper_thresholds[interval] = parameter_dict[interval + 1]["lower_threshold"]
        else:
            raise ValueError(
                f"In {interval} of {parameter} is no upper threshold or a lower"
                f" threshold in the piece after."
            )
    return lower_thresholds, upper_thresholds


def check_rates(parameter_dict, parameter, keys, func_type):
    """
    Select rates depending on piecewise function type.
    """
    options_dict = {
        "quadratic": {
            "necessary_keys": ["rate_linear", "rate_quadratic"],
            "rates_size": 2,
        },
        "cubic": {
            "necessary_keys": ["rate_linear", "rate_quadratic", "rate_cubic"],
            "rates_size": 3,
        },
    }
    # Allow for specification of rate with "rate" and "rate_linear"
    if func_type == "linear":
        rates = np.zeros((1, len(keys)))
        for interval in keys:
            if "rate" in parameter_dict[interval]:
                rates[0, interval] = parameter_dict[interval]["rate"]
            elif "rate_linear" in parameter_dict[interval]:
                rates[0, interval] = parameter_dict[interval]["rate_linear"]
            else:
                raise ValueError(
                    f"In {interval} of {parameter} there is no rate specified."
                )
    elif func_type in options_dict:
        rates = np.zeros((options_dict[func_type]["rates_size"], len(keys)))
        for i, rate_type in enumerate(options_dict[func_type]["necessary_keys"]):
            for interval in keys:
                if rate_type in parameter_dict[interval]:
                    rates[i, interval] = parameter_dict[interval][rate_type]
                else:
                    raise ValueError(
                        f"In {interval} of {parameter} {rate_type} is missing."
                    )
    else:
        raise ValueError(f"Piecewise function {func_type} not specified.")
    return rates


def check_intercepts(
    parameter_dict, parameter, lower_thresholds, upper_thresholds, rates, keys, func
):
    intercepts = np.zeros(len(keys))
    count_intercepts_supplied = 1

    if "intercept_at_lower_threshold" not in parameter_dict[0]:
        raise ValueError(f"The first piece of {parameter} needs an intercept.")
    else:
        intercepts[0] = parameter_dict[0]["intercept_at_lower_threshold"]
        # Check if all intercepts are supplied.
        for interval in keys[1:]:
            if "intercept_at_lower_threshold" in parameter_dict[interval]:
                count_intercepts_supplied += 1
                intercepts[interval] = parameter_dict[interval][
                    "intercept_at_lower_threshold"
                ]
        if (count_intercepts_supplied > 1) & (count_intercepts_supplied != len(keys)):
            raise ValueError(
                "More than one, but not all intercepts are supplied. "
                "The dictionaries should contain either only the lowest intercept "
                "or all intercepts."
            )
        else:
            intercepts = create_intercepts(
                lower_thresholds, upper_thresholds, rates, intercepts[0], func
            )
    return intercepts


def create_intercepts(
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
    intercepts_at_lower_thresholds = np.full_like(upper_thresholds, np.nan)
    intercepts_at_lower_thresholds[0] = intercept_at_lowest_threshold
    for i, up_thr in enumerate(upper_thresholds[:-1]):
        intercepts_at_lower_thresholds[i + 1] = fun(
            up_thr,
            lower_thresholds,
            upper_thresholds,
            rates,
            intercepts_at_lower_thresholds,
        )
    return intercepts_at_lower_thresholds
