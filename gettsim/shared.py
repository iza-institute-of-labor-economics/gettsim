import inspect
import textwrap

import numpy as np
import numpy_groupies as npg


def format_list_linewise(list_):
    formatted_list = '",\n    "'.join(list_)
    return textwrap.dedent(
        """
        [
            "{formatted_list}",
        ]
        """
    ).format(formatted_list=formatted_list)


def parse_to_list_of_strings(user_input, name):
    """Parse None, str, and list of strings to list of strings.

    Note that the function automatically removes duplicates.

    """
    if user_input is None:
        user_input = []
    elif isinstance(user_input, str):
        user_input = [user_input]
    elif isinstance(user_input, list) and all(isinstance(i, str) for i in user_input):
        pass
    else:
        NotImplementedError(
            f"'{name}' needs to be None, a string or a list of strings."
        )

    return sorted(set(user_input))


def get_names_of_arguments_without_defaults(function):
    """Get argument names without defaults.

    The detection of argument names also works for partialed functions.

    Examples
    --------
    >>> def func(a, b): pass
    >>> get_names_of_arguments_without_defaults(func)
    ['a', 'b']
    >>> import functools
    >>> func_ = functools.partial(func, a=1)
    >>> get_names_of_arguments_without_defaults(func_)
    ['b']

    """
    parameters = inspect.signature(function).parameters

    argument_names_without_defaults = []
    for parameter in parameters:
        if parameters[parameter].default == parameters[parameter].empty:
            argument_names_without_defaults.append(parameter)

    return argument_names_without_defaults


def add_rounding_spec(params_key):
    """Decorator adding the location of the rounding specification to a function.

    Parameters
    ----------
    params_key : str
        Key of the parameters dictionary where rouding specifications are found. For
        functions that are not user-written this is just the name of the respective
        .yaml file.

    Returns
    -------
    func : function
        Function with __rounding_params_key__ attribute
    """

    def inner(func):
        func.__rounding_params_key__ = params_key
        return func

    return inner


def sum_on_group_level(column, group_id):
    """Calculate sum of a column by groups.

    Parameters
    ----------
    column : array
        Array that should be aggregated.
    group_id
        Identifiers of groups.

    Returns
    -------
    array
        Aggregated column, has the same length as column
    """
    fail_if_dtype_not_numerical(column, agg_func="sum")
    out_on_hh = npg.aggregate(group_id, column, func="sum", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def mean_on_group_level(column, group_id):
    fail_if_dtype_not_numerical(column, agg_func="mean")

    out_on_hh = npg.aggregate(group_id, column, func="mean", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def max_on_group_level(column, group_id):
    fail_if_dtype_not_numerical(column, agg_func="max")

    out_on_hh = npg.aggregate(group_id, column, func="max", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def any_on_group_level(column, group_id):
    fail_if_dtype_not_boolean(column, agg_func="any")

    out_on_hh = npg.aggregate(group_id, column, func="any", fill_value=0)

    # Expand to indididual level
    out = out_on_hh[group_id]
    return out


def fail_if_dtype_not_numerical(column, agg_func):
    if not np.issubdtype(column.dtype, np.number):
        raise ValueError(
            f"{agg_func}_on_group_level was applied to a column "
            f"that has dtype {column.dtype}. Allowed are only numerical dtypes."
        )


def fail_if_dtype_not_boolean(column, agg_func):
    if column.dtype != "bool":
        raise ValueError(
            f"{agg_func}_on_group_level was applied to a column "
            f"that has dtype {column.dtype}. Allowed is only boolean dtype."
        )
