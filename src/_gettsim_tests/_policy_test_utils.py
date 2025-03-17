from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import flatten_dict
import numpy as np
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
        test_file: Path,
        date: datetime.date,
    ) -> None:
        self.input_tree = input_tree
        self.expected_output_tree = expected_output_tree
        self.test_file = test_file
        self.date = date

    @property
    def target_structure(self) -> NestedInputStructureDict:
        flat_target_structure = {
            k: None for k in flatten_dict.flatten(self.expected_output_tree)
        }
        return flatten_dict.unflatten(flat_target_structure)

    @property
    def test_name(self) -> str:
        return self.test_file.stem


def load_policy_test_data(policy_name: str) -> list[PolicyTest]:
    from _gettsim_tests import TEST_DATA_DIR

    root = TEST_DATA_DIR / policy_name

    out = []

    for path_of_test_file in root.glob("**/*.yaml"):
        if _is_skipped(path_of_test_file):
            continue

        with path_of_test_file.open("r", encoding="utf-8") as file:
            raw_test_data: NestedDataDict = yaml.safe_load(file)

        out.extend(
            _get_policy_tests_from_raw_test_data(
                raw_test_data=raw_test_data,
                path_of_test_file=path_of_test_file,
            )
        )

    return out


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
    input_tree: NestedDataDict = flatten_dict.unflatten(
        {
            k: np.array(v)
            for k, v in flatten_dict.flatten(
                merge_trees(inputs.get("provided", {}), inputs.get("assumed", {}))
            ).items()
        }
    )

    merge_trees(inputs.get("provided", {}), inputs.get("assumed", {}))

    all_expected_outputs: NestedDataDict = raw_test_data.get("outputs", {})

    date: datetime.date = _parse_date(path_of_test_file.parent.name)

    flat_expected_outputs = flatten_dict.flatten(all_expected_outputs)

    for target_name, test_data in flat_expected_outputs.items():
        one_expected_output: NestedDataDict = flatten_dict.unflatten(
            {target_name: test_data}
        )
        out.append(
            PolicyTest(
                input_tree=input_tree,
                expected_output_tree=one_expected_output,
                test_file=path_of_test_file.stem,
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
