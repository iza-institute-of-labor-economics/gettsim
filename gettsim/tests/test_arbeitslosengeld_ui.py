import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.arbeitslosengeld import ui
from gettsim.config import ROOT_DIR
from gettsim.tax_transfer import _apply_tax_transfer_func
from gettsim.taxes.calc_taxes import tarif
from gettsim.tests.policy_for_date import get_policies_for_date


input_cols = [
    "pid",
    "hid",
    "tu_id",
    "m_wage_l1",
    "east",
    "child",
    "months_ue",
    "months_ue_l1",
    "months_ue_l2",
    "alg_soep",
    "m_pensions",
    "w_hours",
    "child_num_tu",
    "age",
    "year",
]
OUT_COL = "m_alg1"
years = [2010, 2011, 2015, 2019]


@pytest.fixture
def input_data():
    file_name = "test_dfs_ui.csv"
    out = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")
    return out


@pytest.mark.parametrize("year", years)
def test_ui(input_data, tax_policy_data, year):
    year_data = input_data[input_data["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    tb["tax_schedule"] = tarif
    df = _apply_tax_transfer_func(
        df,
        tax_func=ui,
        level=["hid", "tu_id", "pid"],
        in_cols=input_cols,
        out_cols=[OUT_COL],
        func_kwargs={"tb": tb},
    )
    # TODO: THis should be reviewed.
    assert_series_equal(df[OUT_COL], year_data[OUT_COL], check_less_precise=3)
