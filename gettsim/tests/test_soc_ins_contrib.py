import itertools

import pandas as pd
import pytest

from gettsim.apply_tax_funcs import apply_tax_transfer_func
from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.social_insurance import soc_ins_contrib

INPUT_COLS = [
    "pid",
    "hid",
    "tu_id",
    "lohn_m",
    "ostdeutsch",
    "alter",
    "selbstständig",
    "hat_kinder",
    "eink_selbstst_m",
    "rente_m",
    "prv_krank_vers",
    "year",
]


YEARS = [2002, 2010, 2018, 2019, 2020]
OUT_COLS = [
    "sozialv_beit_m",
    "rentenv_beit_m",
    "arbeitsl_beit_m",
    "krankv_beit_m",
    "pflegev_beit_m",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_ssc.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_soc_ins_contrib(input_data, year, column, soz_vers_beitr_raw_data):
    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    soz_vers_beitr_params = get_policies_for_date(
        year=year, group="soz_vers_beitr", raw_group_data=soz_vers_beitr_raw_data
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=soc_ins_contrib,
        level=["hid", "tu_id", "pid"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": soz_vers_beitr_params},
    )

    pd.testing.assert_series_equal(df[column], year_data[column])
