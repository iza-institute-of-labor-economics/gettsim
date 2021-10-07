from pathlib import Path

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries

# Obtain the root directory of the package. Do not import gettsim which creates a
# circular import.
ROOT_DIR = Path(__file__).parent

GEP_1_CHARACTER_LIMIT = 17

PATHS_TO_INTERNAL_FUNCTIONS = [
    ROOT_DIR / "social_insurance_payments",
    ROOT_DIR / "transfers",
    ROOT_DIR / "taxes",
    ROOT_DIR / "demographic_vars.py",
]
"""list of Paths: List of paths to internal functions.

If a path is a directory, all Python files are recursively collected from that folder.

"""

INTERNAL_PARAM_GROUPS = [
    "eink_st",
    "eink_st_abzuege",
    "soli_st",
    "arbeitsl_geld_2",
    "arbeitsl_geld",
    "soz_vers_beitr",
    "unterhalt",
    "abgelt_st",
    "wohngeld",
    "kinderzuschlag",
    "kindergeld",
    "elterngeld",
    "ges_renten_vers",
]

ORDER_OF_IDS = {"hh_id": 0, "tu_id": 1, "p_id": 2}

DEFAULT_TARGETS = [
    "rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_krankenv_beitr_m",
    "pflegev_beitr_m",
    "arbeitsl_geld_m",
    "rente_anspr_m",
    "entgeltpunkte_update",
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

STANDARD_DATA_TYPES = {
    "hh_id": IntSeries,
    "tu_id": IntSeries,
    "p_id": IntSeries,
    "vermögen_hh": FloatSeries,
    "bruttolohn_m": FloatSeries,
    "alter": IntSeries,
    "selbstständig": BoolSeries,
    "wohnort_ost": BoolSeries,
    "hat_kinder": BoolSeries,
    "eink_selbst_m": FloatSeries,
    "ges_rente_m": FloatSeries,
    "prv_krankenv": BoolSeries,
    "prv_rente_beitr_m": FloatSeries,
    "bruttolohn_vorj_m": FloatSeries,
    "arbeitsl_lfdj_m": IntSeries,
    "arbeitsl_vorj_m": IntSeries,
    "arbeitsl_vor2j_m": IntSeries,
    "arbeitsstunden_w": FloatSeries,
    "geburtsjahr": IntSeries,
    "geburtstag": IntSeries,
    "geburtsmonat": IntSeries,
    "mietstufe": IntSeries,
    "entgeltpunkte": FloatSeries,
    "kind": BoolSeries,
    "rentner": BoolSeries,
    "betreuungskost_m": FloatSeries,
    "kapital_eink_m": FloatSeries,
    "vermiet_eink_m": FloatSeries,
    "kaltmiete_m_hh": FloatSeries,
    "heizkosten_m_hh": FloatSeries,
    "jahr_renteneintr": IntSeries,
    "behinderungsgrad": IntSeries,
    "wohnfläche_hh": IntSeries,
    "m_elterngeld": IntSeries,
    "m_elterngeld_vat": IntSeries,
    "m_elterngeld_mut": IntSeries,
    "in_ausbildung": BoolSeries,
    "alleinerziehend": BoolSeries,
    "bewohnt_eigentum_hh": BoolSeries,
    "immobilie_baujahr_hh": IntSeries,
    "sonstig_eink_m": FloatSeries,
    "jahr": IntSeries,
}
