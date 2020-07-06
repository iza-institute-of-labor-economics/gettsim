import pandas as pd
import pytest

from gettsim.config import DEFAULT_TARGETS
from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment

REQUIRED_INPUTS = [
    "hh_id",
    "tu_id",
    "p_id",
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
    policy_params, policy_functions = set_up_policy_environment(date=year)
    # params["renten_daten"] = renten_daten

    compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=DEFAULT_TARGETS,
    )
