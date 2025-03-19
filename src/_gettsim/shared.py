import inspect
import textwrap
from collections.abc import Callable
from typing import Any, TypeVar

import flatten_dict
import numpy
import optree
from dags.signature import rename_arguments
from flatten_dict.reducers import make_reducer
from flatten_dict.splitters import make_splitter

from _gettsim.config import QUALIFIED_NAME_SEPARATOR, SUPPORTED_GROUPINGS
from _gettsim.function_types import PolicyFunction
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


qualified_name_reducer = make_reducer(delimiter=QUALIFIED_NAME_SEPARATOR)
qualified_name_splitter = make_splitter(delimiter=QUALIFIED_NAME_SEPARATOR)


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


def merge_trees(left: dict, right: dict) -> dict:
    """
    Merge two pytrees, raising an error if a path is present in both trees.

    Parameters
    ----------
    left
        The first tree to be merged.
    right
        The second tree to be merged.

    Returns
    -------
    The merged pytree.
    """

    if set(optree.tree_paths(left)) & set(optree.tree_paths(right)):
        raise ValueError("Conflicting paths in trees to merge.")

    return upsert_tree(base=left, to_upsert=right)


def upsert_tree(base: dict, to_upsert: dict) -> dict:
    """
    Upsert a tree into another tree for trees defined by dictionaries only.

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


def insert_path_and_value(
    base: dict[str, Any], path_to_insert: tuple[str], value_to_insert: Any = None
) -> dict[str, Any]:
    """Insert a path and value into a tree.

    The path is a list of strings that represent the keys in the nested dictionary. The
    path must not exist in base.
    """
    to_insert = create_tree_from_path_and_value(
        path=path_to_insert, value=value_to_insert
    )
    return merge_trees(left=base, right=to_insert)


def partition_tree_by_reference_tree(
    tree_to_partition: NestedFunctionDict | NestedDataDict,
    reference_tree: NestedFunctionDict | NestedDataDict,
) -> tuple[
    NestedFunctionDict | NestedDataDict,
    NestedFunctionDict | NestedDataDict,
]:
    """
    Partition a tree into two based on the presence of its paths in a reference tree.

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
    ref_paths = set(flatten_dict.flatten(reference_tree).keys())
    flat = flatten_dict.flatten(tree_to_partition)
    intersection = flatten_dict.unflatten(
        {path: leaf for path, leaf in flat.items() if path in ref_paths}
    )
    difference = flatten_dict.unflatten(
        {path: leaf for path, leaf in flat.items() if path not in ref_paths}
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
    function: Callable,
    *,
    mapper: dict | None = None,
    annotations: dict | None = None,
):
    wrapper = rename_arguments(func=function, mapper=mapper)

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


def get_path_for_group_by_id(
    target_path: tuple[str],
    group_by_functions_tree: NestedFunctionDict,
) -> tuple[str]:
    """Get the group-by-identifier for some target path.

    The group-by-identifier is the path to the group identifier that is embedded in the
    name. E.g., "einkommen_hh" has ("demographics", "hh_id") as its group-by-identifier.
    In this sense, the group-by-identifiers live in a global namespace. We generally
    expect them to be unique.

    There is an exception, though: It is enough for them to be unique within the
    uppermost namespace. In that case, however, they cannot be used outside of that
    namespace.

    Parameters
    ----------
    target_path
        The aggregation target.
    group_by_functions_tree
        The group-by functions tree.

    Returns
    -------
    The group-by-identifier, or an empty tuple if it is an individual-level variable.
    """
    group_by_paths = optree.tree_paths(group_by_functions_tree, none_is_leaf=True)
    for g in SUPPORTED_GROUPINGS:
        if target_path[-1].endswith(f"_{g}") and g == "hh":
            # Hardcode because hh_id is not part of the functions tree
            return ("demographics", "hh_id")
        elif target_path[-1].endswith(f"_{g}"):
            return _select_group_by_id_from_candidates(
                candidate_paths=[p for p in group_by_paths if p[-1] == f"{g}_id"],
                target_path=target_path,
            )
    return ()


def _select_group_by_id_from_candidates(
    candidate_paths: list[tuple[str]],
    target_path: tuple[str],
) -> tuple[str]:
    """Select the group-by-identifier from the candidates.

    If there are multiple candidates, the function takes the one that shares the
    first part of the path (uppermost level of namespace) with the aggregation target.

    Raises
    ------
    ValueError
        Raised if the group-by-identifier is ambiguous.

    Parameters
    ----------
    candidates
        The candidates.
    target_path
        The target path.
    nice_target_name
        The nice target name.

    Returns
    -------
    The group-by-identifier.
    """
    if len(candidate_paths) > 1:
        candidate_paths_in_matching_namespace = [
            p for p in candidate_paths if p[0] == target_path[0]
        ]
        if len(candidate_paths_in_matching_namespace) == 1:
            return candidate_paths_in_matching_namespace[0]
        else:
            _fail_with_ambiguous_group_by_identifier(
                all_candidate_paths=candidate_paths,
                candidate_paths_in_matching_namespace=candidate_paths_in_matching_namespace,
                target_path=target_path,
            )
    else:
        return candidate_paths[0]


def _fail_with_ambiguous_group_by_identifier(
    candidate_paths_in_matching_namespace: tuple[str],
    all_candidate_paths: tuple[str],
    target_path: tuple[str],
):
    if len(candidate_paths_in_matching_namespace) == 0:
        paths = "\n    ".join([str(p) for p in all_candidate_paths])
    else:
        paths = "\n    ".join([str(p) for p in candidate_paths_in_matching_namespace])
    msg = format_errors_and_warnings(
        f"""
        Group-by-identifier for target:\n\n    {target_path}\n
        is ambiguous. Group-by-identifiers must be

        1. unique at the uppermost level of the functions tree.
        2. inside the uppermost namespace if there are namespaced identifiers

        Found candidates:\n\n    {paths}
        """
    )
    raise ValueError(msg)
