from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries


def freibetrag_vermögen_grundsicherung_hh(haushaltsgröße_hh):
    out = 5000 * haushaltsgröße_hh
    return out


def unter_vermögens_freibetrag_grundsicherung_hh(
    vermögen_hh, freibetrag_vermögen_grundsicherung_hh
):
    return vermögen_hh < freibetrag_vermögen_grundsicherung_hh


def regelbedarf_m_grundsicherung_vermögens_check_hh(
    regelbedarf_m_hh: FloatSeries,
    unter_vermögens_freibetrag_grundsicherung_hh: BoolSeries,
) -> FloatSeries:

    out = regelbedarf_m_hh
    out.loc[~unter_vermögens_freibetrag_grundsicherung_hh] = 0
    return out


def grundsicherung_m_minus_eink_hh(
    regelbedarf_m_grundsicherung_vermögens_check_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    arbeitsl_geld_2_eink_hh: FloatSeries,
) -> FloatSeries:

    out = (
        regelbedarf_m_grundsicherung_vermögens_check_hh
        - arbeitsl_geld_2_eink_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return out


def grundsicherung_m_hh(
    grundsicherung_m_minus_eink_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    kinderzuschlag_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschlag_vorrang_hh: BoolSeries,
    regelaltersgrenze,
    alter,
) -> FloatSeries:

    out = grundsicherung_m_minus_eink_hh.clip(lower=0)
    cond = (
        wohngeld_vorrang_hh
        | kinderzuschlag_vorrang_hh
        | wohngeld_kinderzuschlag_vorrang_hh
        | (alter < regelaltersgrenze)
    )
    out.loc[cond] = 0
    return out
