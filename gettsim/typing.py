import numpy as np
from pandas.api.types import is_bool_dtype
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_float_dtype
from pandas.api.types import is_integer_dtype


def convert_series_to_internal_type(series, internal_type):
    """Check if data type of series fits to the internal type of gettsim and
    otherwise convert data type of series to the internal type of gettsim.

    Parameters
    ----------
    series : pd.Series
        Some data series.
    internal_type : TypeVar
        One of the internal gettsim types.

    Returns
    -------
    out : adjusted pd.Series
    """

    if internal_type == float:
        # Conversion from boolean to float fails
        if is_bool_dtype(series):
            raise ValueError(f"Conversion of data type to {internal_type} failed.")
        elif not is_float_dtype(series):
            try:
                series = series.astype(float)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    elif internal_type == bool:
        out = is_bool_dtype(series)
        cond = is_integer_dtype(series) or is_float_dtype(series)
        for _, content in series.items():
            cond2 = type(content) == str
        if out:
            series = series
        # input data type is integer or float
        elif cond:
            for _, content in series.items():
                if content == 1 or content == 0:
                    try:
                        series = series.astype(bool)
                    except ValueError:
                        raise ValueError(
                            f"Conversion of data type to {internal_type} failed."
                        )
                else:
                    raise ValueError(
                        f"Conversion to {internal_type} failed."
                        f" Input data does not consist of 1 or 0."
                    )
        # input data type is string
        elif cond2:
            for _, content in series.items():
                if content == "True" or content == "False":
                    try:
                        series = series.astype(bool)
                    except ValueError:
                        raise ValueError(
                            f"Conversion of data type to {internal_type} failed."
                        )
                else:
                    raise ValueError(
                        f"Conversion to {internal_type} failed."
                        f" Input data does not consist of statements True or False."
                    )
        else:
            try:
                series = series.astype(bool)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    elif internal_type == int:
        out = is_integer_dtype(series)
        cond = is_float_dtype(series)
        if out:
            series = series
        elif cond:
            adjusted_series = series.astype(np.int64)
            sum_adjusted = adjusted_series.sum()
            sum_original = series.sum()
            # checking if decimal spaces are equal to 0
            if sum_adjusted == sum_original:
                try:
                    series = series.astype(np.int64)
                except ValueError:
                    raise ValueError(
                        f"Conversion of data type to {internal_type} failed."
                    )
            else:
                raise ValueError(
                    "Data type of input is float but should be int. "
                    "An automatic conversion would lead to rounded numbers."
                )
        else:
            try:
                series = series.astype(int)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    elif internal_type == np.datetime64:
        out = is_datetime64_any_dtype(series)
        if out:
            series = series
        else:
            try:
                series = series.astype(np.datetime64)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    else:
        raise ValueError(f"The internal type {internal_type} is not defined.")

    return series
