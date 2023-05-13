from __future__ import annotations

import importlib
from pathlib import Path

import numpy

# Defaults
USE_JAX = False
numpy_or_jax = numpy


def set_array_backend(backend: str):
    """Set array library backend.

    backend (str): Must be in {'jax', 'numpy'}.

    """
    if backend not in {"jax", "numpy"}:
        raise ValueError(f"Backend must be in {'jax', 'numpy'} but is {backend}.")

    if backend == "jax":
        assert importlib.util.find_spec("jax") is not None, "JAX is not installed."
        global USE_JAX  # noqa: PLW0603
        global numpy_or_jax  # noqa: PLW0603
        import jax

        USE_JAX = True
        numpy_or_jax = jax.numpy
        jax.config.update("jax_platform_name", "cpu")


# Obtain the root directory of the package.
RESOURCE_DIR = Path(__file__).parent.resolve()

GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS = 20
GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS = 32

# List of paths to internal functions.
# If a path is a directory, all Python files are recursively collected from that folder.
PATHS_TO_INTERNAL_FUNCTIONS = [
    RESOURCE_DIR / "social_insurance_contributions",
    RESOURCE_DIR / "transfers",
    RESOURCE_DIR / "taxes",
    RESOURCE_DIR / "demographic_vars.py",
]

INTERNAL_PARAMS_GROUPS = [
    "eink_st",
    "eink_st_abzuege",
    "soli_st",
    "arbeitsl_geld",
    "sozialv_beitr",
    "unterhalt",
    "unterhaltsvors",
    "abgelt_st",
    "wohngeld",
    "kinderzuschl",
    "kindergeld",
    "elterngeld",
    "ges_rente",
    "arbeitsl_geld_2",
    "grunds_im_alter",
    "lohn_st",
]

SUPPORTED_GROUPINGS = {
    "hh": {
        "name": "household",
        "description": "all individuals living in the same household.",
    },
    "tu": {
        "name": "tax unit",
        "description": "one or two persons that file their taxes together.",
        "nested_by": "hh",
    },
}

DEFAULT_TARGETS = [
    "eink_st_tu",
    "soli_st_tu",
    "abgelt_st_tu",
    "sozialv_beitr_m",
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
    "vermögen_bedürft_hh": float,
    "bruttolohn_m": float,
    "alter": int,
    "weiblich": bool,
    "selbstständig": bool,
    "wohnort_ost": bool,
    "hat_kinder": bool,
    "eink_selbst_m": float,
    "in_priv_krankenv": bool,
    "priv_rentenv_beitr_m": float,
    "bruttolohn_vorj_m": float,
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
    "eink_vermietung_m": float,
    "bruttokaltmiete_m_hh": float,
    "heizkosten_m_hh": float,
    "jahr_renteneintr": int,
    "behinderungsgrad": int,
    "wohnfläche_hh": float,
    "m_elterngeld": int,
    "m_elterngeld_vat_hh": int,
    "m_elterngeld_mut_hh": int,
    "in_ausbildung": bool,
    "alleinerz": bool,
    "bewohnt_eigentum_hh": bool,
    "immobilie_baujahr_hh": int,
    "sonstig_eink_m": float,
    "grundr_entgeltp": float,
    "grundr_zeiten": int,
    "grundr_bew_zeiten": int,
    "priv_rente_m": float,
    "schwerbeh_g": bool,
    "m_pflichtbeitrag": float,
    "m_freiw_beitrag": float,
    "m_mutterschutz": float,
    "m_arbeitsunfähig": float,
    "m_krank_ab_16_bis_24": float,
    "m_arbeitslos": float,
    "m_ausbild_suche": float,
    "m_schul_ausbild": float,
    "m_geringf_beschäft": float,
    "m_alg1_übergang": float,
    "m_ersatzzeit": float,
    "m_kind_berücks_zeit": float,
    "m_pfleg_berücks_zeit": float,
    "y_pflichtbeitr_ab_40": float,
    "anwartschaftszeit": bool,
    "arbeitssuchend": bool,
    "m_durchg_alg1_bezug": float,
    "sozialv_pflicht_5j": float,
    "bürgerg_bezug_vorj": bool,
    "kind_unterh_anspr_m": float,
    "kind_unterh_erhalt_m": float,
    "steuerklasse": int,
}
