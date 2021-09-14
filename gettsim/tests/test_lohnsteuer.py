import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.demographic_vars import determine_steuerklassen
from gettsim.policy_environment import set_up_policy_environment
from gettsim.taxes.lohn_st import calc_lohnsteuer

INPUT_COLS = ["tu_id", "pid", "m_wage", "e_st_klasse", "child_num_kg"]

YEARS = [2021]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_lohn_steuer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


def test_steuerklassen():
    policy_params, policy_functions = set_up_policy_environment("2021")

    # Tests steuerklassen are correctly assigned based on our assumptions
    df = pd.DataFrame(
        {
            "tu_id": [1, 2, 2, 3, 3, 3, 4, 4],
            "bruttolohn": [2000, 2000, 2000, 2000, 0, 0, 2000, 0],
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

    result = df.groupby("tu_id").apply(
        determine_steuerklassen(
            df["gemeinsam_veranlagt_tu"],
            df["alleinerziehend_tu"],
            df["bruttolohn"],
            df["anz_erwachsene_tu"],
            policy_params["eink_st"],
        ),
    )

    assert_series_equal(df["steuerklasse"], result)


@pytest.mark.parametrize("year", YEARS)
def test_lohnsteuer(input_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    e_st_abzuege_params = set_up_policy_environment(
        year=year, group="e_st_abzuege", raw_group_data=e_st_abzuege_raw_data
    )
    e_st_params = set_up_policy_environment(
        year=year, group="e_st", raw_group_data=e_st_raw_data
    )
    soli_st_params = set_up_policy_environment(
        year=year, group="soli_st", raw_group_data=soli_st_raw_data
    )

    OUT_COLS = ["lohnsteuer"]

    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby("tu_id").apply(
        calc_lohnsteuer,
        params=e_st_params,
        e_st_abzuege_params=e_st_abzuege_params,
        soli_st_params=soli_st_params,
    )
    """
    e_st_abzuege_params=e_st_abzuege_params,
        soli_st_params=soli_st_params,
        abgelt_st_params=abgelt_st_params,
    """
    assert_frame_equal(df[OUT_COLS], year_data[OUT_COLS], check_dtype=False)
