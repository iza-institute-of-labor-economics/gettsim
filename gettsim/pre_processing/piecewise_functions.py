import numpy as np


def _piecewise_polynomial(
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


piecewise_polynomial = np.vectorize(
    _piecewise_polynomial,
    excluded=[
        "lower_thresholds",
        "upper_thresholds",
        "rates",
        "intercepts_at_lower_thresholds",
        "rates_modified",
    ],
)
