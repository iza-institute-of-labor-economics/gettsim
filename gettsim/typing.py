from typing import TypeVar

import numpy as np

FloatSeries = TypeVar("FloatSeries")
IntSeries = TypeVar("IntSeries")
BoolSeries = TypeVar("BoolSeries")
DateTimeSeries = TypeVar("DateTimeSeries")


def check_if_series_has_internal_type(series, internal_type):
    """Check if data type of series fits to the internal type of gettsim.

    Parameters
    ----------
    series : pd.Series
        Some data series.
    internal_type : TypeVar
        One of the internal gettsim types.

    Returns
    -------
    out : bool
        Return check variable.
    """
    dtype = series.dtype
    if internal_type == FloatSeries:
        # I think we can allow for ints here?!
        out = np.issubdtype(dtype, np.integer) or np.issubdtype(dtype, np.floating)
    elif internal_type == BoolSeries:
        out = np.issubdtype(dtype, np.bool)
    elif internal_type == IntSeries:
        out = np.issubdtype(dtype, np.integer)
    elif internal_type == DateTimeSeries:
        out = dtype == np.dtype("datetime64[ns]")
    else:
        raise ValueError(f"The internal type {internal_type} is not defined.")
    return out
