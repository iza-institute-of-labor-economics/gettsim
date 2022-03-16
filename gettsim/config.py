from pathlib import Path

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries

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
    "in_priv_krankenv": BoolSeries,
    "priv_rentenv_beitr_m": FloatSeries,
    "bruttolohn_vorj_m": FloatSeries,
    "arbeitsl_monate_lfdj": IntSeries,
    "arbeitsl_monate_vorj": IntSeries,
    "arbeitsl_monate_v2j": IntSeries,
    "arbeitsstunden_w": FloatSeries,
    "geburtsjahr": IntSeries,
    "geburtstag": IntSeries,
    "geburtsmonat": IntSeries,
    "mietstufe": IntSeries,
    "entgeltp": FloatSeries,
    "kind": BoolSeries,
    "rentner": BoolSeries,
    "betreuungskost_m": FloatSeries,
    "kapitaleink_brutto_m": FloatSeries,
    "vermiet_eink_m": FloatSeries,
    "bruttokaltmiete_m_hh": FloatSeries,
    "heizkosten_m_hh": FloatSeries,
    "jahr_renteneintr": IntSeries,
    "behinderungsgrad": IntSeries,
    "wohnfläche_hh": IntSeries,
    "m_elterngeld": IntSeries,
    "m_elterngeld_vat": IntSeries,
    "m_elterngeld_mut": IntSeries,
    "in_ausbildung": BoolSeries,
    "alleinerz": BoolSeries,
    "bewohnt_eigentum_hh": BoolSeries,
    "immobilie_baujahr_hh": IntSeries,
    "sonstig_eink_m": FloatSeries,
    "jahr": IntSeries,
    "grundr_entgeltp": FloatSeries,
    "grundr_zeiten": IntSeries,
    "grundr_bew_zeiten": IntSeries,
    "priv_rente_m": FloatSeries,
    "schwerbeh_g": BoolSeries,
}

# =====================================================================================
# Check Available Packages
# =====================================================================================

try:
    import jax  # noqa: F401
except ImportError:
    IS_JAX_INSTALLED = False
else:
    IS_JAX_INSTALLED = True
