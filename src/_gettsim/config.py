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
    "kinderzuschl_eink",
    "kindergeld",
    "elterngeld",
    "ges_rente",
    "erwerbsm_rente",
    "arbeitsl_geld_2",
    "grunds_im_alter",
    "lohnst",
    "erziehungsgeld",
]

SUPPORTED_GROUPINGS = {
    "hh": {
        "name": "Haushalt",
        "description": "Individuals living together in a household in the Wohngeld"
        " sense (§5 WoGG).",
        "potentially_endogenous": False,
    },
    "wthh": {
        "name": "wohngeldrechtlicher Teilhaushalt",
        "description": "The relevant unit for Wohngeld. Members of a household for whom"
        " the Wohngeld priority check compared to Bürgergeld yields the same result"
        " ∈ {True, False}.",
        "potentially_endogenous": True,
    },
    "fg": {
        "name": "Familiengemeinschaft",
        "description": "Maximum of two generations, the relevant base unit for"
        " Bürgergeld / Arbeitslosengeld 2, before excluding children who have enough"
        " income fend for themselves.",
        "potentially_endogenous": True,
    },
    "bg": {
        "name": "Bedarfsgemeinschaft",
        "description": "Familiengemeinschaft except for children who have enough income"
        " to fend for themselves. Relevant unit for Bürgergeld / Arbeitslosengeld 2",
        "potentially_endogenous": True,
    },
    "eg": {
        "name": "Einstandsgemeinschaft / Einstandspartner",
        "description": "A couple whose members are deemed to be responsible for each"
        " other.",
        "potentially_endogenous": True,
    },
    "ehe": {
        "name": "Ehepartner",
        "description": "Couples that are either married or in a civil union.",
        "potentially_endogenous": True,
    },
    "sn": {
        "name": "Steuernummer",
        "description": "Spouses filing taxes jointly or individuals.",
        "potentially_endogenous": True,
    },
}

SUPPORTED_TIME_UNITS = {
    "y": {
        "name": "year",
    },
    "m": {
        "name": "month",
    },
    "w": {
        "name": "week",
    },
    "d": {
        "name": "day",
    },
}

DEFAULT_TARGETS = [
    "eink_st_y_sn",
    "soli_st_y_sn",
    "abgelt_st_y_sn",
    "elterngeld_m",
    "sozialv_beitr_arbeitnehmer_m",
    "ges_rentenv_beitr_arbeitnehmer_m",
    "arbeitsl_v_beitr_arbeitnehmer_m",
    "ges_krankenv_beitr_arbeitnehmer_m",
    "ges_pflegev_beitr_arbeitnehmer_m",
    "arbeitsl_geld_m",
    "kindergeld_m",
    "arbeitsl_geld_2_m_bg",
    "kinderzuschl_m_bg",
    "wohngeld_m_wthh",
    "unterhaltsvors_m",
    "grunds_im_alter_m_eg",
    "ges_rente_m",
    "erwerbsm_rente_m",
]

TYPES_INPUT_VARIABLES = {
    "hh_id": int,
    "p_id": int,
    "p_id_elternteil_1": int,
    "p_id_elternteil_2": int,
    "p_id_kindergeld_empf": int,
    "p_id_erziehgeld_empf": int,
    "p_id_ehepartner": int,
    "p_id_einstandspartner": int,
    "vermögen_bedürft": float,
    "eigenbedarf_gedeckt": bool,
    # TODO(@MImmesberger): Remove input variable eigenbedarf_gedeckt once
    # Bedarfsgemeinschaften are fully endogenous
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/763
    "gemeinsam_veranlagt": bool,
    "bruttolohn_m": float,
    "alter": int,
    "weiblich": bool,
    "selbstständig": bool,
    "wohnort_ost": bool,
    "ges_pflegev_hat_kinder": bool,
    "eink_selbst_m": float,
    "in_priv_krankenv": bool,
    "priv_rentenv_beitr_m": float,
    "elterngeld_nettoeinkommen_vorjahr_m": float,
    "elterngeld_zu_verst_eink_vorjahr_y_sn": float,
    "bruttolohn_vorj_m": float,
    "arbeitsstunden_w": float,
    "geburtsjahr": int,
    "geburtstag": int,
    "geburtsmonat": int,
    "mietstufe": int,
    "entgeltp_ost": float,
    "entgeltp_west": float,
    "kind": bool,
    "rentner": bool,
    "betreuungskost_m": float,
    "p_id_betreuungsk_träger": int,
    "kapitaleink_brutto_m": float,
    "eink_vermietung_m": float,
    "bruttokaltmiete_m_hh": float,
    "heizkosten_m_hh": float,
    "jahr_renteneintr": int,
    "monat_renteneintr": int,
    "behinderungsgrad": int,
    "wohnfläche_hh": float,
    "monate_elterngeldbezug": int,
    "elterngeld_claimed": bool,
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
    "m_arbeitsl": float,
    "m_ausbild_suche": float,
    "m_schul_ausbild": float,
    "m_geringf_beschäft": float,
    "m_alg1_übergang": float,
    "m_ersatzzeit": float,
    "m_kind_berücks_zeit": float,
    "m_pfleg_berücks_zeit": float,
    "y_pflichtbeitr_ab_40": float,
    "pflichtbeitr_8_in_10": bool,
    "arbeitsl_1y_past_585": bool,
    "vertra_arbeitsl_1997": bool,
    "vertra_arbeitsl_2006": bool,
    "höchster_bruttolohn_letzte_15_jahre_vor_rente_y": float,
    "anwartschaftszeit": bool,
    "arbeitssuchend": bool,
    "m_durchg_alg1_bezug": float,
    "sozialv_pflicht_5j": float,
    "bürgerg_bezug_vorj": bool,
    "kind_unterh_anspr_m": float,
    "kind_unterh_erhalt_m": float,
    "steuerklasse": int,
    "budgetsatz_erzieh": bool,
    "voll_erwerbsgemind": bool,
    "teilw_erwerbsgemind": bool,
}

FOREIGN_KEYS = [
    "p_id_ehepartner",
    "p_id_einstandspartner",
    "p_id_elternteil_1",
    "p_id_elternteil_2",
]
