from datetime import date

import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.dag import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date

YEARS = [2002, 2010, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_tax_transfer(
    input_data, year, renten_daten,
):
    df = input_data[input_data["jahr"] == year].copy()
    policy_date = date(year, 1, 1)
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=policy_date, groups="all"
    )
    params_dict["renten_daten"] = renten_daten

    outputs = [
        "rentenv_beitr_m",
        "arbeitsl_v_beitr_m",
        "ges_krankenv_beitr_m",
        "pflegev_beitr_m",
        "arbeitsl_geld_m",
        "rente_anspr_m",
        "entgeltpunkte",
        "abgelt_st_m",
        "soli_st_m",
        "soli_st_m_tu",
        "kindergeld_m",
        "kindergeld_m_tu",
        "eink_st_m",
        "eink_st_m_tu",
        "unterhaltsvors_m",
        "regelsatz_m",
        "kost_unterk_m",
        "unterhaltsvors_m_hh",
        "kinderzuschlag_m",
        "wohngeld_m",
        "arbeitsl_geld_2_m",
    ]
    compute_taxes_and_transfers(
        df, targets=outputs, user_functions=policy_func_dict, params=params_dict
    )
