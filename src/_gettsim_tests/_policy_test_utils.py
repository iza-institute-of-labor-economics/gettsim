from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import dags.tree as dt
import pandas as pd
import yaml

from _gettsim.shared import merge_trees

if TYPE_CHECKING:
    from pathlib import Path

    from _gettsim.gettsim_typing import NestedDataDict, NestedInputStructureDict


class PolicyTest:
    """A class for a single policy test."""

    def __init__(
        self,
        input_tree: NestedDataDict,
        expected_output_tree: NestedDataDict,
        path: Path,
        date: datetime.date,
    ) -> None:
        self.input_tree = input_tree
        self.expected_output_tree = expected_output_tree
        self.path = path
        self.date = date

    @property
    def target_structure(self) -> NestedInputStructureDict:
        flat_target_structure = {
            k: None for k in dt.flatten_to_tree_paths(self.expected_output_tree)
        }
        return dt.unflatten_from_tree_paths(flat_target_structure)

    @property
    def test_name(self) -> str:
        return self.path.stem


def load_policy_test_data(policy_name: str) -> list[PolicyTest]:
    from _gettsim_tests import TEST_DATA_DIR

    root = TEST_DATA_DIR / policy_name

    out = []

    for path_of_test_file in root.glob("**/*.yaml"):
        if _is_skipped(path_of_test_file):
            continue

        with path_of_test_file.open("r", encoding="utf-8") as file:
            raw_test_data: NestedDataDict = yaml.safe_load(file)

        # TODO(@MImmesberger): Remove this before merging this PR.
        raw_test_data = get_test_data_as_tree(raw_test_data)

        out.extend(
            _get_policy_tests_from_raw_test_data(
                raw_test_data=raw_test_data,
                path_of_test_file=path_of_test_file,
            )
        )

    return out


def get_test_data_as_tree(test_data: NestedDataDict) -> NestedDataDict:
    provided_inputs = test_data["inputs"].get("provided", {})
    assumed_inputs = test_data["inputs"].get("assumed", {})

    unflattened_dict = {}
    unflattened_dict["inputs"] = {}
    unflattened_dict["outputs"] = {}
    if provided_inputs:
        unflattened_dict["inputs"]["provided"] = dt.unflatten_from_qual_names(
            provided_inputs
        )
    else:
        unflattened_dict["inputs"]["provided"] = {}
    if assumed_inputs:
        unflattened_dict["inputs"]["assumed"] = dt.unflatten_from_qual_names(
            assumed_inputs
        )
    else:
        unflattened_dict["inputs"]["assumed"] = {}

    unflattened_dict["outputs"] = dt.unflatten_from_qual_names(test_data["outputs"])

    return unflattened_dict


def _is_skipped(test_file: Path) -> bool:
    return "skip" in test_file.stem or "skip" in test_file.parent.name


def _get_policy_tests_from_raw_test_data(
    raw_test_data: NestedDataDict, path_of_test_file: Path
) -> list[PolicyTest]:
    """Get a list of PolicyTest objects from raw test data.

    Args:
        raw_test_data: The raw test data.

    Returns:
        A list of PolicyTest objects.
    """
    out = []

    inputs: NestedDataDict = raw_test_data.get("inputs", {})
    input_tree: NestedDataDict = dt.unflatten_from_tree_paths(
        {
            k: pd.Series(v)
            for k, v in dt.flatten_to_tree_paths(
                merge_trees(inputs.get("provided", {}), inputs.get("assumed", {}))
            ).items()
        }
    )

    expected_output_tree: NestedDataDict = dt.unflatten_from_tree_paths(
        {
            k: pd.Series(v)
            for k, v in dt.flatten_to_tree_paths(
                raw_test_data.get("outputs", {})
            ).items()
        }
    )

    date: datetime.date = _parse_date(path_of_test_file.parent.name)

    if expected_output_tree == {}:
        out.append(
            PolicyTest(
                input_tree=input_tree,
                expected_output_tree={},
                path=path_of_test_file,
                date=date,
            )
        )
    else:
        for target_name, output_data in dt.flatten_to_tree_paths(
            expected_output_tree
        ).items():
            one_expected_output: NestedDataDict = dt.unflatten_from_tree_paths(
                {target_name: output_data}
            )
            out.append(
                PolicyTest(
                    input_tree=input_tree,
                    expected_output_tree=one_expected_output,
                    path=path_of_test_file,
                    date=date,
                )
            )

    return out


def _parse_date(date: str) -> datetime.date:
    parts = date.split("-")

    if len(parts) == 1:
        return datetime.date(int(parts[0]), 1, 1)
    if len(parts) == 2:
        return datetime.date(int(parts[0]), int(parts[1]), 1)
    if len(parts) == 3:
        return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
