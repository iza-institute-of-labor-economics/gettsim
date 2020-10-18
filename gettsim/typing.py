from typing import TypeVar

FloatSeries = TypeVar("FloatSeries")
IntSeries = TypeVar("IntSeries")
BoolSeries = TypeVar("BoolSeries")


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
        out = dtype == float or dtype == int
    elif internal_type == BoolSeries:
        out = dtype == bool
    elif internal_type == IntSeries:
        out = dtype == int
    else:
        raise ValueError(f"The internal type {internal_type} is not defined.")
    return out
