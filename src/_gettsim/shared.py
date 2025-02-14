import inspect
import textwrap
from collections.abc import Callable
from typing import Any, TypeVar

import numpy
import optree
from dags.signature import rename_arguments

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


def tree_structure_from_paths(paths: list[tuple[str]]) -> dict:
    """Create a tree structure from a list of paths with 'None' as leaves.

    Note: In case of conflicting paths, the last path takes precedence.

    Example:
        Input:
            paths = [("a", "b", "c"), ("a", "b", "d")]
        Output:
            {"a": {"b": {"c": None, "d": None}}}

    Parameters
    ----------
    paths : list[tuple[str]]
        The paths to create the tree structure from.

    Returns
    -------
    The tree structure.
    """
    tree_structure = {}
    for path in paths:
        tree_structure_from_path = create_tree_from_path_and_value(path)
        tree_structure = upsert_tree(
            base=tree_structure,
            to_upsert=tree_structure_from_path,
        )
    return tree_structure


def create_tree_from_path_and_value(path: tuple[str], value: Any = None) -> dict:
    """Create a nested dict with 'path' as keys and 'value' as leaf.

    Example:
        Input:
            path = ("a", "b", "c")
            value = None
        Result:
            {"a": {"b": {"c": None}}}

    Parameters
    ----------
    path
        The path to create the tree structure from.
    value (Optional)
        The value to insert into the tree structure.

    Returns
    -------
    The tree structure.
    """
    nested_dict = value
    for entry in reversed(path):
        nested_dict = {entry: nested_dict}
    return nested_dict


def upsert_tree(base: dict, to_upsert: dict) -> dict:
    """
    Upsert a tree into another tree for trees defined by dictionaries only.

    Dataclasses are treated as leaves and not merged.

    Note: In case of conflicting trees, the to_upsert takes precedence.

    Example:
        Input:
            base = {"a": {"b": {"c": None}}}
            to_upsert = {"a": {"b": {"d": None}}}
        Output:
            {"a": {"b": {"c": None, "d": None}}}

    Parameters
    ----------
    base
        The base dictionary.
    to_upsert
        The dictionary to update the base dictionary.

    Returns
    -------
    The merged dictionary.
    """
    result = base.copy()

    for key, value in to_upsert.items():
        base_value = result.get(key)
        if key in result and isinstance(base_value, dict) and isinstance(value, dict):
            result[key] = upsert_tree(base=base_value, to_upsert=value)
        else:
            result[key] = value

    return result


def upsert_path_and_value(
    base: dict[str, Any], path_to_upsert: tuple[str], value_to_upsert: Any = None
) -> dict[str, Any]:
    """Update tree with a path and value.

    The path is a list of strings that represent the keys in the nested dictionary. If
    the path does not exist, it will be created. If the path already exists, the value
    will be updated.
    """
    to_upsert = create_tree_from_path_and_value(
        path=path_to_upsert, value=value_to_upsert
    )
    return upsert_tree(base=base, to_upsert=to_upsert)


def partition_tree_by_reference_tree(
    tree_to_partition: NestedFunctionDict | NestedDataDict,
    reference_tree: NestedFunctionDict | NestedDataDict,
) -> tuple[
    NestedFunctionDict | NestedDataDict,
    NestedFunctionDict | NestedDataDict,
]:
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
            intersection = upsert_path_and_value(
                base=intersection, path_to_upsert=path, value_to_upsert=leaf
            )
        else:
            difference = upsert_path_and_value(
                base=difference, path_to_upsert=path, value_to_upsert=leaf
            )
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


def assert_valid_gettsim_pytree(
    tree: Any, leaf_checker: Callable, tree_name: str
) -> None:
    """
    Recursively assert that a pytree meets the following conditions:
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

    def _assert_valid_gettsim_pytree(
        subtree: Any, current_key: tuple[str, ...]
    ) -> None:
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
                _assert_valid_gettsim_pytree(value, new_key_path)
            else:
                if not leaf_checker(value):
                    msg = format_errors_and_warnings(
                        f"Leaf at {tree_name}{format_key_path(new_key_path)} is "
                        f"invalid: got {value} of type {type(value)}."
                    )
                    raise TypeError(msg)

    _assert_valid_gettsim_pytree(tree, current_key=())
