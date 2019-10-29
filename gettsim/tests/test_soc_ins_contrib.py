import itertools

import pandas as pd
import pytest

from gettsim.social_insurance import calc_midi_contributions
from gettsim.social_insurance import no_midi
from gettsim.social_insurance import soc_ins_contrib
from gettsim.tax_transfer import _apply_tax_transfer_func
from gettsim.tests.auxiliary_test_tax import load_tb
from gettsim.tests.auxiliary_test_tax import load_test_data

INPUT_COLUMNS = [
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


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_soc_ins_contrib(year, column):
    df = load_test_data(year, "test_dfs_ssc.ods", INPUT_COLUMNS)
    tb = load_tb(year)
    if year >= 2003:
        tb["calc_midi_contrib"] = calc_midi_contributions
    else:
        tb["calc_midi_contrib"] = no_midi
    expected = load_test_data(year, "test_dfs_ssc.ods", column)
    df = _apply_tax_transfer_func(
        df,
        tax_func=soc_ins_contrib,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLUMNS,
        out_cols=OUT_COLS,
        func_kwargs={"tb": tb},
    )
    pd.testing.assert_series_equal(df[column], expected)
