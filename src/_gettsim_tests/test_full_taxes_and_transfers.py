import datetime

import pandas as pd
import pytest
from _gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS, TYPES_INPUT_VARIABLES
from _gettsim.functions_loader import _convert_paths_to_import_strings, _load_functions
from _gettsim.gettsim_typing import check_series_has_expected_type
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import (
    load_functions_for_date,
    set_up_policy_environment,
)

from _gettsim_tests import TEST_DATA_DIR

YEARS = [2019]
INPUT_COLS = [*list(TYPES_INPUT_VARIABLES.keys()), "sum_ges_rente_priv_rente_m"]
OUT_COLS = [
    "eink_st_tu",
    "soli_st_tu",
    "abgelt_st_tu",
    "ges_rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_krankenv_beitr_m",
    "ges_pflegev_beitr_m",
    "arbeitsl_geld_m",
    "kindergeld_m_tu",
    "arbeitsl_geld_2_m_hh",
    "kinderzuschl_m_hh",
    "wohngeld_m_hh",
    "unterhaltsvors_m_hh",
]
OVERRIDE_COLS = ["sum_ges_rente_priv_rente_m"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "full_taxes_and_transfers.csv"
    out = pd.read_csv(TEST_DATA_DIR / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_full_taxes_and_transfers(
    input_data,
    year,
):
    year_data = input_data[input_data["jahr"] == year].copy()
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=OUT_COLS,
        columns_overriding_functions=OVERRIDE_COLS,
    )


@pytest.mark.parametrize("year", YEARS)
def test_data_types(
    input_data,
    year,
):
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    functions = _load_functions(imports)

    # Load all time dependent functions
    for y in range(1990, 2023):
        year_functions = load_functions_for_date(datetime.date(year=y, month=1, day=1))

    year_data = input_data[input_data["jahr"] == year].copy()
    df = year_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    data = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=OUT_COLS,
        debug=True,
        columns_overriding_functions=OVERRIDE_COLS,
    )
    for column_name, series in data.items():

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
                # ToDo: Implement easy way to find out expected type of
                # ToDo: aggregated functions
                if column_name.endswith("_tu") or column_name.endswith("_hh"):
                    internal_type = None
                else:
                    raise ValueError(f"Column name {column_name} unknown.")
            if internal_type:
                assert check_series_has_expected_type(series, internal_type)
