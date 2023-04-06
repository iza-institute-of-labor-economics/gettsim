from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

_ValueDict = dict[str, list[Any]]


class PolicyTestSet:
    def __init__(self, policy_name: str, test_data: list[PolicyTestData]):
        self.policy_name = policy_name
        self.test_data = test_data

    @property
    def parametrize_args(self) -> list[tuple[PolicyTestData, str]]:
        return [(test, column) for test in self.test_data for column in test.output_df]

    def merged_input_df(self) -> pd.DataFrame:
        return pd.concat([test.input_df for test in self.test_data], ignore_index=True)

    def merged_output_df(self) -> pd.DataFrame:
        return pd.concat([test.output_df for test in self.test_data], ignore_index=True)


class PolicyTestData:
    def __init__(  # noqa: PLR0913
        self,
        policy_name: str,
        test_file: Path,
        household_name: str,
        date: str,
        inputs_provided: _ValueDict,
        inputs_assumed: _ValueDict,
        outputs: _ValueDict,
    ):
        self.policy_name = policy_name
        self.test_file = test_file
        self.household_name = household_name
        self.date: date = _parse_date(date)
        self._inputs_provided = inputs_provided
        self._inputs_assumed = inputs_assumed
        self._outputs = outputs

    @property
    def input_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(
            {**self._inputs_provided, **self._inputs_assumed}
        ).reset_index(drop=True)

    @property
    def output_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self._outputs).reset_index(drop=True)

    def __repr__(self) -> str:
        return f"PolicyTestData({self.policy_name}, {self.test_file.name}, {self.household_name})"

    def __str__(self) -> str:
        return f"{self.test_file.name} {self.household_name}"


def load_policy_test_data(policy_name: str) -> PolicyTestSet:
    from _gettsim_tests import TEST_DATA_DIR

    root = TEST_DATA_DIR / policy_name

    out = []

    for test_file in root.glob("*.yaml"):
        if "skip" in test_file.stem:
            continue

        with test_file.open("r", encoding="utf-8") as file:
            test_data: dict[str, dict] = yaml.safe_load(file)

        date = test_file.stem

        for household_name, household_data in test_data.items():
            inputs: dict[str, dict] = household_data["inputs"]
            inputs_provided: _ValueDict = inputs["provided"]
            inputs_assumed: _ValueDict = inputs["assumed"]
            outputs: _ValueDict = household_data["outputs"]

            out.append(
                PolicyTestData(
                    policy_name=policy_name,
                    test_file=test_file,
                    household_name=household_name,
                    date=date,
                    inputs_provided=inputs_provided,
                    inputs_assumed=inputs_assumed,
                    outputs=outputs,
                )
            )

    return PolicyTestSet(policy_name, out)


def _parse_date(date: str) -> datetime.date:
    parts = date.split("-")

    if len(parts) == 1:
        return datetime.date(int(parts[0]), 1, 1)
    if len(parts) == 2:
        return datetime.date(int(parts[0]), int(parts[1]), 1)
    if len(parts) == 3:
        return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
