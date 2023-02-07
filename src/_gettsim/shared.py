import inspect
import textwrap

from _gettsim.config import SUPPORTED_GROUPINGS


class KeyErrorMessage(str):
    """Subclass str to allow for line breaks in KeyError messages."""

    def __repr__(self):
        return str(self)


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
            f"{name!r} needs to be None, a string or a list of strings."
        )

    return sorted(set(user_input))


def format_errors_and_warnings(text, width=79):
    """Format our own exception messages and warnings by dedenting paragraphs and
    wrapping at the specified width. Mainly required because of messages are written as
    part of indented blocks in our source code.

    Parameter
    ---------
    text : str
        The text which can include multiple paragraphs separated by two newlines.
    width : int
        The text will be wrapped by `width` characters.

    Returns
    -------
    formatted_text : str
        Correctly dedented, wrapped text.

    """
    text = text.lstrip("\n")
    paragraphs = text.split("\n\n")
    wrapped_paragraphs = []
    for paragraph in paragraphs:
        dedented_paragraph = textwrap.dedent(paragraph)
        wrapped_paragraph = textwrap.fill(dedented_paragraph, width=width)
        wrapped_paragraphs.append(wrapped_paragraph)

    formatted_text = "\n\n".join(wrapped_paragraphs)

    return formatted_text


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


def remove_group_suffix(col):
    out = col
    for g in SUPPORTED_GROUPINGS:
        out = out.removesuffix(f"_{g}")

    return out
