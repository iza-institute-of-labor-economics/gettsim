import numpy as np
import pandas as pd


def piecewise_polynomial(
    x,
    thresholds,
    rates,
    intercepts_at_lower_thresholds,
    individual_rates=False,
    rates_multiplier=None,
):
    """Calculate value of the piecewise function at `x`.

    Parameters
    ----------
    x : series
        The value that the function is applied to.
    lower_thresholds : numpy.ndarray
        A one-dimensional array containing lower thresholds of each interval.
    upper_thresholds : numpy.ndarray
        A one-dimensional array containing upper thresholds each interval.
    rates : numpy.ndarray
        A two-dimensional array where columns are interval sections and rows correspond
        to the nth polynomial.
    intercepts_at_lower_thresholds : numpy.ndarray
        The intercepts at the lower threshold of each interval.
    individual_rates : bool
        Boolean variable indicating, that intercepts can't be used anymore.

    Returns
    -------
    out : float
        The value of `x` under the piecewise function.

    """
    if x.empty:
        return x
    binned = pd.cut(x, bins=thresholds, right=False, labels=range(len(thresholds) - 1))
    thresholds_individual = binned.replace(
        {i: v for i, v in enumerate(thresholds[:-1])}
    )
    increment_to_calc = x - thresholds_individual
    if individual_rates:
        out = x * 0
        for i in binned.cat.categories[1:-1]:
            threshold_incr = thresholds[i] - thresholds[i - 1]
            for pol in range(1, rates.shape[0] + 1):
                out.loc[binned >= i] += (
                    rates_multiplier.loc[binned >= i]
                    * rates[pol - 1, i - 1]
                    * threshold_incr ** pol
                )
        for pol in range(1, rates.shape[0] + 1):
            out += (
                binned.replace({i: v for i, v in enumerate(rates[pol - 1, :])})
                * rates_multiplier
                * (increment_to_calc ** pol)
            )

    else:
        out = binned.replace(
            {i: v for i, v in enumerate(intercepts_at_lower_thresholds)}
        )

        for pol in range(1, rates.shape[0] + 1):
            out += binned.replace({i: v for i, v in enumerate(rates[pol - 1, :])}) * (
                increment_to_calc ** pol
            )

    return out

    # # Check if value lies within the defined range.
    # if (x < lower_thresholds[0]) or (x > upper_thresholds[-1]) or np.isnan(x):
    #     return np.nan
    # index_interval = np.searchsorted(upper_thresholds, x, side="left")
    # if rates_modified:
    #     # Calculate new intercept
    #     intercept_interval = 0
    #     for interval in range(index_interval):
    #         for pol in range(1, rates.shape[0] + 1):
    #             intercept_interval += (rates[pol - 1, interval] ** pol) * (
    #                 upper_thresholds[interval] - lower_thresholds[interval]
    #             )
    #
    # else:
    #     intercept_interval = intercepts_at_lower_thresholds[index_interval]
    #
    # # Select threshold and calculate corresponding increment into interval
    # lower_thresehold_interval = lower_thresholds[index_interval]
    # increment_to_calc = x - lower_thresehold_interval
    #
    # out = intercept_interval
    # for pol in range(1, rates.shape[0] + 1):
    #     out += rates[pol - 1, index_interval] * (increment_to_calc ** pol)

    return out


def get_piecewise_parameters(parameter_dict, parameter, func_type):
    """Create the objects for piecewise polynomial.



    Parameters
    ----------
    parameter_dict
    parameter
    func_type

    Returns
    -------

    """

    # Get all interval keys.
    keys = sorted(key for key in parameter_dict if isinstance(key, int))

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
        parameter_dict, parameter, lower_thresholds, upper_thresholds, rates, keys,
    )

    piecewise_elements = {
        "thresholds": sorted([lower_thresholds[0], *upper_thresholds]),
        "rates": rates,
        "intercepts_at_lower_thresholds": intercepts,
    }

    return piecewise_elements


def check_threholds(parameter_dict, parameter, keys):
    """Check and transfer raw threshold data.


    Transfer and check raw threshold data, which needs to be specified in a
    piecewise_polynomial layout in the yaml file.

    Parameters
    ----------
    parameter_dict
    parameter
    keys

    Returns
    -------

    """
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
    """Check and transfer raw rates data.

    Transfer and check raw rates data, which needs to be specified in a
    piecewise_polynomial layout in the yaml file.

    Parameters
    ----------
    parameter_dict
    parameter
    keys
    func_type

    Returns
    -------

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
    parameter_dict, parameter, lower_thresholds, upper_thresholds, rates, keys
):
    """Check and transfer raw intercepte data. If necessary create intercepts.

    Transfer and check raw rates data, which needs to be specified in a
    piecewise_polynomial layout in the yaml file.

    Parameters
    ----------
    parameter_dict
    parameter
    lower_thresholds
    upper_thresholds
    rates
    keys

    Returns
    -------

    """
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
                lower_thresholds, upper_thresholds, rates, intercepts[0]
            )
    return intercepts


def create_intercepts(
    lower_thresholds, upper_thresholds, rates, intercept_at_lowest_threshold
):
    """Create intercepts from raw data.

    Parameters
    ----------
    lower_thresholds : np.array
                       The lower thresholds defining the intervals

    upper_thresholds : np.array
                       The upper thresholds defining the intervals

    rates : np.array
           The slope in the interval below the corresponding element of
           *upper_thresholds*.

    intercept_at_lowest_threshold : np.array
                                    Intecept at the lowest threshold

    fun: function handle (currently only piecewise_linear, will need to think about
    whether we can have a generic function with a different interface or make
    it specific )

    Returns
    -------

    """ """

    """
    intercepts_at_lower_thresholds = np.full_like(upper_thresholds, np.nan)
    intercepts_at_lower_thresholds[0] = intercept_at_lowest_threshold
    for i, up_thr in enumerate(upper_thresholds[:-1]):
        intercepts_at_lower_thresholds[i + 1] = piecewise_polynomial_float(
            x=up_thr,
            lower_thresholds=lower_thresholds,
            upper_thresholds=upper_thresholds,
            rates=rates,
            intercepts_at_lower_thresholds=intercepts_at_lower_thresholds,
        )
    return intercepts_at_lower_thresholds


def piecewise_polynomial_float(
    x,
    lower_thresholds,
    upper_thresholds,
    rates,
    intercepts_at_lower_thresholds,
    rates_modified=False,
):
    """Calculate value of the piecewise function at `x`.

    Parameters
    ----------
    x : float
        The value that the function is applied to.
    lower_thresholds : numpy.ndarray
        A one-dimensional array containing lower thresholds of each interval.
    upper_thresholds : numpy.ndarray
        A one-dimensional array containing upper thresholds each interval.
    rates : numpy.ndarray
        A two-dimensional array where columns are interval sections and rows correspond
        to the nth polynomial.
    intercepts_at_lower_thresholds : numpy.ndarray
        The intercepts at the lower threshold of each interval.
    rates_modified : bool
        Boolean variable indicating, that intercepts can't be used anymore.

    Returns
    -------
    out : float
        The value of `x` under the piecewise function.

    """

    # Check if value lies within the defined range.
    if (x < lower_thresholds[0]) or (x > upper_thresholds[-1]) or np.isnan(x):
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
