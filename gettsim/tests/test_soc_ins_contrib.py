import itertools

import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.social_insurance import soc_ins_contrib
from gettsim.tax_transfer import _apply_tax_transfer_func

INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "m_wage",
    "east",
    "age",
    "selfemployed",
    "haskids",
    "m_self",
    "m_pensions",
    "pkv",
    "year",
]


YEARS = [2002, 2010, 2018, 2019]
OUT_COLS = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_ssc.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_soc_ins_contrib(input_data, raw_tax_policy_data, year, column):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    tb = get_policies_for_date(year=year, tax_data_raw=raw_tax_policy_data)
    df = _apply_tax_transfer_func(
        df,
        tax_func=soc_ins_contrib,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"tb": tb},
    )
    pd.testing.assert_series_equal(df[column], year_data[column])
