from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

INPUT_COLS = [
    "p_id",
    "hh_id",
    "tu_id",
    "alter",
    "jahr",
    "geburtsjahr",
    "geburtsmonat",
    "m_arbeitsunfähig",
    "m_krank_ab_16_bis_24",
    "m_mutterschutz",
    "m_arbeitslos",
    "m_ausbild_suche",
    "m_schul_ausbild",
    "m_alg1_übergang",
    "m_geringf_beschäft",
    "weiblich",
    "y_pflichtbeitr_ab_40",
    "m_pflichtbeitrag",
    "m_freiw_beitrag",
    "m_ersatzzeit",
    "m_kind_berücks_zeit",
    "m_pfleg_berücks_zeit",
]

OUT_COLS = [
    "ges_rente_regelaltersgrenze",
    "ges_rente_frauen_altersgrenze",
    "_ges_rente_langj_altersgrenze",
    "_ges_rente_besond_langj_altersgrenze",
]


def convert(path: Path):
    # Original Data Source: Seibold, A. (2021).
    # Reference points for retirement behavior:
    # Evidence from german pension discontinuities.
    # American Economic Review, 111(4), 1126-65.
    # Data: https://www.openicpsr.org/openicpsr/project/120903/version/V1/view
    # retirement ages wide.dta

    # IDs were added to the original data
    original_data = pd.read_csv(path)

    original_data.columns = original_data.columns.str.lower()

    # Rename variables to GETTSIM convention
    var_names = {
        "id": "p_id",
        "yob": "geburtsjahr",
        "mob": "geburtsmonat",
        "regsray": "Regelaltersgrenze_Jahr",
        "regsram": "Regelaltersgrenze_Monat",
        "ltsray": "Langjährig_Jahr",
        "ltsram": "Langjährig_Monat",
        "wosray": "Rente_Frauen_Jahr",
        "wosram": "Rente_Frauen_Monat",
        "vltsray": "Besonders_Langjährig_Jahr",
        "vltsram": "Besonders_Langjährig_Monat",
    }
    out = original_data[[*var_names]].rename(columns=var_names).copy()

    # Create IDs
    out["tu_id"] = out["p_id"]
    out["hh_id"] = out["p_id"]

    # Create variables needed in GETTSIM
    out["jahr"] = 2010
    out["weiblich"] = True
    out["alter"] = 60
    out["m_arbeitsunfähig"] = 0.0
    out["m_krank_ab_16_bis_24"] = 0.0
    out["m_mutterschutz"] = 0.0
    out["m_arbeitslos"] = 0.0
    out["m_ausbild_suche"] = 0.0
    out["m_schul_ausbild"] = 0.0
    out["m_alg1_übergang"] = 0.0
    out["m_geringf_beschäft"] = 0.0
    out["m_freiw_beitrag"] = 0.0
    out["m_ersatzzeit"] = 0.0
    out["m_kind_berücks_zeit"] = 0.0
    out["m_pfleg_berücks_zeit"] = 0.0
    out["ges_rente_anrechnungszeit_45"] = 0
    out["ges_rente_regelaltersgrenze"] = out["Regelaltersgrenze_Jahr"] + out[
        "Regelaltersgrenze_Monat"
    ] * (1 / 12)
    out["ges_rente_frauen_altersgrenze"] = out["Rente_Frauen_Jahr"] + out[
        "Rente_Frauen_Monat"
    ] * (1 / 12)
    out["_ges_rente_langj_altersgrenze"] = out["Langjährig_Jahr"] + out[
        "Langjährig_Monat"
    ] * (1 / 12)
    out["_ges_rente_besond_langj_altersgrenze"] = out[
        "Besonders_Langjährig_Jahr"
    ] + out["Besonders_Langjährig_Monat"] * (1 / 12)

    # assuming the months of compulsory contributions required for
    # "Besonders langjährig Versicherte"
    # since this type of pension requires the longest duration of contributions
    out["m_pflichtbeitrag"] = 540.0

    # assuming the months of compulsory contributions since the years of 40 required
    # for the pension for women
    out["y_pflichtbeitr_ab_40"] = 10.0

    # after the pension for women was abolished
    out.loc[
        np.isnan(out["ges_rente_frauen_altersgrenze"]), "ges_rente_frauen_altersgrenze"
    ] = out["ges_rente_regelaltersgrenze"]

    # before the pension for "Besonders langjährig Versicherte" was introduced
    out["geburtsdatum"] = pd.to_datetime(
        (out["geburtsjahr"] * 10000 + out["geburtsmonat"] * 100 + 1).apply(int),
        format="%Y%m%d",
    )
    relevant_date = datetime(1951, 7, 1)
    introduction_year = 2014
    introduction_month = 7
    out["year_diff"] = introduction_year - out["geburtsjahr"]
    out["month_diff"] = introduction_month - out["geburtsmonat"]
    out["total_diff"] = out["year_diff"] + out["month_diff"] * (1 / 12)
    out.loc[out["total_diff"] > 65, "total_diff"] = 65
    out.loc[out["total_diff"] <= 65, "total_diff"] = out["total_diff"]

    out.loc[
        out["geburtsdatum"] < relevant_date, "_ges_rente_besond_langj_altersgrenze"
    ] = out["total_diff"]

    out[[*INPUT_COLS, *OUT_COLS]].to_csv("renten_alter_converted.csv", index=False)
