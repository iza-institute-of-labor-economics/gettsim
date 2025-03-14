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

QUALIFIED_NAME_SEPARATOR = "__"

# List of paths to internal functions.
# If a path is a directory, all Python files are recursively collected from that folder.
PATHS_TO_INTERNAL_FUNCTIONS = [
    RESOURCE_DIR / "transfers",
    RESOURCE_DIR / "taxes",
    RESOURCE_DIR / "demographics.py",
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
        "namespace": "demographics",
        "description": "Individuals living together in a household in the Wohngeld"
        " sense (§5 WoGG).",
        "potentially_endogenous": False,
    },
    "wthh": {
        "name": "wohngeldrechtlicher Teilhaushalt",
        "namespace": "wohngeld",
        "description": "The relevant unit for Wohngeld. Members of a household for whom"
        " the Wohngeld priority check compared to Bürgergeld yields the same result"
        " ∈ {True, False}.",
        "potentially_endogenous": True,
    },
    "fg": {
        "name": "Familiengemeinschaft",
        "namespace": "arbeitslosengeld_2",
        "description": "Maximum of two generations, the relevant base unit for"
        " Bürgergeld / Arbeitslosengeld 2, before excluding children who have enough"
        " income fend for themselves.",
        "potentially_endogenous": True,
    },
    "bg": {
        "name": "Bedarfsgemeinschaft",
        "namespace": "arbeitslosengeld_2",
        "description": "Familiengemeinschaft except for children who have enough income"
        " to fend for themselves. Relevant unit for Bürgergeld / Arbeitslosengeld 2",
        "potentially_endogenous": True,
    },
    "eg": {
        "name": "Einstandsgemeinschaft / Einstandspartner",
        "namespace": "arbeitslosengeld_2",
        "description": "A couple whose members are deemed to be responsible for each"
        " other.",
        "potentially_endogenous": True,
    },
    "ehe": {
        "name": "Ehepartner",
        "namespace": "demographics",
        "description": "Couples that are either married or in a civil union.",
        "potentially_endogenous": True,
    },
    "sn": {
        "name": "Steuernummer",
        "namespace": "einkommensteuer",
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

DEFAULT_TARGETS = {
    "einkommensteuer": {"betrag_y_sn": None},
    "solidaritätszuschlag": {"betrag_y_sn": None},
    "abgeltungssteuer": {"betrag_y_sn": None},
    "sozialversicherung": {
        "arbeitslosen": {
            "beitrag": {"betrag_arbeitnehmer_m": None},
            "betrag_m": None,
        },
        "kranken": {"beitrag": {"betrag_arbeitnehmer_m"}},
        "pflege": {"beitrag": {"betrag_arbeitnehmer_m"}},
        "rente": {
            "beitrag": {"betrag_arbeitnehmer_m"},
            "altersrente": {"betrag_m": None},
            "erwerbsminderung": {"betrag_m": None},
        },
        "beitrag_arbeitnehmer_m": None,
    },
    "elterngeld": {"betrag_m": None},
    "kindergeld": {"betrag_m": None},
    "arbeitslosengeld_2": {"betrag_m_bg": None},
    "kinderzuschlag": {"betrag_m_bg": None},
    "wohngeld": {"betrag_m_wthh": None},
    "unterhaltsvorschuss": {"betrag_m": None},
    "grundsicherung": {"im_alter": {"betrag_m_eg": None}},
}

TYPES_INPUT_VARIABLES = {
    "sozialversicherung__arbeitslosen__anwartschaftszeit": bool,
    "sozialversicherung__arbeitslosen__arbeitssuchend": bool,
    "sozialversicherung__arbeitslosen__monate_durchgängiger_bezug_von_arbeitslosengeld": float,
    "sozialversicherung__arbeitslosen__monate_sozialversicherungspflichtig_in_letzten_5_jahren": float,
    # TODO(@MImmesberger): Remove input variable eigenbedarf_gedeckt once
    # Bedarfsgemeinschaften are fully endogenous
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/763
    "arbeitslosengeld_2__eigenbedarf_gedeckt": bool,
    "arbeitslosengeld_2__arbeitslosengeld_2_bezug_im_vorjahr": bool,
    "demographics__alleinerziehend": bool,
    "demographics__alter": int,
    "demographics__arbeitsstunden_w": float,  # Temporary namespace
    "demographics__behinderungsgrad": int,
    "demographics__geburtsjahr": int,
    "demographics__geburtsmonat": int,
    "demographics__geburtstag": int,
    "demographics__hh_id": int,
    "demographics__kind": bool,
    "demographics__p_id_elternteil_1": int,
    "demographics__p_id_elternteil_2": int,
    "demographics__p_id": int,
    "demographics__vermögen": float,
    "demographics__weiblich": bool,
    "demographics__wohnort_ost": bool,
    "demographics__p_id_ehepartner": int,
    "arbeitslosengeld_2__p_id_einstandspartner": int,
    "einkommen__aus_selbstständigkeit_m": float,
    "einkommen__aus_vermietung_und_verpachtung_m": float,
    "einkommen__kapitaleinnahmen_m": float,
    "einkommen__bruttolohn_m": float,
    "einkommen__bruttolohn_vorjahr_m": float,
    "einkommen__ist_selbstständig": bool,
    "einkommen__sonstige_m": float,
    "einkommensteuer__einkommen__beitrag_private_rentenversicherung_m": float,
    "einkommensteuer__freibeträge__betreuungskosten_m": float,
    "einkommensteuer__freibeträge__p_id_betreuungskosten_träger": int,
    "einkommensteuer__gemeinsam_veranlagt": bool,
    "elterngeld__bisheriger_bezug_m": int,
    "elterngeld__claimed": bool,
    "elterngeld__nettoeinkommen_vorjahr_m": float,
    "elterngeld__zu_versteuerndes_einkommen_vorjahr_y_sn": float,
    "erziehungsgeld__budgetsatz": bool,
    "erziehungsgeld__p_id_empfänger": int,
    "kindergeld__in_ausbildung": bool,
    "kindergeld__p_id_empfänger": int,
    "lohnsteuer__steuerklasse": int,
    "sozialversicherung__rente__arbeitslosigkeitszeiten_m": float,
    "sozialversicherung__rente__arbeitsunfähigkeitszeiten_m": float,
    "sozialversicherung__rente__ausbildungssuche_m": float,
    "sozialversicherung__rente__entgeltersatzleistungen_arbeitslosigkeit_m": float,
    "sozialversicherung__rente__entgeltpunkte_ost": float,
    "sozialversicherung__rente__entgeltpunkte_west": float,
    "sozialversicherung__rente__ersatzzeiten_m": float,
    "sozialversicherung__rente__freiwillige_beitragszeiten_m": float,
    "sozialversicherung__rente__altersrente__für_frauen__jahre_pflichtbeiträge_ab_40": float,
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__pflichtbeitrag_in_8_von_10_jahren": bool,
    "sozialversicherung__rente__altersrente__höchster_bruttolohn_letzte_15_jahre_vor_rente_y": float,
    "sozialversicherung__rente__kinderberücksichtigungszeiten_m": float,
    "sozialversicherung__rente__krankheitszeiten_ab_16_bis_24_m": float,
    "sozialversicherung__rente__mutterschutzzeiten_m": float,
    "sozialversicherung__rente__pflegeberücksichtigungszeiten_m": float,
    "sozialversicherung__rente__pflichtbeitragszeiten_m": float,
    "sozialversicherung__rente__rentner": bool,
    "sozialversicherung__rente__schulausbildung_m": float,
    "demographics__schwerbehindert_grad_g": bool,
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__arbeitslos_für_1_jahr_nach_alter_58_ein_halb": bool,
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_1997": bool,
    "sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_2004": bool,
    "sozialversicherung__rente__zeiten_geringfügiger_beschäftigung_m": float,
    "sozialversicherung__rente__erwerbsminderung__teilweise_erwerbsgemindert": bool,
    "sozialversicherung__rente__erwerbsminderung__voll_erwerbsgemindert": bool,
    "sozialversicherung__rente__grundrente__bewertungszeiten_m": int,
    "sozialversicherung__rente__grundrente__entgeltpunkte": float,
    "sozialversicherung__rente__grundrente__grundrentenzeiten_m": int,
    "sozialversicherung__rente__jahr_renteneintritt": int,
    "sozialversicherung__rente__monat_renteneintritt": int,
    "sozialversicherung__rente__private_rente_m": float,
    "sozialversicherung__kranken__beitrag__privat_versichert": bool,
    "sozialversicherung__pflege__beitrag__hat_kinder": bool,
    "unterhalt__anspruch_m": float,
    "unterhalt__tatsächlich_erhaltener_betrag_m": float,
    "wohnen__bewohnt_eigentum_hh": bool,
    "wohnen__bruttokaltmiete_m_hh": float,
    "wohnen__heizkosten_m_hh": float,
    "wohnen__wohnfläche_hh": float,
    "wohnen__baujahr_immobilie_hh": int,
    "wohngeld__mietstufe": int,
}

FOREIGN_KEYS = [
    ("demographics", "p_id_ehepartner"),
    ("arbeitslosengeld_2", "p_id_einstandspartner"),
    ("demographics", "p_id_elternteil_1"),
    ("demographics", "p_id_elternteil_2"),
]
