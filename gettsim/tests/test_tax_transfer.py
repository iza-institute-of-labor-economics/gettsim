import datetime

import pandas as pd
import pytest

from gettsim.config import DEFAULT_TARGETS
from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.config import ROOT_DIR
from gettsim.config import STANDARD_DATA_TYPES
from gettsim.functions_loader import _convert_paths_to_import_strings
from gettsim.functions_loader import _load_functions
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import load_reforms_for_date
from gettsim.policy_environment import set_up_policy_environment
from gettsim.typing import check_if_series_has_internal_type


YEARS = [2020]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_tax_transfer(
    input_data, year,
):
    year_data = input_data[input_data["jahr"] == year].copy()
    df = year_data[list(STANDARD_DATA_TYPES.keys())].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    # params["renten_daten"] = renten_daten

    compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=DEFAULT_TARGETS,
    )


@pytest.mark.parametrize("year", YEARS)
def test_data_types(
    input_data, year,
):
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    functions = _load_functions(imports)

    # Load all time dependent functions
    for year in range(1990, 2021):
        year_functions = load_reforms_for_date(datetime.date(year=year, month=1, day=1))

    year_data = input_data[input_data["jahr"] == year].copy()
    df = year_data[list(STANDARD_DATA_TYPES.keys())].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)
    # params["renten_daten"] = renten_daten

    data = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=DEFAULT_TARGETS,
        debug=True,
    )
    for column_name, series in data.items():
        if series.empty:
            pass
        else:
            if column_name in STANDARD_DATA_TYPES:
                internal_type = STANDARD_DATA_TYPES[column_name]
            elif column_name in functions:
                internal_type = functions[column_name].__annotations__["return"]
            elif column_name in year_functions:
                internal_type = year_functions[column_name].__annotations__["return"]
            else:
                raise ValueError("Column name unknown.")
            if not check_if_series_has_internal_type(series, internal_type):
                raise AssertionError(
                    f"{column_name} has datatype {series.dtype}, but should have {internal_type}."
                )
