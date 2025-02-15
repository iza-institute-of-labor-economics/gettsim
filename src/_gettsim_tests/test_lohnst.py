import pytest
from pandas.testing import assert_series_equal

from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

INPUT_COLS = [
    "hh_id",
    "p_id",
    "wohnort_ost",
    "steuerklasse",
    "bruttolohn_m",
    "alter",
    "ges_pflegev_hat_kinder",
    "arbeitsstunden_w",
    "in_ausbildung",
    "ges_krankenv_zusatzbeitr_satz",
    "ges_pflegev_zusatz_kinderlos",
]

OUT_COLS = ["lohnst_m", "soli_st_lohnst_m"]

data = load_policy_test_data("lohnst")


@pytest.mark.xfail(reason="Needs renamings PR.")
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
    environment = cached_set_up_policy_environment(date=test_data.date)

    result = compute_taxes_and_transfers(
        data=df, environment=environment, targets=column
    )

    assert_series_equal(
        result[column], test_data.output_df[column], check_dtype=False, atol=2
    )


@pytest.mark.xfail(reason="Needs renamings PR.")
def test_lohnsteuer_rv_anteil():
    environment = set_up_policy_environment(2018)

    assert (
        environment.params["eink_st_abzuege"]["vorsorgepauschale_rentenv_anteil"]
        == 0.72
    )

    environment = set_up_policy_environment(2023)

    assert (
        environment.params["eink_st_abzuege"]["vorsorgepauschale_rentenv_anteil"] == 1
    )
