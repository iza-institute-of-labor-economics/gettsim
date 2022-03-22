from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grunds_im_alter_m_hh(
    arbeitsl_geld_2_regelbedarf_m_hh: FloatSeries,
    _grunds_im_alter_mehrbedarf_schwerbeh_g_m_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    grunds_im_alter_eink_m_hh: FloatSeries,
    erwachsene_alle_rentner_hh: BoolSeries,
    vermögen_hh: FloatSeries,
    grunds_im_alter_vermög_freib_hh: FloatSeries,
) -> FloatSeries:
    """Calculate Grundsicherung im Alter on household level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    # ToDo: currently not implemented for retirees.

    # ToDo: Grundsicherung im Alter is only paid if all adults in the household
    # ToDo: are retired. Other households get ALG 2 (This is a simplification by
    # ToDo: GETTSIM)

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_hh
        See :func:`arbeitsl_geld_2_regelbedarf_m_hh`.
    _grunds_im_alter_mehrbedarf_schwerbeh_g_m_hh
        See :func:`_grunds_im_alter_mehrbedarf_schwerbeh_g_m_hh`.
    kindergeld_m_hh
        See :func:`kindergeld_m_hh`.
    unterhaltsvors_m_hh
        See :func:`unterhaltsvors_m_hh`.
    grunds_im_alter_eink_m_hh
        See :func:`grunds_im_alter_eink_m_hh`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh`.
    vermögen_hh
        See basic input variable :ref:`vermögen_hh`.
    grunds_im_alter_vermög_freib_hh
        See :func:`grunds_im_alter_vermög_freib_hh`.
    Returns
    -------

    """

    # Wealth check
    # Only pay Grundsicherung im Alter if all adults are retired (see docstring)
    if (vermögen_hh >= grunds_im_alter_vermög_freib_hh) | (
        not erwachsene_alle_rentner_hh
    ):
        out = 0.0
    else:
        # Subtract income
        out = (
            arbeitsl_geld_2_regelbedarf_m_hh
            + _grunds_im_alter_mehrbedarf_schwerbeh_g_m_hh
            - grunds_im_alter_eink_m_hh
            - unterhaltsvors_m_hh
            - kindergeld_m_hh
        )
        out = max(out, 0)

    return out


def grunds_im_alter_eink_m_hh(
    grunds_im_alter_eink_m: FloatSeries, hh_id: IntSeries
) -> FloatSeries:
    """Aggregate income which is considered in the calculation of Grundsicherung im
    Alter on household level.

    Parameters
    ----------
    grunds_im_alter_eink_m
        See :func:`grunds_im_alter_eink_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return grunds_im_alter_eink_m.groupby(hh_id).sum()


def grunds_im_alter_eink_m(
    grunds_im_alter_erwerbseink_m: FloatSeries,
    grunds_im_alter_priv_rente_m: FloatSeries,
    grunds_im_alter_ges_rente_m: FloatSeries,
    sonstig_eink_m: FloatSeries,
    vermiet_eink_m: FloatSeries,
    _grunds_im_alter_kapitaleink_brutto_m: FloatSeries,
    elterngeld_m: FloatSeries,
    eink_st_tu: FloatSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_gesamt_m: FloatSeries,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate income considered in the calculation of Grundsicherung im
    Alter.

    Parameters
    ----------
    grunds_im_alter_erwerbseink_m
        See :func:`grunds_im_alter_erwerbseink_m`.
    grunds_im_alter_priv_rente_m
        See :func:`grunds_im_alter_priv_rente_m`.
    grunds_im_alter_ges_rente_m
        See :func:`grunds_im_alter_ges_rente_m`.
    sonstig_eink_m
        See :func:`sonstig_eink_m`.
    vermiet_eink_m
        See :func:`vermiet_eink_m`.
    _grunds_im_alter_kapitaleink_brutto_m
        See :func:`_grunds_im_alter_kapitaleink_brutto_m`.
    elterngeld_m
        See :func:`elterngeld_m`.
    eink_st_tu
        See :func:`eink_st_tu`.
    soli_st_tu
        See :func:`soli_st_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    sozialv_beitr_gesamt_m
        See :func:`sozialv_beitr_gesamt_m`.
    grunds_im_alter_params
        See params documentation
        :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """

    # Consider Elterngeld that is larger than 300
    elterngeld_grunds_im_alter_m = (
        elterngeld_m - grunds_im_alter_params["elterngeld_anr_frei"]
    )

    if elterngeld_grunds_im_alter_m < 0:
        elterngeld_grunds_im_alter_m = 0
    else:
        elterngeld_grunds_im_alter_m = elterngeld_grunds_im_alter_m

    # Income
    total_income = (
        grunds_im_alter_erwerbseink_m
        + grunds_im_alter_ges_rente_m
        + grunds_im_alter_priv_rente_m
        + sonstig_eink_m
        + vermiet_eink_m
        + _grunds_im_alter_kapitaleink_brutto_m
        + elterngeld_grunds_im_alter_m
    )

    # subtract taxes and social insurance contributions
    # TODO: Change this to lohn_steuer
    out = (
        total_income
        - (eink_st_tu / anz_erwachsene_tu / 12)
        - (soli_st_tu / anz_erwachsene_tu / 12)
        - sozialv_beitr_gesamt_m
    )

    return max(out, 0.0)


def grunds_im_alter_erwerbseink_m(
    bruttolohn_m: FloatSeries,
    eink_selbst_m: FloatSeries,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate earnings considered in the calculation of Grundsicherung im
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
    earnings = (1 - grunds_im_alter_params["erwerbseink_anr_frei"]) * earnings

    if earnings < earnings_after_max_deduction:
        return earnings_after_max_deduction
    else:
        return earnings


def _grunds_im_alter_kapitaleink_brutto_m(
    kapitaleink_brutto: FloatSeries, grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate capital income considered in the calculation of Grundsicherung im
    Alter.

    Legal reference: § 82 SGB XII Abs. 2


    Parameters
    ----------
    kapitaleink_brutto
        See :func:`kapitaleink_brutto`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    # Can deduct allowance from yearly capital income
    capital_income_y = (
        kapitaleink_brutto - grunds_im_alter_params["kapitaleink_anr_frei"]
    )

    # Calculate and return monthly capital income (after deduction)
    if capital_income_y < 0:
        out = 0.0
    else:
        out = capital_income_y / 12

    return out


def grunds_im_alter_priv_rente_m(
    priv_rente_m: FloatSeries,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate private pension benefits considered in the calculation of
    Grundsicherung im Alter.

    Legal reference: § 82 SGB XII Abs. 4

    Parameters
    ----------
    priv_rente_m
        See basic input variable :ref:`priv_rente_m <priv_rente_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    priv_rente_m_amount_exempt = piecewise_polynomial(
        x=priv_rente_m,
        thresholds=grunds_im_alter_params["priv_rente_anr_frei"]["thresholds"],
        rates=grunds_im_alter_params["priv_rente_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=grunds_im_alter_params["priv_rente_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
    )
    upper = arbeitsl_geld_2_params["regelsatz"][1] / 2
    if priv_rente_m_amount_exempt > upper:
        return priv_rente_m - upper
    else:
        return priv_rente_m - priv_rente_m_amount_exempt


def _grunds_im_alter_mehrbedarf_schwerbeh_g_m_hh(
    _grunds_im_alter_mehrbedarf_schwerbeh_g_m: FloatSeries, hh_id: IntSeries,
) -> FloatSeries:
    """Aggregate additional allowance for individuals with disabled person's pass G on
    household level.

    Parameters
    ----------
    _grunds_im_alter_mehrbedarf_schwerbeh_g_m
        See :func:`_grunds_im_alter_mehrbedarf_schwerbeh_g_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    Returns
    -------

    """
    return _grunds_im_alter_mehrbedarf_schwerbeh_g_m.groupby(hh_id).sum()


def _grunds_im_alter_mehrbedarf_schwerbeh_g_m(
    schwerbeh_g: BoolSeries,
    anz_erwachsene_hh: IntSeries,
    grunds_im_alter_params: dict,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate additional allowance for individuals with disabled person's pass G.

    Parameters
    ----------
    schwerbeh_g
        See basic input variable :ref:`behinderungsgrad <schwerbeh_g>`.
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    Returns
    -------

    """
    # mehrbedarf for disabilities = % of regelsatz of the person getting the mehrbedarf
    mehrbedarf_singles = (arbeitsl_geld_2_params["regelsatz"][1]) * (
        grunds_im_alter_params["mehrbedarf_schwerbeh_g"]["rate"]
    )
    mehrbedarf_in_couple = (arbeitsl_geld_2_params["regelsatz"][2]) * (
        grunds_im_alter_params["mehrbedarf_schwerbeh_g"]["rate"]
    )

    if (schwerbeh_g) & (anz_erwachsene_hh == 1):
        return mehrbedarf_singles
    elif (schwerbeh_g) & (anz_erwachsene_hh > 1):
        return mehrbedarf_in_couple
    else:
        return 0


def grunds_im_alter_ges_rente_m_bis_2020(ges_rente_m: FloatSeries,) -> FloatSeries:
    """Calculate public pension benefits which are considered in the calculation of
    Grundsicherung im Alter.

    Until 2020: No deduction is possible.

    Parameters
    ----------
    ges_rente_m
        See basic input variable :ref:`ges_rente_m <ges_rente_m>`.

    Returns
    -------

    """
    return ges_rente_m


def grunds_im_alter_ges_rente_m_ab_2021(
    ges_rente_m: FloatSeries,
    grundr_berechtigt: BoolSeries,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate public pension benefits which are considered in the calculation of
    Grundsicherung im Alter.

    Starting from 2021: If eligible for Grundrente, can deduct 100€ completely and 30%
    of private pension above 100 (but no more than 1/2 of regelbedarf)

    Parameters
    ----------
    ges_rente_m
        See basic input variable :ref:`ges_rente_m <ges_rente_m>`.
    grundr_berechtigt
        See :func:`grundr_berechtigt`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """

    deducted_rent = piecewise_polynomial(
        x=ges_rente_m,
        thresholds=grunds_im_alter_params["ges_rente_anr_frei"]["thresholds"],
        rates=grunds_im_alter_params["ges_rente_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=grunds_im_alter_params["ges_rente_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
    )

    grenze = arbeitsl_geld_2_params["regelsatz"][1] / 2
    if (grundr_berechtigt) & (deducted_rent <= grenze):
        deducted_rent = deducted_rent
    elif (grundr_berechtigt) & (deducted_rent > grenze):
        deducted_rent = grenze
    else:
        deducted_rent = 0

    return ges_rente_m - deducted_rent


def grunds_im_alter_vermög_freib_hh(
    anz_erwachsene_hh: IntSeries,
    anz_kinder_hh: IntSeries,
    grunds_im_alter_params: dict,
) -> FloatSeries:
    """Calculate maximum wealth not considered for Grundsicherung im Alter.

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
        grunds_im_alter_params["vermögensfreibetrag"]["adult"] * anz_erwachsene_hh
        + grunds_im_alter_params["vermögensfreibetrag"]["child"] * anz_kinder_hh
    )
    return out
