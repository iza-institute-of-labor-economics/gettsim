import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "wohnort_ost",
    "steuerklasse",
    "bruttolohn_m",
    "alter",
    "hat_kinder",
    "arbeitsstunden_w",
    "in_ausbildung",
    "ges_krankenv_zusatzbeitr_satz",
    "ges_pflegev_zusatz_kinderlos",
]

OUT_COLS = [
    "lohnst_m",
    # "soli_st_lohnst_m"
]

OVERRIDE_COLS = [
    "ges_krankenv_zusatzbeitr_satz",
    "ges_pflegev_zusatz_kinderlos",
]

YEARS = [2022]

data = load_policy_test_data("lohn_st")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_lohnsteuer(
    test_data: PolicyTestData,
    column: str,
):
    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=OVERRIDE_COLS,
    )
    assert_series_equal(
        result[column], test_data.output_df[column], check_dtype=False, atol=2
    )


def test_lohnsteuer_rv_anteil():
    policy_params, policy_functions = set_up_policy_environment(2018)

    assert policy_params["eink_st_abzuege"]["vorsorgepauschale_rv_anteil"] == 0.72

    policy_params, policy_functions = set_up_policy_environment(2023)

    assert policy_params["eink_st_abzuege"]["vorsorgepauschale_rv_anteil"] == 1
