import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.pre_processing.policy_for_date import get_policies_for_date

REQUIRED_INPUTS = [
    "hh_id",
    "tu_id",
    "p_id",
    "tu_vorstand",
    "anz_minderj_hh",
    "vermögen_hh",
    "bruttolohn_m",
    "alter",
    "selbstständig",
    "wohnort_ost",
    "hat_kinder",
    "eink_selbst_m",
    "ges_rente_m",
    "prv_krankenv",
    "prv_rente_beitr_m",
    "bruttolohn_vorj_m",
    "arbeitsl_lfdj_m",
    "arbeitsl_vorj_m",
    "arbeitsl_vor2j_m",
    "arbeitsstunden_w",
    "geburtsjahr",
    "geburtstag",
    "geburtsmonat",
    "mietstufe",
    "entgeltpunkte",
    "kind",
    "rentner",
    "betreuungskost_m",
    "kapital_eink_m",
    "vermiet_eink_m",
    "kaltmiete_m_hh",
    "heizkosten_m_hh",
    "jahr_renteneintr",
    "behinderungsgrad",
    "wohnfläche_hh",
    "m_elterngeld",
    "m_elterngeld_vat",
    "m_elterngeld_mut",
    "in_ausbildung",
    "alleinerziehend",
    "bewohnt_eigentum_hh",
    "immobilie_baujahr_hh",
    "sonstig_eink_m",
    "jahr",
]
DESIRED_OUTPUTS = [
    "rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_krankenv_beitr_m",
    "pflegev_beitr_m",
    "arbeitsl_geld_m",
    # "rente_anspr_m",
    # "entgeltpunkte",
    "abgelt_st_tu",
    "soli_st_tu",
    "kindergeld_m",
    "kindergeld_m_tu",
    "eink_st_tu",
    "unterhaltsvors_m",
    "regelsatz_m_hh",
    "kost_unterk_m_hh",
    "unterhaltsvors_m_hh",
    "kinderzuschlag_m_hh",
    "wohngeld_m_hh",
    "arbeitsl_geld_2_m_hh",
    # "verfügb_eink_m",
    # "verfügb_eink_hh_m",
]

YEARS = [2019]


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
    df = year_data[REQUIRED_INPUTS].copy()
    params_dict, policy_func_dict = get_policies_for_date(
        policy_date=year, policy_groups="all"
    )
    # params_dict["renten_daten"] = renten_daten

    compute_taxes_and_transfers(
        df, targets=DESIRED_OUTPUTS, user_functions=policy_func_dict, params=params_dict
    )
