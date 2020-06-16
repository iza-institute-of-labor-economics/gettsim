from pathlib import Path

# Obtain the root directory of the package. Do not import gettsim which creates a
# circular import.
ROOT_DIR = Path(__file__).parent

GEP_1_CHARACTER_LIMIT = 17

INTERNAL_FUNCTION_FILES = [
    ROOT_DIR / "soz_vers",
    ROOT_DIR / "benefits",
    ROOT_DIR / "taxes",
    ROOT_DIR / "demographic_vars.py",
]

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
