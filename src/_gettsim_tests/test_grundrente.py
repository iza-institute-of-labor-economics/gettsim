from datetime import timedelta

import pytest
from pandas.testing import assert_series_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

YEARS = [2021]

OUT_COLS_TOL = {
    "sozialversicherung__rente__grundrente__entgeltpunkte_zuschlag": 0.0001,
    "sozialversicherung__rente__grundrente__basisbetrag_m": 1,
    "sozialversicherung__rente__grundrente__betrag_m": 1,
    "sozialversicherung__rente__altersrente__betrag_m": 1,
}
data = load_policy_test_data("grundrente")


@pytest.mark.xfail(reason="Needs renamings PR.")
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
    environment = cached_set_up_policy_environment(date=test_data.date)

    result = compute_taxes_and_transfers(
        data=df, environment=environment, targets=column
    )

    tol = OUT_COLS_TOL[column]
    assert_series_equal(
        result[column], test_data.output_df[column], check_dtype=False, atol=tol, rtol=0
    )


INPUT_COLS_INCOME = [
    "p_id",
    "hh_id",
    "demographics__alter",
    "sozialversicherung__rente__private_rente_betrag_m",
    "sozialversicherung__rente__entgeltpunkte_west",
    "sozialversicherung__rente__entgeltpunkte_ost",
    "demographics__geburtsjahr",
    "demographics__geburtsmonat",
    "sozialversicherung__rente__bezieht_rente",
    "sozialversicherung__rente__jahr_renteneintritt",
    "sozialversicherung__rente__monat_renteneintritt",
    "demographics__wohnort_ost",
    "einnahmen__bruttolohn_m",
    "sozialversicherung__rente__altersrente__rente__altersrente__höchster_bruttolohn_letzte_15_jahre_vor_rente_y",
    "demographics__weiblich",
    "sozialversicherung__rente__altersrente__für_frauen__pflichtsbeitragszeiten_ab_40_y",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__pflichtbeitragsjahre_8_von_10",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__arbeitslos_für_1_jahr_nach_alter_58_ein_halb",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_2004",
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_1997",
    "sozialversicherung__rente__pflichtbeitragszeiten_m",
    "sozialversicherung__rente__freiwillige_beitragszeiten_m",
    "sozialversicherung__rente__ersatzzeiten_m",
    "sozialversicherung__rente__schulausbildung_m",
    "sozialversicherung__rente__kinderberücksichtigungszeiten_m",
    "sozialversicherung__rente__pflegeberücksichtigungszeiten_m",
    "sozialversicherung__rente__arbeitsunfähigkeitszeiten_m",
    "sozialversicherung__rente__krankheitszeiten_ab_16_bis_24_m",
    "sozialversicherung__rente__mutterschutzzeiten_m",
    "sozialversicherung__rente__arbeitslosigkeitszeiten_m",
    "sozialversicherung__rente__ausbildungssuche_m",
    "sozialversicherung__rente__entgeltersatzleistungen_arbeitslosigkeit_m",
    "sozialversicherung__rente__zeiten_geringfügiger_beschäftigung_m",
]

data_proxy = load_policy_test_data("grundrente_proxy_rente")


@pytest.mark.xfail(reason="Needs renamings PR.")
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
    environment = cached_set_up_policy_environment(date=test_data.date)

    result = compute_taxes_and_transfers(
        data=df, environment=environment, targets=column
    )

    assert_series_equal(
        result[column].astype(float),
        test_data.output_df[column],
        check_dtype=False,
        rtol=0,
        atol=0.01,
    )


@pytest.mark.xfail(reason="Needs renamings PR.")
@pytest.mark.parametrize(
    "test_data",
    data_proxy.test_data,
    ids=str,
)
def test_proxy_rente_vorj_comparison_last_year(test_data: PolicyTestData):
    df = test_data.input_df[INPUT_COLS_INCOME].copy()
    date = test_data.date
    environment = cached_set_up_policy_environment(date)

    calc_result = compute_taxes_and_transfers(
        data=df,
        environment=environment,
        targets="sozialversicherung__rente__grundrente__proxy_rente_vorjahr_m",
    )

    # Calculate pension of last year
    environment = cached_set_up_policy_environment(date - timedelta(days=365))
    df["demographics__alter"] -= 1
    calc_result_last_year = compute_taxes_and_transfers(
        data=df,
        environment=environment,
        targets=["sozialversicherung__rente__altersrente__bruttorente_m"],
    )
    assert_series_equal(
        calc_result["sozialversicherung__rente__grundrente__proxy_rente_vorjahr_m"],
        calc_result_last_year["sozialversicherung__rente__altersrente__bruttorente_m"]
        + df["sozialversicherung__rente__private_rente_betrag_m"],
        check_names=False,
        rtol=0,
    )
