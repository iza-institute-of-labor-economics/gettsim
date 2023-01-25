import itertools

import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests import TEST_DATA_DIR

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_m",
    "betreuungskost_m",
    "eink_selbst_m",
    "kapitaleink_brutto_m",
    "eink_vermietung_m",
    "jahr_renteneintr",
    "sum_ges_rente_priv_rente_m",
    "arbeitsstunden_w",
    "in_ausbildung",
    "kind",
    "behinderungsgrad",
    "priv_rentenv_beitr_m",
    "alleinerz",
    "alter",
    "jahr",
    "wohnort_ost",
    "selbstständig",
    "hat_kinder",
    "in_priv_krankenv",
    "geburtsjahr",
    "vorsorgeaufw_tu",
]

OUT_COLS = [
    "_zu_verst_eink_ohne_kinderfreib_tu",
    "zu_verst_eink_mit_kinderfreib_tu",
    "eink_st_kinderfreib_tu",
    "eink_st_altersfreib",
    "alleinerz_freib_tu",
    "sum_eink",
    "_eink_st_behinderungsgrad_pauschbetrag",
]
OVERRIDE_COLS = [
    "sum_ges_rente_priv_rente_m",
    "vorsorgeaufw_tu",
]
YEARS = [2010, 2015, 2017, 2018, 2019, 2020]


@pytest.fixture(scope="module")
def input_data():
    file_name = "zu_verst_eink.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year, target", itertools.product(YEARS, OUT_COLS))
def test_zu_verst_eink(
    input_data,
    year,
    target,
):
    year_data = input_data[input_data["jahr"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=target,
        columns_overriding_functions=OVERRIDE_COLS,
    )

    expected_result = year_data[target]

    assert_series_equal(
        result[target], expected_result, check_dtype=False, atol=1e-1, rtol=0
    )


def sum_test_data_tu(column, year_data):
    return (
        year_data[column]
        .groupby(year_data["tu_id"])
        .transform("sum")
        .rename(column + "_tu")
    )
