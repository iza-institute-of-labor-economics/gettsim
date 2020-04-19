import itertools

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.taxes.zve import zve


IN_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "bruttolohn_m",
    "betreuungskost_m",
    "eink_selbstst_m",
    "kapital_eink_m",
    "vermiet_eink_m",
    "jahr_renteneintr",
    "ges_rente_m",
    "arbeitsstunden_w",
    "in_ausbildung",
    "gem_veranlagt",
    "kind",
    "behinderungsgrad",
    "rentenv_beit_m",
    "prv_rente_beit_m",
    "arbeitsl_v_beit_m",
    "pflegev_beit_m",
    "alleinerziehend",
    "alter",
    "anz_kinder_tu",
    "jahr",
    "wohnort_ost",
    "ges_krankv_beit_m",
]
OUT_COLS = [
    "_zu_versteuerndes_eink_kein_kind_freib",
    "_zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib",
    "_zu_versteuerndes_eink_kind_freib",
    "_zu_versteuerndes_eink_abgelt_st_m_kind_freib",
    "kind_freib",
    "brutto_eink_1",
    "brutto_eink_4",
    "brutto_eink_5",
    "brutto_eink_6",
    "brutto_eink_7",
    "brutto_eink_1_tu",
    "brutto_eink_4_tu",
    "brutto_eink_5_tu",
    "brutto_eink_6_tu",
    "brutto_eink_7_tu",
    "_ertragsanteil",
    "sonder",
    "hh_freib",
    "altersfreib",
    "vorsorge",
]

TEST_COLS = [
    "_zu_versteuerndes_eink_kein_kind_freib",
    "_zu_versteuerndes_eink_kind_freib",
    "altersfreib",
]
YEARS = [2005, 2009, 2010, 2012, 2018]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_zve.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLS))
def test_zve(
    input_data,
    year,
    column,
    kindergeld_raw_data,
    soz_vers_beitr_raw_data,
    eink_st_abzuege_raw_data,
):
    year_data = input_data[input_data["jahr"] == year]
    df = year_data[IN_COLS].copy()
    eink_st_abzuege_params = get_policies_for_date(
        year=year, group="eink_st_abzuege", raw_group_data=eink_st_abzuege_raw_data
    )
    soz_vers_beitr_params = get_policies_for_date(
        year=year, group="soz_vers_beitr", raw_group_data=soz_vers_beitr_raw_data
    )
    kindergeld_params = get_policies_for_date(
        year=year, group="kindergeld", raw_group_data=kindergeld_raw_data
    )

    for col in OUT_COLS:
        df[col] = np.nan
    df = df.groupby(["hh_id", "tu_id"]).apply(
        zve,
        eink_st_abzuege_params=eink_st_abzuege_params,
        soz_vers_beitr_params=soz_vers_beitr_params,
        kindergeld_params=kindergeld_params,
    )

    assert_series_equal(
        df[column], year_data[column], check_less_precise=2, check_dtype=False
    )
