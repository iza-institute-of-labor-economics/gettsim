import itertools
from datetime import date

import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.soz_vers import soc_ins_contrib

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_m",
    "wohnort_ost",
    "alter",
    "selbstständig",
    "hat_kinder",
    "eink_selbstst_m",
    "ges_rente_m",
    "prv_krankv_beit_m",
    "jahr",
]


YEARS = [2002, 2010, 2018, 2019, 2020]
OUT_COLS = [
    "sozialv_beit_m",
    "rentenv_beit_m",
    "arbeitsl_v_beit_m",
    "ges_krankv_beit_m",
    "pflegev_beit_m",
]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_ssc.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_soc_ins_contrib(input_data, year, column, soz_vers_beitr_raw_data):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[INPUT_COLS].copy()
    policy_date = date(year, 1, 1)
    soz_vers_beitr_params = get_policies_for_date(
        policy_date=policy_date,
        group="soz_vers_beitr",
        raw_group_data=soz_vers_beitr_raw_data,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=soc_ins_contrib,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": soz_vers_beitr_params},
    )

    pd.testing.assert_series_equal(df[column], year_data[column])
