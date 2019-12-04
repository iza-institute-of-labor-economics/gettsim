import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.elterngeld import elt_geld
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.tax_transfer import _apply_tax_transfer_func


INPUT_COLS = [
    "hid",
    "tu_id",
    "pid",
    "m_wage",
    "elt_zeit",
    "year",
]

OUT_COLS = ["elt_geld"]
YEARS = [2017, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_eltg.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_eltgeld(year, input_data):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    elterngeld_params = get_policies_for_date(year=year, group="elterngeld")

    df = _apply_tax_transfer_func(
        df,
        tax_func=elt_geld,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": elterngeld_params},
    )

    assert_frame_equal(df[OUT_COLS].astype(int), year_data[OUT_COLS], check_dtype=False)
