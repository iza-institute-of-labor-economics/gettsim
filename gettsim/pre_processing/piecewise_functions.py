import numpy as np

from gettsim._numpy import numpy_vectorize


@numpy_vectorize(
    excluded=[
        "lower_thresholds",
        "upper_thresholds",
        "rates",
        "intercepts_at_lower_thresholds",
        "rates_modified",
    ]
)
def piecewise_polynomial(
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
