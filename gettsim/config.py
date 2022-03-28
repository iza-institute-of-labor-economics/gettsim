from pathlib import Path


# Obtain the root directory of the package. Do not import gettsim which creates a
# circular import.
ROOT_DIR = Path(__file__).parent

GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS = 20
GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS = 32

PATHS_TO_INTERNAL_FUNCTIONS = [
    ROOT_DIR / "social_insurance_contributions",
    ROOT_DIR / "transfers",
    ROOT_DIR / "taxes",
    ROOT_DIR / "demographic_vars.py",
]
"""list of Paths: List of paths to internal functions.

If a path is a directory, all Python files are recursively collected from that folder.

"""

INTERNAL_PARAM_GROUPS = [
    "eink_st",
    "eink_st_abzüge",
    "soli_st",
    "arbeitsl_geld",
    "soz_vers_beitr",
    "unterhalt",
    "abgelt_st",
    "wohngeld",
    "kinderzuschl",
    "kindergeld",
    "elterngeld",
    "ges_rente",
    "arbeitsl_geld_2",
    "grunds_im_alter",
]

ORDER_OF_IDS = {"hh_id": 0, "tu_id": 1, "p_id": 2}

DEFAULT_TARGETS = [
    "eink_st_tu",
    "soli_st_tu",
    "abgelt_st_tu",
    "ges_rentenv_beitr_m",
    "arbeitsl_v_beitr_m",
    "ges_krankenv_beitr_m",
    "ges_pflegev_beitr_m",
    "arbeitsl_geld_m",
    "kindergeld_m_tu",
    "arbeitsl_geld_2_m_hh",
    "kinderzuschl_m_hh",
    "wohngeld_m_hh",
    "unterhaltsvors_m_hh",
    "grunds_im_alter_m_hh",
    "ges_rente_m",
]

TYPES_INPUT_VARIABLES = {
    "hh_id": int,
    "tu_id": int,
    "p_id": int,
    "vermögen_hh": float,
    "bruttolohn_m": float,
    "alter": int,
    "selbstständig": bool,
    "wohnort_ost": bool,
    "hat_kinder": bool,
    "eink_selbst_m": float,
    "in_priv_krankenv": bool,
    "priv_rentenv_beitr_m": float,
    "bruttolohn_vorj_m": float,
    "arbeitsl_monate_lfdj": int,
    "arbeitsl_monate_vorj": int,
    "arbeitsl_monate_v2j": int,
    "arbeitsstunden_w": float,
    "geburtsjahr": int,
    "geburtstag": int,
    "geburtsmonat": int,
    "mietstufe": int,
    "entgeltp": float,
    "kind": bool,
    "rentner": bool,
    "betreuungskost_m": float,
    "kapitaleink_brutto_m": float,
    "vermiet_eink_m": float,
    "bruttokaltmiete_m_hh": float,
    "heizkosten_m_hh": float,
    "jahr_renteneintr": int,
    "behinderungsgrad": int,
    "wohnfläche_hh": int,
    "m_elterngeld": int,
    "m_elterngeld_vat_hh": int,
    "m_elterngeld_mut_hh": int,
    "in_ausbildung": bool,
    "alleinerz": bool,
    "bewohnt_eigentum_hh": bool,
    "immobilie_baujahr_hh": int,
    "sonstig_eink_m": float,
    "jahr": int,
    "grundr_entgeltp": float,
    "grundr_zeiten": int,
    "grundr_bew_zeiten": int,
    "priv_rente_m": float,
    "schwerbeh_g": bool,
}

# =====================================================================================
# Check Available Packages
# =====================================================================================

USE_JAX = False
