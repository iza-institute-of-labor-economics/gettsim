import inspect
import textwrap


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


def add_rounding_spec(base, direction):
    """Decorator to add rounding specification attributes to a function.

    Parameters
    ----------
    base : float
        Precision of rounding (e.g. 0.1 to round to the first decimal place)
    direction : str
        Whether the series should be rounded up, down or to the nearest number

    Returns
    -------
    func : function
        Function with rounding specification attributes
    """

    def inner(func):
        func.__roundingspec__ = {"base": base, "direction": direction}
        return func

    return inner
