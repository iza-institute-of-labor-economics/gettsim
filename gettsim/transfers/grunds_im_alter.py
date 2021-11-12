import pandas as pd
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grunds_im_alter_m_hh(
    grunds_ia_m_minus_eink_hh: FloatSeries,
    anz_erwachsene_hh: IntSeries,
    anz_rentner_hh: IntSeries,
) -> FloatSeries:
    """Calculate Grundsicherung im Alter on household level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    currently not implemented for retirees.

    Parameters
    ----------
    grunds_ia_m_minus_eink_hh
        See :func:`grunds_ia_m_minus_eink_hh`.

    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.
    Returns
    -------

    """
    out = grunds_ia_m_minus_eink_hh.clip(lower=0)
    cond = anz_erwachsene_hh != anz_rentner_hh
    out.loc[cond] = 0
    return out


def grunds_ia_m_minus_eink_hh(
    regelbedarf_m_grunds_ia_vermögens_check_hh: FloatSeries,
    mehrbedarf_behinderung_m_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    anrechenbares_eink_grunds_ia_m_hh: FloatSeries,
) -> FloatSeries:
    """Calculate remaining basic subsistence after recieving other benefits.

    Parameters
    ----------
    regelbedarf_m_grunds_ia_vermögens_check_hh
        See :func:`regelbedarf_m_grunds_ia_vermögens_check_hh`.
    mehrbedarf_behinderung_m_hh
        See :func:`mehrbedarf_behinderung_m_hh`.
    kindergeld_m_hh
        See :func:`kindergeld_m_hh`.
    unterhaltsvors_m_hh
        See :func:`unterhaltsvors_m_hh`.
    anrechenbares_eink_grunds_ia_m_hh
        See :func:`anrechenbares_eink_grunds_ia_m_hh`.

    Returns
    -------

    """
    out = (
        regelbedarf_m_grunds_ia_vermögens_check_hh
        + mehrbedarf_behinderung_m_hh
        - anrechenbares_eink_grunds_ia_m_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return out


def anrechenbares_eink_grunds_ia_m_hh(
    anrechenbares_eink_grunds_ia_m: FloatSeries, hh_id: IntSeries
) -> FloatSeries:
    """Aggregate income relevant for Grundsicherung on household level.

    Parameters
    ----------
    anrechenbares_eink_grunds_ia_m
        See :func:`anrechenbares_eink_grunds_ia_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return anrechenbares_eink_grunds_ia_m.groupby(hh_id).sum()


def anrechenbares_eink_grunds_ia_m(
    anrechenbares_erwerbs_eink_grunds_ia_m: FloatSeries,
    anrechenbare_prv_rente_grunds_ia_m: FloatSeries,
    sonstig_eink_m: FloatSeries,
    vermiet_eink_m: FloatSeries,
    kapital_eink_minus_pauschbetr: FloatSeries,
    elterngeld_m: FloatSeries,
    eink_st_tu: FloatSeries,
    tu_id: IntSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_m: FloatSeries,
    staatl_rente_m: FloatSeries,
) -> FloatSeries:
    """Calculate income relevant for Grundsicherung of Grundsicherung im Alter.

    Parameters
    ----------
    grunds_ia_eink_excl_pensions
        See :func:`grunds_ia_eink_excl_pensions`.
    kapital_eink_minus_pauschbetr
        See :func:`grunds_ia_eink_excl_pensions`.
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
    grunds_ia_eink_anr_frei
        See :func:`grunds_ia_eink_anr_frei`.
    freibetrag_grunds_ia_grundr
        See :func:`freibetrag_grunds_ia_grundr`.
    freibetrag_prv_rente
        See :func:`freibetrag_prv_rente`.

    Returns
    -------

    """

    # Consider Elterngeld that is larger than 300
    anrechenbares_elterngeld_m = (elterngeld_m - 300).clip(lower=0)

    # Income
    total_income = (
        anrechenbares_erwerbs_eink_grunds_ia_m
        + staatl_rente_m
        + anrechenbare_prv_rente_grunds_ia_m
        + sonstig_eink_m
        + vermiet_eink_m
        + kapital_eink_minus_pauschbetr / 12
        + anrechenbares_elterngeld_m
    )

    # subtract taxes and social security contributions
    out = (
        total_income
        - tu_id.replace((eink_st_tu / anz_erwachsene_tu) / 12)
        - tu_id.replace((soli_st_tu / anz_erwachsene_tu) / 12)
        - sozialv_beitr_m
    ).clip(lower=0)

    return out


def anrechenbares_erwerbs_eink_grunds_ia_m(
    bruttolohn_m: FloatSeries, eink_selbst_m: FloatSeries, arbeitsl_geld_2_params: dict
) -> FloatSeries:
    """Calculate earnings relevant for Grundsicherung of Grundsicherung im Alter.

    Note: Freibeträge for income are currently not considered

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    earnings = bruttolohn_m + eink_selbst_m

    # Can deduct 30% of earnings (but no more than 1/2 of regelbedarf)
    earnings_after_max_deduction = earnings - arbeitsl_geld_2_params["regelsatz"][1] / 2
    earnings = (0.7 * earnings).clip(lower=earnings_after_max_deduction)

    return earnings


def anrechenbare_prv_rente_grunds_ia_m(
    prv_rente_m: FloatSeries, arbeitsl_geld_2_params: dict
) -> FloatSeries:
    """Calculate private pension earnings relevant for Grundsicherung of Grundsicherung
    im Alter.

    Parameters
    ----------
    prv_rente_m
        See basic input variable :ref:`prv_rente_m <prv_rente_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Can deduct 100 € of private pension completely
    prv_rente_above_100 = (prv_rente_m - 100).clip(lower=0)

    # Can deduct 30% of private pension above 100 (but no more than 1/2 of regelbedarf)
    prv_rente_after_max_deduction = (
        prv_rente_above_100 - arbeitsl_geld_2_params["regelsatz"][1] / 2
    )
    out = (0.7 * prv_rente_above_100).clip(lower=prv_rente_after_max_deduction)
    return out

def mehrbedarf_behinderung_m_hh(
    mehrbedarf_behinderung_m: FloatSeries, 
    hh_id: IntSeries,
) -> FloatSeries:
    """Aggregate mehrbedarf for people with disabilities on household level.

    Parameters
    ----------
    mehrbedarf_behinderung_m
        See :func:`mehrbedarf_behinderung_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    Returns
    -------

    """
    return mehrbedarf_behinderung_m.groupby(hh_id).sum()

def mehrbedarf_behinderung_m(
    behinderungsgrad: IntSeries, 
    rented_or_owned: object,
    hhsize_tu: IntSeries,
    ges_renten_vers_params: dict,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate mehrbedarf for people with disabilities.
    
    Parameters
    ----------
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    rented_or_owned
        See basic input variable :ref:`rented_or_owned <rented_or_owned>`.
    hhsize_tu
    See basic input variable :ref:`hhsize_tu <hhsize_tu>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    Returns
    -------

    """
    out = pd.Series(0,index=behinderungsgrad.index, dtype=float)

    # mehrbedarf for disabilities is the rate times the regelsatz for the person getting the mehrbedarf
    bedarf1 = (arbeitsl_geld_2_params["regelsatz"][1]) * (ges_renten_vers_params["mehrbedarf_g"]["rate"])
    bedarf2 = (arbeitsl_geld_2_params["regelsatz"][2]) * (ges_renten_vers_params["mehrbedarf_g"]["rate"])
    bedarf3 = (arbeitsl_geld_2_params["regelsatz"][3]) * (ges_renten_vers_params["mehrbedarf_g"]["rate"])

    # singles not living in einrichtungen
    out.loc[(behinderungsgrad >= ges_renten_vers_params["mehrbedarf_g_grenze"]["lower_threshold"]) & (
        rented_or_owned != 'Heimbewohner oder Gemeinschaftsunterkunft'
    )] = bedarf1
    # couples not living in einrichtungen
    out.loc[(behinderungsgrad >= ges_renten_vers_params["mehrbedarf_g_grenze"]["lower_threshold"]) & (
        rented_or_owned != 'Heimbewohner oder Gemeinschaftsunterkunft') & (
        hhsize_tu != 1
    )] = bedarf2
    # people in einrichtungen
    out.loc[(behinderungsgrad >= ges_renten_vers_params["mehrbedarf_g_grenze"]["lower_threshold"]) & (
        rented_or_owned == 'Heimbewohner oder Gemeinschaftsunterkunft'
    )] = bedarf3
    

    return out


def regelbedarf_m_grunds_ia_vermögens_check_hh(
    regelbedarf_m_hh: FloatSeries, unter_vermögens_freibetrag_grunds_ia_hh: BoolSeries,
) -> FloatSeries:
    """Set preliminary basic subsistence to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    regelbedarf_m_hh
        See :func:`regelbedarf_m_hh`.
    unter_vermögens_freibetrag_grunds_ia_hh
        See :func:`unter_vermögens_freibetrag_grunds_ia_hh`.

    Returns
    -------

    """
    out = regelbedarf_m_hh.copy()
    out.loc[~unter_vermögens_freibetrag_grunds_ia_hh] = 0
    return out


def unter_vermögens_freibetrag_grunds_ia_hh(
    vermögen_hh: FloatSeries, freibetrag_vermögen_grunds_ia_hh: FloatSeries
) -> BoolSeries:
    """Check if capital of household is below limit of Grundsicherung im Alter.

    Parameters
    ----------
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.
    freibetrag_vermögen_grunds_ia_hh
       See :func:`freibetrag_vermögen_grunds_ia_hh`.

    Returns
    -------

    """
    return vermögen_hh < freibetrag_vermögen_grunds_ia_hh


def freibetrag_vermögen_grunds_ia_hh(
    anz_erwachsene_hh: IntSeries, anz_kinder_hh: IntSeries, ges_renten_vers_params: dict
) -> FloatSeries:
    """Calculate maximum capital allowed for Grundsicherung im Alter.

    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    kinder_in_hh
        See :func:`kinder_in_hh`.
    Returns
    -------

    """
    out = (
        ges_renten_vers_params["schonvermögen_grunds_ia"]["adult"] * anz_erwachsene_hh
        + ges_renten_vers_params["schonvermögen_grunds_ia"]["child"] * anz_kinder_hh
    )
    return out
