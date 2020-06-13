from pathlib import Path

# Obtain the root directory of the package. Do not import gettsim which creates a
# circular import.
ROOT_DIR = Path(__file__).parent

GEP_1_CHARACTER_LIMIT = 17

PATHS_TO_INTERNAL_FUNCTIONS = [
    ROOT_DIR / "soz_vers",
    ROOT_DIR / "benefits",
    ROOT_DIR / "taxes",
    ROOT_DIR / "demographic_vars.py",
    ROOT_DIR / "renten_anspruch_dag.py
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
]

ORDER_OF_IDS = {"hh_id": 0, "tu_id": 1, "p_id": 2}

DEFAULT_TARGETS = [
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
