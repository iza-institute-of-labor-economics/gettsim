from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grunds_im_alter_m_hh(
    grunds_ia_m_minus_eink_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    kinderzuschlag_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschlag_vorrang_hh: BoolSeries,
    anz_erwachsene_hh: IntSeries,
    anz_rentner_hh: IntSeries,
) -> FloatSeries:
    """Calculate Grundsicherung im Alter on household level.

    Parameters
    ----------
    grunds_ia_m_minus_eink_hh
        See :func:`grunds_ia_m_minus_eink_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    kinderzuschlag_vorrang_hh
        See :func:`kinderzuschlag_vorrang_hh`.
    wohngeld_kinderzuschlag_vorrang_hh
        See :func:`wohngeld_kinderzuschlag_vorrang_hh`.
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.
    Returns
    -------

    """
    out = grunds_ia_m_minus_eink_hh.clip(lower=0)
    cond = (
        wohngeld_vorrang_hh
        | kinderzuschlag_vorrang_hh
        | wohngeld_kinderzuschlag_vorrang_hh
        | (anz_erwachsene_hh != anz_rentner_hh)
    )
    out.loc[cond] = 0
    return out


def grunds_ia_m_minus_eink_hh(
    regelbedarf_m_grunds_ia_vermögens_check_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    grunds_ia_eink_hh: FloatSeries,
) -> FloatSeries:
    """Calculate remaining basic subsistence after recieving other benefits.

    Parameters
    ----------
    regelbedarf_m_grunds_ia_vermögens_check_hh
        See :func:`regelbedarf_m_grunds_ia_vermögens_check_hh`.
    kindergeld_m_hh
        See :func:`kindergeld_m_hh`.
    unterhaltsvors_m_hh
        See :func:`unterhaltsvors_m_hh`.
    grunds_ia_eink_hh
        See :func:`grunds_ia_eink_hh`.

    Returns
    -------

    """
    out = (
        regelbedarf_m_grunds_ia_vermögens_check_hh
        - grunds_ia_eink_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return out


def grunds_ia_eink_hh(grunds_ia_eink: FloatSeries, hh_id: IntSeries) -> FloatSeries:
    """Sum up income for calculation of Grundsicherung im Alter per household.

    Parameters
    ----------
    grunds_ia_eink
        See :func:`grunds_ia_eink`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return grunds_ia_eink.groupby(hh_id).sum()


def grunds_ia_eink(
    grunds_ia_eink_excl_pensions: FloatSeries,
    eink_st_tu: FloatSeries,
    tu_id: IntSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_m: FloatSeries,
    grunds_ia_eink_anr_frei: FloatSeries,
    freibetrag_grunds_ia_grundr: FloatSeries,
    freibetrag_prv_rente: FloatSeries,
) -> FloatSeries:
    """Sum up income for calculation of Grundsicherung im Alter.

    Parameters
    ----------
    grunds_ia_eink_excl_pensions
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
    eink_excl_pensions = (
        grunds_ia_eink_excl_pensions
        - tu_id.replace((eink_st_tu / anz_erwachsene_tu) / 12)
        - tu_id.replace((soli_st_tu / anz_erwachsene_tu) / 12)
        - sozialv_beitr_m
        - grunds_ia_eink_anr_frei
        - +-freibetrag_prv_rente
    ).clip(lower=0)

    return


def grunds_ia_eink_excl_pensions(
    bruttolohn_m: FloatSeries,
    sonstig_eink_m: FloatSeries,
    eink_selbst_m: FloatSeries,
    vermiet_eink_m: FloatSeries,
    kapital_eink_m: FloatSeries,
    elterngeld_m: FloatSeries,
) -> FloatSeries:

    """Sum up the income before tax (excluding pension payments)

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`hh_id <hh_id>`.
    sonstig_eink_m
        See basic input variable :ref:`sonstig_eink_m <sonstig_eink_m>`.
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    vermiet_eink_mp
        See basic input variable :ref:`vermiet_eink_m <vermiet_eink_m>`.
    kapital_eink_m
        See basic input variable :ref:`kapital_eink_m <kapital_eink_m>`.
    elterngeld_m
        See :func:`elterngeld_m`.

    Returns
    -------
    FloatSeries with the income by unemployment insurance before tax.
    """
    return (
        bruttolohn_m
        + sonstig_eink_m
        + eink_selbst_m
        + vermiet_eink_m
        + kapital_eink_m
        + elterngeld_m
    )


def grunds_ia_eink_anr_frei(
    bruttolohn_m: FloatSeries, arbeitsl_geld_2_params: dict
) -> FloatSeries:
    """Calculate income not considered for amount of Grundsicherung
    im Alter (oder bei voller Erwerbsminderung)

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
    out = regelbedarf_m_hh
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
