import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment

INPUT_COLS = ["tu_id", "pid", "bruttolohn_m", "steuerklasse", "child_num_kg"]

YEARS = [2021]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_lohn_steuer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


def test_steuerklassen():
    policy_params, policy_functions = set_up_policy_environment("2021")

    # Tests whether steuerklassen are correctly assigned based on our assumptions
    df = pd.DataFrame(
        {
            "tu_id": [1, 2, 2, 3, 3, 3, 4, 4],
            "bruttolohn_m": [2000, 2000, 2000, 2000, 0, 0, 2000, 0],
            "gemeinsam_veranlagt_tu": [
                False,
                False,
                False,
                True,
                True,
                False,
                False,
                False,
            ],
            "anz_erwachsene_tu": [1, 2, 2, 2, 2, 2, 1, 1],
            "alleinerziehend_tu": [
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
            ],
            "steuerklasse": [1, 4, 4, 3, 5, 4, 2, 2],
        }
    )

    result = compute_taxes_and_transfers(
        data=df.drop(columns=["steuerklasse"]),
        params=policy_params,
        functions=policy_functions,
        targets="steuerklasse",
        columns_overriding_functions=["alleinerziehend_tu", "anz_erwachsene_tu"],
    )

    assert_series_equal(df["steuerklasse"], result["steuerklasse"])


@pytest.mark.parametrize("year", YEARS)
def test_lohnsteuer(input_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    df["alleinerziehend"] = df["steuerklasse"] == 2
    df["kind"] = 0
    df["jahr_renteneintr"] = 2060
    df["kinderlos"] = df["child_num_kg"] == 0

    policy_params, policy_functions = set_up_policy_environment(date=year)
    out_cols = ["lohn_steuer"]

    result = compute_taxes_and_transfers(
        data=df, params=policy_params, functions=policy_functions, targets=OUT_COLS
    )
    print(result)

    assert_frame_equal(df[OUT_COLS], year_data[out_cols], check_dtype=False)
