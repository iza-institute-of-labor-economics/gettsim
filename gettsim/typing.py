import numpy as np
from pandas.api.types import is_bool_dtype
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_float_dtype
from pandas.api.types import is_integer_dtype
from pandas.api.types import is_object_dtype


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
    # Copy input series in out
    out = series.copy()

    # Conversion to float
    if internal_type == float:
        # Conversion from boolean to float fails
        if is_bool_dtype(out):
            raise ValueError(
                f"Your variable {series} has the data type boolean."
                f" Conversion of boolean to required data type float is not supported."
            )
        if is_object_dtype(out):
            raise ValueError(
                f"Your variable {series} has the data type object."
                f" GETTSIM does not support this data type."
            )
        elif not is_float_dtype(out):
            try:
                out = out.astype(float)
            except ValueError:
                raise ValueError(
                    f"Your variable {series} has the data type {type(series)}."
                    f" Conversion of required data type {internal_type} failed."
                )

    # Conversion to int
    elif internal_type == int:
        if is_float_dtype(out):

            # checking if decimal places are equal to 0, if not return error
            if np.array_equal(out, out.astype(np.int64)):
                out = out.astype(np.int64)
            else:
                raise ValueError(
                    f"Your variable {series} has the data type float."
                    f"Conversion of float to required data type int is only supported"
                    f" if all decimal places of input data are equal to 0."
                )
        if is_object_dtype(out):
            raise ValueError(
                f"Your variable {series} has the data type object."
                f" GETTSIM does not support this data type."
            )
        elif not is_integer_dtype(out):
            try:
                out = out.astype(np.int64)
            except ValueError:
                raise ValueError(
                    f"Your variable {series} has the data type {type(series)}."
                    f" Conversion of required data type {internal_type} failed."
                )

    # Conversion to boolean
    elif internal_type == bool:

        # if input data type is integer or float,
        if is_integer_dtype(out) or is_float_dtype(out):

            # check if series consists only of 1 or 0
            if len([v for v in out.unique() if v not in [1, 0]]) == 0:
                out = out.astype(bool)
            else:
                raise ValueError(
                    f"Your variable {series} has the data type {type(series)}."
                    f"Conversion of {type(series)} to boolean is supported only"
                    f" if input data exclusively contains '1' and '0'."
                )

        # if input data type is object, raise error
        elif is_object_dtype(out):
            raise ValueError(
                f"Your variable {series} has the data type object."
                f" GETTSIM does not support this data type."
            )
        elif not is_bool_dtype(out):
            raise ValueError(
                f"Your variable {series} has the data type {type(series)}."
                f" Conversion to bool is supported only for"
                f" int, float or object columns."
            )

    # Conversion to DateTime
    elif internal_type == np.datetime64:
        if is_object_dtype(out):
            raise ValueError(
                f"Your variable {series} has the data type object."
                f" GETTSIM does not support this data type."
            )
        elif not is_datetime64_any_dtype(out):
            try:
                out = out.astype(np.datetime64)
            except ValueError:
                raise ValueError(
                    f"Your variable {series} has the data type {type(series)}."
                    f" Conversion of required data type {internal_type} failed."
                )
    else:
        raise ValueError(f"The internal type {internal_type} is not yet supported.")

    return out
