import functools
import inspect
import operator
import textwrap
from collections.abc import Callable
from dataclasses import is_dataclass
from typing import Any, TypeVar

import numpy
import optree
from dags.signature import rename_arguments

from _gettsim.config import QUALIFIED_NAME_SEPARATOR, SUPPORTED_GROUPINGS
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


def create_tree_from_qualified_names(qualified_names: set[str]) -> dict:
    """Create a tree from a set of qualified names.

    Parameters
    ----------
    qualified_names
        Set of qualified names.

            Example: {"a__b__c", "a__b__d", "a__e"}

    Returns
    -------
    Tree with qualified names as keys, all leaves are None.

    Example: {"a": {"b": {"c": None, "d": None}, "e": None}}
    """
    paths = [
        create_tree_from_path(get_path_from_qualified_name(qn))
        for qn in qualified_names
    ]
    return functools.reduce(lambda x, y: tree_merge(x, y), paths, {})


def create_tree_from_path(path: tuple[str]) -> dict:
    """Create a nested dict from a list of strings.

    Example:
        Input:
            keys = ("a", "b", "c")
        Result:
            {"a": {"b": {"c": None}}}

    """
    nested_dict = None
    for entry in reversed(path):
        nested_dict = {entry: nested_dict}
    return nested_dict


def tree_merge(base_tree: dict, update_tree: dict) -> dict:
    """
    Recursively merge trees.

    Dataclasses are treated as leaves and not merged.

    Example:
        Input:
            base_tree = {"a": {"b": {"c": None}}}
            update_tree = {"a": {"b": {"d": None}}}
        Output:
            {"a": {"b": {"c": None, "d": None}}}

    Parameters
    ----------
    base_tree : dict
        The base dictionary.
    update_tree : dict
        The dictionary to update the base dictionary.

    Returns
    -------
    dict
        The merged dictionary.
    """
    result = base_tree.copy()

    for key, value in update_tree.items():
        base_value = result.get(key)
        if (
            key in result
            and isinstance(base_value, dict)
            and isinstance(value, dict)
            and not is_dataclass(value)
        ):
            result[key] = tree_merge(base_value, value)
        else:
            result[key] = value

    return result


def tree_update(
    tree: dict[str, Any], tree_path: list[str], value: Any = None
) -> dict[str, Any]:
    """Update tree with a path and value.

    The path is a list of strings that represent the keys in the nested dictionary. If
    the path does not exist, it will be created. If the path already exists, the value
    will be updated.
    """
    update_dict = create_tree_from_path(tree_path)
    tree_set_by_path(update_dict, tree_path, value)
    return tree_merge(tree, update_dict)


def partition_tree_by_reference_tree(
    tree_to_partition: NestedFunctionDict | NestedDataDict,
    reference_tree: NestedDataDict,
) -> tuple[NestedFunctionDict, NestedFunctionDict]:
    """
    Partition a tree into two separate trees based on the presence of its leaves in a
    reference tree.

    Parameters
    ----------
    tree_to_partition
        The tree to be partitioned.
    reference_tree
        The reference tree used to determine the partitioning.

    Returns
    -------
    A tuple containing:
    - The first tree with leaves present in both trees.
    - The second tree with leaves absent in the reference tree.
    """

    # Get reference paths once to avoid repeated tree traversal
    ref_paths = set(optree.tree_paths(reference_tree, none_is_leaf=True))
    intersection = {}
    difference = {}
    # Use tree_flatten_with_path to get paths and leaves in a single pass
    for path, leaf in zip(
        *optree.tree_flatten_with_path(tree_to_partition, none_is_leaf=True)[:2]
    ):
        if path in ref_paths:
            intersection = tree_update(intersection, path, leaf)
        else:
            difference = tree_update(difference, path, leaf)
    return intersection, difference


def format_errors_and_warnings(text: str, width: int = 79) -> str:
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
        msg = format_errors_and_warnings(
            f"Duplicate primary keys: {duplicate_primary_keys}",
        )
        raise ValueError(msg)

    invalid_foreign_keys = foreign_key[
        (foreign_key >= 0) & (~numpy.isin(foreign_key, primary_key))
    ]

    if len(invalid_foreign_keys) > 0:
        msg = format_errors_and_warnings(
            f"Invalid foreign keys: {invalid_foreign_keys}",
        )
        raise ValueError(msg)

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


def tree_get_by_path(data_dict, key_list):
    """Access a nested object in root by item sequence."""
    return functools.reduce(operator.getitem, key_list, data_dict)


def tree_set_by_path(data_dict, key_list, value):
    """Set a value in a nested object in root by item sequence."""
    tree_get_by_path(data_dict, key_list[:-1])[key_list[-1]] = value


def get_path_from_qualified_name(qualified_name: str) -> tuple[str]:
    return tuple(qualified_name.split(QUALIFIED_NAME_SEPARATOR))


# TODO(@MImmesberger): Remove.
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
    paths, flattened_tree, tree_spec = optree.tree_flatten_with_path(
        tree, none_is_leaf=none_is_leaf
    )
    qualified_names = [QUALIFIED_NAME_SEPARATOR.join(path) for path in paths]
    return qualified_names, flattened_tree, tree_spec


def assert_valid_pytree(tree: Any, leaf_checker: Callable, tree_name: str) -> None:
    """
    Recursively assert that a pytree (nested dict) meets the following conditions:
      - The tree is a dictionary.
      - All keys are strings.
      - All leaves satisfy a provided condition (leaf_checker).

    Parameters
    ----------
    tree : Any
         The tree to validate.
    leaf_checker : Callable
         A function that takes a leaf and returns True if it is valid.
    tree_name : str
         The name of the tree (used for error messages).

    Raises
    ------
    TypeError
         If any branch or leaf does not meet the expected requirements.
    """

    def _assert_valid_pytree(subtree: Any, current_key: tuple[str, ...]) -> None:
        def format_key_path(key_tuple: tuple[str, ...]) -> str:
            return "".join(f"[{k}]" for k in key_tuple)

        if not isinstance(subtree, dict):
            path_str = format_key_path(current_key)
            msg = format_errors_and_warnings(
                f"{tree_name}{path_str} must be a dict, got {type(subtree)}."
            )
            raise TypeError(msg)

        for key, value in subtree.items():
            new_key_path = (*current_key, key)
            if not isinstance(key, str):
                msg = format_errors_and_warnings(
                    f"Key {key} in {tree_name}{format_key_path(current_key)} must be a "
                    f"string but got {type(key)}."
                )
                raise TypeError(msg)
            if isinstance(value, dict):
                _assert_valid_pytree(value, new_key_path)
            else:
                if not leaf_checker(value):
                    msg = format_errors_and_warnings(
                        f"Leaf at {tree_name}{format_key_path(new_key_path)} is "
                        f"invalid: got {value} of type {type(value)}."
                    )
                    raise TypeError(msg)

    _assert_valid_pytree(tree, current_key=())
