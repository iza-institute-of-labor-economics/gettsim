from datetime import timedelta

import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

YEARS = [2021]

OUT_COLS_TOL = {
    "grundr_zuschlag_bonus_entgeltp": 0.0001,
    "grundr_zuschlag_vor_eink_anr_m": 1,
    "grundr_zuschlag_m": 1,
    "ges_rente_m": 1,
}
data = load_policy_test_data("grundrente")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_grundrente(
    test_data: PolicyTestData,
    column: str,
):
    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    result = compute_taxes_and_transfers(
        data=df, params=policy_params, functions=policy_functions, targets=column
    )

    tol = OUT_COLS_TOL[column]
    assert_series_equal(
        result[column], test_data.output_df[column], check_dtype=False, atol=tol, rtol=0
    )


INPUT_COLS_INCOME = [
    "p_id",
    "tu_id",
    "hh_id",
    "alter",
    "priv_rente_m",
    "entgeltp",
    "geburtsjahr",
    "geburtsmonat",
    "rentner",
    "jahr_renteneintr",
    "monat_renteneintr",
    "wohnort_ost",
    "bruttolohn_m",
    "weiblich",
    "y_pflichtbeitr_ab_40",
    "pflichtbeitr_8_in_10",
    "arbeitsl_1y_past_585",
    "vertrauenss_arbeitsl",
    "m_pflichtbeitrag",
    "m_freiw_beitrag",
    "m_ersatzzeit",
    "m_schul_ausbild",
    "m_kind_berücks_zeit",
    "m_pfleg_berücks_zeit",
    "m_arbeitsunfähig",
    "m_krank_ab_16_bis_24",
    "m_mutterschutz",
    "m_arbeitsl",
    "m_ausbild_suche",
    "m_alg1_übergang",
    "m_geringf_beschäft",
]

data_proxy = load_policy_test_data("grundrente_proxy_rente")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data_proxy.parametrize_args,
    ids=str,
)
def test_proxy_rente_vorj(
    test_data: PolicyTestData,
    column: str,
):
    df = test_data.input_df[INPUT_COLS_INCOME]
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    result = compute_taxes_and_transfers(
        data=df, params=policy_params, functions=policy_functions, targets=column
    )

    assert_series_equal(
        result[column].astype(float),
        test_data.output_df[column],
        check_dtype=False,
        rtol=0,
        atol=0.01,
    )


@pytest.mark.parametrize(
    "test_data",
    data_proxy.test_data,
    ids=str,
)
def test_proxy_rente_vorj_comparison_last_year(test_data: PolicyTestData):
    df = test_data.input_df[INPUT_COLS_INCOME].copy()
    date = test_data.date
    policy_params, policy_functions = cached_set_up_policy_environment(date)

    calc_result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets="rente_vorj_vor_grundr_proxy_m",
    )

    # Calculate pension of last year
    policy_params, policy_functions = cached_set_up_policy_environment(
        date - timedelta(days=365)
    )
    df["alter"] -= 1
    calc_result_last_year = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=["ges_rente_vor_grundr_m"],
    )
    assert_series_equal(
        calc_result["rente_vorj_vor_grundr_proxy_m"],
        calc_result_last_year["ges_rente_vor_grundr_m"] + df["priv_rente_m"],
        check_names=False,
        rtol=0,
    )
