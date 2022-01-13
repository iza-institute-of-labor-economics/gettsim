import pandas as pd

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grunds_im_alter_m_hh(
    grunds_im_alter_m_minus_eink_hh: FloatSeries,
    alle_erwachsene_rentner_hh: BoolSeries,
) -> FloatSeries:
    """Calculate Grundsicherung im Alter on household level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    currently not implemented for retirees.

    Parameters
    ----------
    grunds_im_alter_m_minus_eink_hh
        See :func:`grunds_im_alter_m_minus_eink_hh`.
    alle_erwachsene_rentner_hh
        See :func:`alle_erwachsene_rentner_hh`.

    Returns
    -------

    """
    out = grunds_im_alter_m_minus_eink_hh.clip(lower=0)
    out.loc[~alle_erwachsene_rentner_hh] = 0
    return out


def grunds_im_alter_m_minus_eink_hh(
    regelbedarf_m_grunds_im_alter_vermögens_check_hh: FloatSeries,
    mehrbedarf_behinderung_m_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    anrechenbares_eink_grunds_im_alter_m_hh: FloatSeries,
) -> FloatSeries:
    """Calculate remaining basic subsistence after recieving other benefits.

    Parameters
    ----------
    regelbedarf_m_grunds_im_alter_vermögens_check_hh
        See :func:`regelbedarf_m_grunds_im_alter_vermögens_check_hh`.
    mehrbedarf_behinderung_m_hh
        See :func:`mehrbedarf_behinderung_m_hh`.
    kindergeld_m_hh
        See :func:`kindergeld_m_hh`.
    unterhaltsvors_m_hh
        See :func:`unterhaltsvors_m_hh`.
    anrechenbares_eink_grunds_im_alter_m_hh
        See :func:`anrechenbares_eink_grunds_im_alter_m_hh`.

    Returns
    -------

    """
    out = (
        regelbedarf_m_grunds_im_alter_vermögens_check_hh
        + mehrbedarf_behinderung_m_hh
        - anrechenbares_eink_grunds_im_alter_m_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return out


def anrechenbares_eink_grunds_im_alter_m_hh(
    anrechenbares_eink_grunds_im_alter_m: FloatSeries, hh_id: IntSeries
) -> FloatSeries:
    """Aggregate income which is considered in the calculation of Grundsicherung im
    Alter on household level.

    Parameters
    ----------
    anrechenbares_eink_grunds_im_alter_m
        See :func:`anrechenbares_eink_grunds_im_alter_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return anrechenbares_eink_grunds_im_alter_m.groupby(hh_id).sum()


def anrechenbares_eink_grunds_im_alter_m(
    anrechenbares_erwerbs_eink_grunds_im_alter_m: FloatSeries,
    anrechenbare_prv_rente_grunds_im_alter_m: FloatSeries,
    anrechenbare_staatl_rente_grunds_im_alter_m: FloatSeries,
    sonstig_eink_m: FloatSeries,
    vermiet_eink_m: FloatSeries,
    anrechenbares_kapital_eink_grunds_im_alter_m: FloatSeries,
    elterngeld_m: FloatSeries,
    eink_st_tu: FloatSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_m: FloatSeries,
    tu_id: IntSeries,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate income which is considered in the calculation of Grundsicherung im
    Alter.

    Parameters
    ----------
    anrechenbares_erwerbs_eink_grunds_im_alter_m
        See :func:`anrechenbares_erwerbs_eink_grunds_im_alter_m`.
    anrechenbare_prv_rente_grunds_im_alter_m
        See :func:`anrechenbare_prv_rente_grunds_im_alter_m`.
    anrechenbare_staatl_rente_grunds_im_alter_m
        See :func:`anrechenbare_staatl_rente_grunds_im_alter_m`.
    sonstig_eink_m
        See :func:`sonstig_eink_m`.
    vermiet_eink_m
        See :func:`vermiet_eink_m`.
    anrechenbares_kapital_eink_grunds_im_alter_m
        See :func:`anrechenbares_kapital_eink_grunds_im_alter_m`.
    elterngeld_m
        See :func:`elterngeld_m`.
    eink_st_tu
        See :func:`eink_st_tu`.
    soli_st_tu
        See :func:`soli_st_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    grunds_im_alter_params
        See params documentation
        :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """

    # Consider Elterngeld that is larger than 300
    anrechenbares_elterngeld_m = (
        elterngeld_m - grunds_im_alter_params["elterngeld_anr_frei"]
    ).clip(lower=0)

    # Income
    total_income = (
        anrechenbares_erwerbs_eink_grunds_im_alter_m
        + anrechenbare_staatl_rente_grunds_im_alter_m
        + anrechenbare_prv_rente_grunds_im_alter_m
        + sonstig_eink_m
        + vermiet_eink_m
        + anrechenbares_kapital_eink_grunds_im_alter_m
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


def anrechenbares_erwerbs_eink_grunds_im_alter_m(
    bruttolohn_m: FloatSeries,
    eink_selbst_m: FloatSeries,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate earnings which are considered in the calculation of Grundsicherung im
    Alter.

    Legal reference: § 82 SGB XII Abs. 3

    Note: Freibeträge for income are currently not considered
    Note: the cap at 1/2 of Regelbedarf was only introduced in 2006 (which is currently
    not implemented): https://www.buzer.de/gesetz/3415/al3764-0.htm

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    earnings = bruttolohn_m + eink_selbst_m

    # Can deduct 30% of earnings (but no more than 1/2 of regelbedarf)
    earnings_after_max_deduction = earnings - arbeitsl_geld_2_params["regelsatz"][1] / 2
    earnings = ((1 - grunds_im_alter_params["erwerbs_eink_anr_frei"]) * earnings).clip(
        lower=earnings_after_max_deduction
    )

    return earnings


def anrechenbares_kapital_eink_grunds_im_alter_m(
    brutto_eink_5: FloatSeries, grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate capital income which are considered in the calculation of Grundsicherung im
    Alter.

    Legal reference: § 82 SGB XII Abs. 2


    Parameters
    ----------
    brutto_eink_5
        See :func:`brutto_eink_5`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    # Can deduct allowance from yearly capital income
    capital_income_y = (
        brutto_eink_5 - grunds_im_alter_params["kapital_eink_anr_frei"]
    ).clip(lower=0)

    # Calculate and return monthly capital income (after deduction)
    return capital_income_y / 12


def anrechenbare_prv_rente_grunds_im_alter_m(
    prv_rente_m: FloatSeries,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate private pension benefits which are considered in the calculation of
    Grundsicherung im Alter.

    Legal reference: § 82 SGB XII Abs. 4

    Parameters
    ----------
    prv_rente_m
        See basic input variable :ref:`prv_rente_m <prv_rente_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    prv_rente_m_amount_exempt = piecewise_polynomial(
        x=prv_rente_m,
        thresholds=grunds_im_alter_params["prv_rente_anr_frei"]["thresholds"],
        rates=grunds_im_alter_params["prv_rente_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=grunds_im_alter_params["prv_rente_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
    )

    prv_rente_m_amount_exempt = prv_rente_m_amount_exempt.clip(
        upper=arbeitsl_geld_2_params["regelsatz"][1] / 2
    )

    return prv_rente_m - prv_rente_m_amount_exempt


def mehrbedarf_behinderung_m_hh(
    mehrbedarf_behinderung_m: FloatSeries, hh_id: IntSeries,
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
    schwerbe_ausweis_g: BoolSeries,
    hhsize_tu: IntSeries,
    grunds_im_alter_params: dict,
    arbeitsl_geld_2_params: dict,
    tu_id: IntSeries,
) -> FloatSeries:
    """Calculate mehrbedarf for people with disabilities.

    Parameters
    ----------
    schwerbe_ausweis_g
        See basic input variable :ref:`behinderungsgrad <schwerbe_ausweis_g>`.
    hhsize_tu
        See :func:`hhsize_tu`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    Returns
    -------

    """
    out = pd.Series(0, index=schwerbe_ausweis_g.index, dtype=float)
    hhsize_tu = tu_id.replace(hhsize_tu)

    # mehrbedarf for disabilities = % of regelsatz of the person getting the mehrbedarf
    bedarf1 = (arbeitsl_geld_2_params["regelsatz"][1]) * (
        grunds_im_alter_params["mehrbedarf_g"]["rate"]
    )
    bedarf2 = (arbeitsl_geld_2_params["regelsatz"][2]) * (
        grunds_im_alter_params["mehrbedarf_g"]["rate"]
    )

    # singles
    out.loc[(schwerbe_ausweis_g)] = bedarf1

    # couples
    out.loc[(schwerbe_ausweis_g) & (hhsize_tu != 1)] = bedarf2

    return out


def anrechenbare_staatl_rente_grunds_im_alter_m(
    staatl_rente_m: FloatSeries,
    nicht_grundrentenberechtigt: BoolSeries,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate public pension benefits which are considered in the calculation of
    Grundsicherung im Alter.

    Starting from 2020: If eligible for Grundrente, can deduct 100€ completely and 30%
    of private pension above 100 (but no more than 1/2 of regelbedarf)

    Parameters
    ----------
    staatl_rente_m
        See basic input variable :ref:`staatl_rente_m <staatl_rente_m>`.
    nicht_grundrentenberechtigt
        See :func:`nicht_grundrentenberechtigt`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """

    deducted_rent = piecewise_polynomial(
        x=staatl_rente_m,
        thresholds=grunds_im_alter_params["staatl_rente_anr_frei"]["thresholds"],
        rates=grunds_im_alter_params["staatl_rente_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=grunds_im_alter_params["staatl_rente_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
    )

    deducted_rent = deducted_rent.clip(upper=arbeitsl_geld_2_params["regelsatz"][1] / 2)
    deducted_rent.loc[nicht_grundrentenberechtigt] = 0

    return staatl_rente_m - deducted_rent


def regelbedarf_m_grunds_im_alter_vermögens_check_hh(
    regelbedarf_m_hh: FloatSeries,
    unter_vermögens_freibetrag_grunds_im_alter_hh: BoolSeries,
) -> FloatSeries:
    """Set preliminary basic subsistence to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    regelbedarf_m_hh
        See :func:`regelbedarf_m_hh`.
    unter_vermögens_freibetrag_grunds_im_alter_hh
        See :func:`unter_vermögens_freibetrag_grunds_im_alter_hh`.

    Returns
    -------

    """
    out = regelbedarf_m_hh.copy()
    out.loc[~unter_vermögens_freibetrag_grunds_im_alter_hh] = 0
    return out


def unter_vermögens_freibetrag_grunds_im_alter_hh(
    vermögen_hh: FloatSeries, freibetrag_vermögen_grunds_im_alter_hh: FloatSeries
) -> BoolSeries:
    """Check if capital of household is below limit of Grundsicherung im Alter.

    Parameters
    ----------
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.
    freibetrag_vermögen_grunds_im_alter_hh
       See :func:`freibetrag_vermögen_grunds_im_alter_hh`.

    Returns
    -------

    """
    return vermögen_hh < freibetrag_vermögen_grunds_im_alter_hh


def freibetrag_vermögen_grunds_im_alter_hh(
    anz_erwachsene_hh: IntSeries,
    anz_kinder_hh: IntSeries,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate maximum capital allowed for Grundsicherung im Alter.

    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    anz_kinder_hh
        See :func:`anz_kinder_hh`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    out = (
        grunds_im_alter_params["schonvermögen_grunds_im_alter"]["adult"]
        * anz_erwachsene_hh
        + grunds_im_alter_params["schonvermögen_grunds_im_alter"]["child"]
        * anz_kinder_hh
    )
    return out
