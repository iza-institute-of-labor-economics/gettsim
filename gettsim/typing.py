import numpy as np
from pandas.api.types import is_bool_dtype
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_float_dtype
from pandas.api.types import is_integer_dtype


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
    if internal_type == float:
        out = is_float_dtype(series) or is_integer_dtype(series)
    elif internal_type == bool:
        out = is_bool_dtype(series)
    elif internal_type == int:
        out = is_integer_dtype(series)
    elif internal_type == np.datetime64:
        out = is_datetime64_any_dtype(series)
    else:
        raise ValueError(f"The internal type {internal_type} is not defined.")
    return out
