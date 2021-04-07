from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grundsicherung_m_hh(
    grundsicherung_m_minus_eink_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    kinderzuschlag_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschlag_vorrang_hh: BoolSeries,
    regelaltersgrenze: FloatSeries,
    alter: IntSeries,
    anz_erwachsene_hh: IntSeries,
    anz_rentner_hh: IntSeries,
) -> FloatSeries:
    """Calculate Grundsicherung im Alter on household level.

    Parameters
    ----------
    grundsicherung_m_minus_eink_hh
        See :func:`grundsicherung_m_minus_eink_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    kinderzuschlag_vorrang_hh
        See :func:`kinderzuschlag_vorrang_hh`.
    wohngeld_kinderzuschlag_vorrang_hh
        See :func:`wohngeld_kinderzuschlag_vorrang_hh`.
    regelaltersgrenze
        See :func:`regelaltersgrenze`.
    alter
        See basic input variable :ref:`alter <alter>`.
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.
    Returns
    -------

    """
    out = grundsicherung_m_minus_eink_hh.clip(lower=0)
    cond = (
        wohngeld_vorrang_hh
        | kinderzuschlag_vorrang_hh
        | wohngeld_kinderzuschlag_vorrang_hh
        | (alter < regelaltersgrenze)
        | (anz_erwachsene_hh != anz_rentner_hh)
    )
    out.loc[cond] = 0
    return out


def grundsicherung_m_minus_eink_hh(
    regelbedarf_m_grundsicherung_vermögens_check_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    grundsicherung_eink_hh: FloatSeries,
) -> FloatSeries:
    """Calculate remaining basic subsistence after recieving other benefits.

    Parameters
    ----------
    regelbedarf_m_grundsicherung_vermögens_check_hh
        See :func:`regelbedarf_m_grundsicherung_vermögens_check_hh`.
    kindergeld_m_hh
        See :func:`kindergeld_m_hh`.
    unterhaltsvors_m_hh
        See :func:`unterhaltsvors_m_hh`.
    grundsicherung_eink_hh
        See :func:`grundsicherung_eink_hh`.

    Returns
    -------

    """
    out = (
        regelbedarf_m_grundsicherung_vermögens_check_hh
        - grundsicherung_eink_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return out


def grundsicherung_eink_hh(
    grundsicherung_eink: FloatSeries, hh_id: IntSeries
) -> FloatSeries:
    """Sum up income for calculation of Grundsicherung im Alter per household.

    Parameters
    ----------
    grundsicherung_eink
        See :func:`grundsicherung_eink`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return grundsicherung_eink.groupby(hh_id).sum()


def grundsicherung_eink(
    arbeitsl_geld_2_brutto_eink: FloatSeries,
    eink_st_tu: FloatSeries,
    tu_id: IntSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_m: FloatSeries,
    eink_anr_frei_grundsicherung: FloatSeries,
    freibetrag_grundsicherung_grundrente: FloatSeries,
    freibetrag_prv_rente: FloatSeries,
) -> FloatSeries:
    """Sum up income for calculation of Grundsicherung im Alter.

    Parameters
    ----------
    arbeitsl_geld_2_brutto_eink
        See :func:`arbeitsl_geld_2_brutto_eink`.
    eink_st_tu
        See :func:`eink_st_tu`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    soli_st_tu
        See :func:`soli_st_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.
    eink_anr_frei_grundsicherung
        See :func:`eink_anr_frei_grundsicherung`.
    freibetrag_grundsicherung_grundrente
        See :func:`freibetrag_grundsicherung_grundrente`.
    freibetrag_prv_rente
        See :func:`freibetrag_prv_rente`.

    Returns
    -------

    """
    return (
        arbeitsl_geld_2_brutto_eink
        - tu_id.replace((eink_st_tu / anz_erwachsene_tu) / 12)
        - tu_id.replace((soli_st_tu / anz_erwachsene_tu) / 12)
        - sozialv_beitr_m
        - eink_anr_frei_grundsicherung
        - freibetrag_grundsicherung_grundrente
        - freibetrag_prv_rente
    ).clip(lower=0)


def eink_anr_frei_grundsicherung(
    bruttolohn_m: FloatSeries, arbeitsl_geld_2_params: dict
) -> FloatSeries:
    """Calculate income not considered for amount of Grundsicherung im Alter.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = (bruttolohn_m * 0.3).clip(upper=0.5 * arbeitsl_geld_2_params["regelsatz"][1])

    return out


def freibetrag_prv_rente(
    prv_rente_m: FloatSeries, arbeitsl_geld_2_params: dict
) -> FloatSeries:
    """Calculate allowance for private pensions.

    Parameters
    ----------
    prv_rente_m
        See basic input variable :ref:`prv_rente_m <prv_rente_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = (prv_rente_m.clip(upper=100) + (prv_rente_m - 100).clip(lower=0) * 0.3).clip(
        upper=0.5 * arbeitsl_geld_2_params["regelsatz"][1]
    )
    return out


def regelbedarf_m_grundsicherung_vermögens_check_hh(
    regelbedarf_m_hh: FloatSeries,
    unter_vermögens_freibetrag_grundsicherung_hh: BoolSeries,
) -> FloatSeries:
    """Set preliminary basic subsistence to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    regelbedarf_m_hh
        See :func:`regelbedarf_m_hh`.
    unter_vermögens_freibetrag_grundsicherung_hh
        See :func:`unter_vermögens_freibetrag_grundsicherung_hh`.

    Returns
    -------

    """
    out = regelbedarf_m_hh
    out.loc[~unter_vermögens_freibetrag_grundsicherung_hh] = 0
    return out


def unter_vermögens_freibetrag_grundsicherung_hh(
    vermögen_hh: FloatSeries, freibetrag_vermögen_grundsicherung_hh: FloatSeries
) -> BoolSeries:
    """Check if capital of household is below limit of Grundsicherung im Alter.

    Parameters
    ----------
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.
    freibetrag_vermögen_grundsicherung_hh
       See :func:`freibetrag_vermögen_grundsicherung_hh`.

    Returns
    -------

    """
    return vermögen_hh < freibetrag_vermögen_grundsicherung_hh


def freibetrag_vermögen_grundsicherung_hh(
    haushaltsgröße_hh: IntSeries, ges_renten_vers_params: dict
) -> FloatSeries:
    """Calculate maximum capital allowed for Grundsicherung im Alter.

    Parameters
    ----------
    haushaltsgröße
        See :func:`haushaltsgröße`.

    Returns
    -------

    """
    out = ges_renten_vers_params["schonvermögen_grundsicherung"] * haushaltsgröße_hh
    return out
