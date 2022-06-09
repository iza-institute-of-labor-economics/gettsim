import datetime

import pandas as pd
import pytest

from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.config import ROOT_DIR
from gettsim.config import TYPES_INPUT_VARIABLES
from gettsim.functions_loader import _convert_paths_to_import_strings
from gettsim.functions_loader import _load_functions
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import load_reforms_for_date
from gettsim.policy_environment import set_up_policy_environment
from gettsim.typing import check_if_series_has_internal_type


YEARS = [2019]

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


@pytest.fixture(scope="module")
def input_data():
    file_name = "full_taxes_and_transfers.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_full_taxes_and_transfers(
    input_data,
    year,
):
    year_data = input_data[input_data["jahr"] == year].copy()
    df = year_data[
        list(TYPES_INPUT_VARIABLES.keys()) + ["sum_ges_rente_priv_rente_m"]
    ].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=OUT_COLS,
        columns_overriding_functions=["sum_ges_rente_priv_rente_m"],
    )


@pytest.mark.parametrize("year", YEARS)
def test_data_types(
    input_data,
    year,
):
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    functions = _load_functions(imports)

    # Load all time dependent functions
    for year in range(1990, 2023):
        year_functions = load_reforms_for_date(datetime.date(year=year, month=1, day=1))

    year_data = input_data[input_data["jahr"] == year].copy()
    df = year_data[
        list(TYPES_INPUT_VARIABLES.keys()) + ["sum_ges_rente_priv_rente_m"]
    ].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    # params["renten_daten"] = renten_daten

    data = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=OUT_COLS,
        debug=True,
        columns_overriding_functions=["sum_ges_rente_priv_rente_m"],
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
                raise ValueError("Column name unknown.")
            if not check_if_series_has_internal_type(series, internal_type):
                raise AssertionError(
                    f"{column_name} has datatype {series.dtype}, "
                    f"but should have {internal_type}."
                )
