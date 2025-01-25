import functools
import inspect
import operator
import textwrap
from collections.abc import Callable
from typing import Any, TypeVar

import numpy
from dags.signature import rename_arguments
from optree import tree_flatten_with_path

from _gettsim.config import SUPPORTED_GROUPINGS
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.gettsim_typing import NestedDataDict, NestedFunctionDict


class KeyErrorMessage(str):
    """Subclass str to allow for line breaks in KeyError messages."""

    __slots__ = ()

    def __repr__(self):
        return str(self)


def format_list_linewise(list_):
    formatted_list = '",\n    "'.join(list_)
    return textwrap.dedent(
        """
        [
            "{formatted_list}",
        ]
        """
    ).format(formatted_list=formatted_list)


def tree_update(
    tree: dict[str, Any], path: list[str], value: Any = None
) -> dict[str, Any]:
    """Update tree with a path and value.

    The path is a list of strings that represent the keys in the nested dictionary. If
    the path does not exist, it will be created. If the path already exists, the value
    will be updated.
    """
    update_dict = create_dict_from_list(path)
    set_by_path(update_dict, path, value)
    return merge_nested_dicts(tree, update_dict)


def create_dict_from_list(keys: list[str]) -> dict:
    """Create a nested dict from a list of strings.

    Example:
        Input:
            keys = ["a", "b", "c"]
        Result:
            {"a": {"b": {"c": None}}}

    """
    nested_dict = None
    for key in reversed(keys):
        nested_dict = {key: nested_dict}
    return nested_dict


def merge_nested_dicts(base_dict: dict, update_dict: dict) -> dict:
    """
    Recursively merge nested dictionaries.

    Example:
        Input:
            base_dict = {"a": {"b": {"c": None}}}
            update_dict = {"a": {"b": {"d": None}}}
        Output:
            {"a": {"b": {"c": None, "d": None}}}

    Parameters
    ----------
    base_dict : dict
        The base dictionary.
    update_dict : dict
        The dictionary to update the base dictionary.

    Returns
    -------
    dict
        The merged dictionary.
    """
    result = base_dict.copy()

    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_nested_dicts(result[key], value)
        else:
            result[key] = value

    return result


def _filter_tree_by_name_list(
    tree: NestedFunctionDict | NestedDataDict,
    qualified_names_list: list[str],
) -> tuple[NestedFunctionDict, NestedFunctionDict]:
    """Filter a tree by name.

    Splits the functions tree in two parts: functions whose qualified name is in the
    qualified_names_list and functions whose qualified name is not in
    qualified_names_list.

    Parameters
    ----------
    tree : NestedFunctionDict | NestedDataDict
        Dictionary containing functions to build the DAG.
    qualified_names_list : list[str]
        List of qualified names.

    Returns
    -------
    not_in_names_list : NestedFunctionDict
        All functions except the ones that are overridden by an input column.
    in_names_list : NestedFunctionDict
        Functions that are overridden by an input column.

    """
    not_in_names_list = {}
    in_names_list = {}

    paths, leafs, _ = tree_flatten_with_path(tree)

    for name, leaf in zip(paths, leafs):
        qualified_name = "__".join(name)
        if qualified_name in qualified_names_list:
            in_names_list = tree_update(
                in_names_list,
                name,
                leaf,
            )
        else:
            not_in_names_list = tree_update(
                not_in_names_list,
                name,
                leaf,
            )

    return not_in_names_list, in_names_list


def format_errors_and_warnings(text, width=79):
    """Format our own exception messages and warnings by dedenting paragraphs and
    wrapping at the specified width. Mainly required because of messages are written as
    part of indented blocks in our source code.

    Parameters
    ----------
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


def get_names_of_arguments_without_defaults(function: PolicyFunction) -> list[str]:
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

    return [p for p in parameters if parameters[p].default == parameters[p].empty]


def remove_group_suffix(col):
    out = col
    for g in SUPPORTED_GROUPINGS:
        out = out.removesuffix(f"_{g}")

    return out


Key: TypeVar = TypeVar("Key")
Out: TypeVar = TypeVar("Out")


def join_numpy(
    foreign_key: numpy.ndarray[Key],
    primary_key: numpy.ndarray[Key],
    target: numpy.ndarray[Out],
    value_if_foreign_key_is_missing: Out,
) -> numpy.ndarray[Out]:
    """
    Given a foreign key, find the corresponding primary key, and return the target at
    the same index as the primary key.

    Parameters
    ----------
    foreign_key : numpy.ndarray[Key]
        The foreign keys.
    primary_key : numpy.ndarray[Key]
        The primary keys.
    target : numpy.ndarray[Out]
        The targets in the same order as the primary keys.
    value_if_foreign_key_is_missing : Out
        The value to return if no matching primary key is found.

    Returns
    -------
    numpy.ndarray[Out]
        The joined array.
    """
    if len(numpy.unique(primary_key)) != len(primary_key):
        keys, counts = numpy.unique(primary_key, return_counts=True)
        duplicate_primary_keys = keys[counts > 1]
        raise ValueError(f"Duplicate primary keys: {duplicate_primary_keys}")

    invalid_foreign_keys = foreign_key[
        (foreign_key >= 0) & (~numpy.isin(foreign_key, primary_key))
    ]

    if len(invalid_foreign_keys) > 0:
        raise ValueError(f"Invalid foreign keys: {invalid_foreign_keys}")

    # For each foreign key and for each primary key, check if they match
    matches_foreign_key = foreign_key[:, None] == primary_key

    # For each foreign key, add a column with True at the end, to later fall back to
    # the value for unresolved foreign keys
    padded_matches_foreign_key = numpy.pad(
        matches_foreign_key, ((0, 0), (0, 1)), "constant", constant_values=True
    )

    # For each foreign key, compute the index of the first matching primary key
    indices = numpy.argmax(padded_matches_foreign_key, axis=1)

    # Add the value for unresolved foreign keys at the end of the target array
    padded_targets = numpy.pad(
        target, (0, 1), "constant", constant_values=value_if_foreign_key_is_missing
    )

    # Return the target at the index of the first matching primary key
    return padded_targets.take(indices)


def rename_arguments_and_add_annotations(
    function: Callable | None = None,
    *,
    mapper: dict | None = None,
    annotations: dict | None = None,
):
    wrapper = rename_arguments(function, mapper=mapper)

    if annotations:
        wrapper.__annotations__ = annotations

    return wrapper


def get_by_path(data_dict, key_list):
    """Access a nested object in root by item sequence."""
    return functools.reduce(operator.getitem, key_list, data_dict)


def set_by_path(data_dict, key_list, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(data_dict, key_list[:-1])[key_list[-1]] = value


def get_path_from_qualified_name(qualified_name: str) -> list[str]:
    return qualified_name.split("__")


def tree_to_dict_with_qualified_name(
    tree: dict[str, Any], none_is_leaf: bool = True
) -> dict[str, Any]:
    """Flatten a nested dictionary and return a dictionary with qualified names."""
    qualified_names, flattened_tree, _ = tree_flatten_with_qualified_name(
        tree, none_is_leaf=none_is_leaf
    )
    return dict(zip(qualified_names, flattened_tree))


def tree_flatten_with_qualified_name(
    tree: dict[str, Any],
    none_is_leaf: bool = True,
) -> tuple[list[list[str]], list[Any], list[str]]:
    """Flatten a nested dictionary and qualified names, tree_spec, and leafs."""
    paths, flattened_tree, tree_spec = tree_flatten_with_path(
        tree, none_is_leaf=none_is_leaf
    )
    qualified_names = ["__".join(path) for path in paths]
    return qualified_names, flattened_tree, tree_spec
