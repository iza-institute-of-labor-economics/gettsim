import itertools

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment


# Variables for the standard wohngeld test.
INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "kind",
    "bruttokaltmiete_m_hh",
    "alleinerziehend",
    "alter",
    "immobilie_baujahr_hh",
    "kindergeld_anspruch",
    "mietstufe",
    "bruttolohn_m",
    "gesamte_rente_m",
    "ertragsanteil",
    "elterngeld_m",
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "unterhaltsvors_m",
    "brutto_eink_1",
    "brutto_eink_4",
    "brutto_eink_5",
    "brutto_eink_6",
    "eink_st_m",
    "ges_rentenv_beitr_m",
    "ges_krankenv_beitr_m",
    "behinderungsgrad",
    "jahr",
]
YEARS_TEST_MAIN = [2006, 2009, 2013, 2016, 2018, 2019, 2021]
TEST_COLUMN = ["wohngeld_basis_hh"]

# Variables for test of wohngeld with varying size.
MAX_HH_SIZE = 12
YEARS_TEST_VARYING_HH_SIZES = [2009, 2016, 2021]
MIETSTUFEN = range(1, 7)


@pytest.fixture(scope="module")
def input_data():
    return pd.read_csv(ROOT_DIR / "tests" / "test_data" / "test_dfs_wohngeld.csv")


@pytest.mark.parametrize(
    "year, column", itertools.product(YEARS_TEST_MAIN, TEST_COLUMN)
)
def test_wohngeld_main(input_data, year, column):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    columns = [
        "elterngeld_m",
        "arbeitsl_geld_m",
        "unterhaltsvors_m",
        "ertragsanteil",
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "brutto_eink_6",
        "ges_krankenv_beitr_m",
        "ges_rentenv_beitr_m",
        "kindergeld_anspruch",
        "gesamte_rente_m",
    ]
    policy_functions["eink_st_tu"] = eink_st_m_tu_from_data

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=columns,
    )
    assert_series_equal(result[column], year_data[column])


def eink_st_m_tu_from_data(eink_st_m, tu_id):
    return eink_st_m.groupby(tu_id).sum()


@pytest.fixture(scope="module")
def input_data_households():
    df = pd.DataFrame(
        data={
            "p_id": 0,
            "hh_id": np.arange(MAX_HH_SIZE + 1).repeat(np.arange(MAX_HH_SIZE + 1)),
            "tu_id": np.arange(MAX_HH_SIZE + 1).repeat(np.arange(MAX_HH_SIZE + 1)),
            "kind": False,
            "bruttokaltmiete_m_hh": 200,
            "alleinerziehend": False,
            "alter": 30,
            "immobilie_baujahr_hh": 1970,
            "kindergeld_anspruch": False,
            "bruttolohn_m": 0,
            "gesamte_rente_m": 0,
            "ertragsanteil": 0,
            "elterngeld_m": 0,
            "mietstufe": 0,
            "arbeitsl_geld_m": 0,
            "sonstig_eink_m": 0,
            "unterhaltsvors_m": 0,
            "brutto_eink_1": 0,
            "brutto_eink_4": 0,
            "brutto_eink_5": 0,
            "brutto_eink_6": 0,
            "eink_st_tu": 0,
            "ges_rentenv_beitr_m": 0,
            "ges_krankenv_beitr_m": 0,
            "behinderungsgrad": 0,
        },
    )
    df["p_id"] = df.index

    return df


@pytest.mark.parametrize(
    "year, mietstufe, column",
    itertools.product(YEARS_TEST_VARYING_HH_SIZES, MIETSTUFEN, TEST_COLUMN),
)
def test_wohngeld_varying_hh_sizes(input_data_households, year, mietstufe, column):
    policy_params, policy_functions = set_up_policy_environment(date=year)
    columns = [
        "elterngeld_m",
        "arbeitsl_geld_m",
        "unterhaltsvors_m",
        "ertragsanteil",
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "eink_st_tu",
        "brutto_eink_6",
        "ges_krankenv_beitr_m",
        "ges_rentenv_beitr_m",
        "kindergeld_anspruch",
        "gesamte_rente_m",
    ]
    input_data_households["mietstufe"] = mietstufe

    result = compute_taxes_and_transfers(
        data=input_data_households,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=columns,
    )
    assert result[column].is_monotonic
