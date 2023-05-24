import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

# ToDo: add "wohngeld_miete_m_hh" "wohngeld_eink_m" to test data and to
# ToDo: OUT_COLS (take care of rounding)

OVERRIDE_COLS = [
    "elterngeld_m",
    "arbeitsl_geld_m",
    "rente_ertragsanteil",
    "eink_abhängig_beschäftigt",
    "eink_st_tu",
    "ges_krankenv_beitr_m",
    "ges_rentenv_beitr_m",
    "kindergeld_anspruch",
    "sum_ges_rente_priv_rente_m",
    "kapitaleink_brutto_y",
    "haushaltsgröße_hh",
    "unterhaltsvors_m",
]

data = load_policy_test_data("wohngeld")


@pytest.mark.parametrize(
    ("test_data", "column"),
    data.parametrize_args,
    ids=str,
)
def test_wohngeld(
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

    if column == "wohngeld_eink_m":
        result[column] = result[column].round(1)
    else:
        result[column] = result[column].round(2)

    assert_series_equal(
        result[column], test_data.output_df[column], check_dtype=False, atol=0, rtol=0
    )
