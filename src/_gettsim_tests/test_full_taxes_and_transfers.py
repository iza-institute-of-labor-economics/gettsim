import datetime

import pytest
from _gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS, TYPES_INPUT_VARIABLES
from _gettsim.functions_loader import _convert_paths_to_import_strings, _load_functions
from _gettsim.gettsim_typing import check_series_has_expected_type
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import (
    load_functions_for_date,
)

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

OUT_COLS = [
    "eink_st_y_sn",
    "soli_st_y_sn",
    "abgelt_st_y_sn",
    "ges_rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_krankenv_beitr_m",
    "ges_pflegev_beitr_m",
    "arbeitsl_geld_m",
    "kindergeld_m",
    "arbeitsl_geld_2_m_bg",
    "kinderzuschl_m_bg",
    "wohngeld_m_hh",
    "unterhaltsvors_m_hh",
    "elterngeld_nettolohn_vorj_m"
    "zu_verst_eink_mit_kinderfreib_tu",
]

data = load_policy_test_data("full_taxes_and_transfers")


@pytest.mark.parametrize(
    "test_data",
    data.test_data,
    ids=str,
)
def test_full_taxes_and_transfers(
    test_data: PolicyTestData,
):
    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    out = OUT_COLS.copy()
    if test_data.date.year <= 2008:
        out.remove("abgelt_st_y_sn")

    compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=out,
    )


@pytest.mark.parametrize(
    "test_data",
    data.test_data,
    ids=str,
)
def test_data_types(
    test_data: PolicyTestData,
):
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    functions = _load_functions(imports)

    out = OUT_COLS.copy()
    if test_data.date.year <= 2008:
        out.remove("abgelt_st_y_sn")

    # Load all time dependent functions
    for y in range(1990, 2023):
        year_functions = load_functions_for_date(datetime.date(year=y, month=1, day=1))

    df = test_data.input_df
    policy_params, policy_functions = cached_set_up_policy_environment(
        date=test_data.date
    )

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=out,
        debug=True,
    )
    for column_name, series in result.items():
        if series.empty:
            pass
        else:
            if column_name in TYPES_INPUT_VARIABLES:
                internal_type = TYPES_INPUT_VARIABLES[column_name]
            elif column_name in functions:
                internal_type = functions[column_name].__annotations__["return"]
            elif column_name in year_functions:
                internal_type = year_functions[column_name].__annotations__["return"]
            else:
                # TODO (@hmgaudecker): Implement easy way to find out expected type of
                #     aggregated functions
                # https://github.com/iza-institute-of-labor-economics/gettsim/issues/604
                if column_name.endswith(("_sn", "_hh", "_fg", "_bg", "_eg", "_ehe")):
                    internal_type = None
                else:
                    raise ValueError(f"Column name {column_name} unknown.")
            if internal_type:
                assert check_series_has_expected_type(series, internal_type)
