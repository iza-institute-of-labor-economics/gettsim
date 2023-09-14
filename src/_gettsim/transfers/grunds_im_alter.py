from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import dates_active


def grunds_im_alter_m_vg(  # noqa: PLR0913
    arbeitsl_geld_2_regelbedarf_m_vg: float,
    _grunds_im_alter_mehrbedarf_schwerbeh_g_m_vg: float,
    kindergeld_m_vg: float,
    kind_unterh_erhalt_m_vg: float,
    unterhaltsvors_m_vg: float,
    grunds_im_alter_eink_m_vg: float,
    erwachsene_alle_rentner_vg: bool,
    vermögen_bedürft_vg: float,
    grunds_im_alter_vermög_freib_vg: float,
) -> float:
    """Calculate Grundsicherung im Alter on household level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    # ToDo: currently not implemented for retirees.

    # ToDo: Grundsicherung im Alter is only paid if all adults in the household
    # ToDo: are retired. Other households get ALG 2 (This is a simplification by
    # ToDo: GETTSIM)

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_vg
        See :func:`arbeitsl_geld_2_regelbedarf_m_vg`.
    _grunds_im_alter_mehrbedarf_schwerbeh_g_m_vg
        See :func:`_grunds_im_alter_mehrbedarf_schwerbeh_g_m_vg`.
    kindergeld_m_vg
        See :func:`kindergeld_m_vg`.
    kind_unterh_erhalt_m_vg
        See basic input variable
        :ref:`kind_unterh_erhalt_m_vg <kind_unterh_erhalt_m_vg>`.
    unterhaltsvors_m_vg
        See :func:`unterhaltsvors_m_vg`.
    grunds_im_alter_eink_m_vg
        See :func:`grunds_im_alter_eink_m_vg`.
    erwachsene_alle_rentner_vg
        See :func:`erwachsene_alle_rentner_vg`.
    vermögen_bedürft_vg
        See basic input variable :ref:`vermögen_bedürft_vg`.
    grunds_im_alter_vermög_freib_vg
        See :func:`grunds_im_alter_vermög_freib_vg`.
    Returns
    -------

    """

    # Wealth check
    # Only pay Grundsicherung im Alter if all adults are retired (see docstring)
    if (vermögen_bedürft_vg >= grunds_im_alter_vermög_freib_vg) or (
        not erwachsene_alle_rentner_vg
    ):
        out = 0.0
    else:
        # Subtract income
        out = (
            arbeitsl_geld_2_regelbedarf_m_vg
            + _grunds_im_alter_mehrbedarf_schwerbeh_g_m_vg
            - grunds_im_alter_eink_m_vg
            - kind_unterh_erhalt_m_vg
            - unterhaltsvors_m_vg
            - kindergeld_m_vg
        )

    return max(out, 0.0)


def grunds_im_alter_eink_m(  # noqa: PLR0913
    grunds_im_alter_erwerbseink_m: float,
    grunds_im_alter_priv_rente_m: float,
    grunds_im_alter_ges_rente_m: float,
    sonstig_eink_m: float,
    eink_vermietung_m: float,
    _grunds_im_alter_kapitaleink_brutto_m: float,
    eink_st_y_tu: float,
    soli_st_y_tu: float,
    anz_erwachsene_tu: int,
    sozialv_beitr_m: float,
    elterngeld_anr_m: float,
) -> float:
    """Calculate individual income considered in the calculation of Grundsicherung im
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
    eink_vermietung_m
        See :func:`eink_vermietung_m`.
    _grunds_im_alter_kapitaleink_brutto_m
        See :func:`_grunds_im_alter_kapitaleink_brutto_m`.
    eink_st_y_tu
        See :func:`eink_st_y_tu`.
    soli_st_y_tu
        See :func:`soli_st_y_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.
    elterngeld_anr_m
        See :func:`elterngeld_anr_m`.

    Returns
    -------

    """

    # Income
    total_income = (
        grunds_im_alter_erwerbseink_m
        + grunds_im_alter_ges_rente_m
        + grunds_im_alter_priv_rente_m
        + sonstig_eink_m
        + eink_vermietung_m
        + _grunds_im_alter_kapitaleink_brutto_m
        + elterngeld_anr_m
    )

    out = (
        total_income
        - (eink_st_y_tu / anz_erwachsene_tu / 12)
        - (soli_st_y_tu / anz_erwachsene_tu / 12)
        - sozialv_beitr_m
    )

    return max(out, 0.0)


def grunds_im_alter_erwerbseink_m(
    bruttolohn_m: float,
    eink_selbst_m: float,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> float:
    """Calculate individual earnings considered in the calculation of Grundsicherung im
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

    out = max(earnings, earnings_after_max_deduction)

    return out


def _grunds_im_alter_kapitaleink_brutto_m(
    kapitaleink_brutto_y: float,
    grunds_im_alter_params: dict,
) -> float:
    """Calculate individual capital income considered in the calculation of
    Grundsicherung im Alter.

    Legal reference: § 82 SGB XII Abs. 2


    Parameters
    ----------
    kapitaleink_brutto_y
        See :func:`kapitaleink_brutto_y`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params
        <grunds_im_alter_params>`.

    Returns
    -------

    """
    # Can deduct allowance from yearly capital income
    capital_income_y = (
        kapitaleink_brutto_y - grunds_im_alter_params["kapitaleink_anr_frei"]
    )

    # Calculate and return monthly capital income (after deduction)
    out = max(0.0, capital_income_y / 12)

    return out


def grunds_im_alter_priv_rente_m(
    priv_rente_m: float,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> float:
    """Calculate individual private pension benefits considered in the calculation of
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

    out = priv_rente_m - min(priv_rente_m_amount_exempt, upper)

    return out


def _grunds_im_alter_mehrbedarf_schwerbeh_g_m(
    schwerbeh_g: bool,
    anz_erwachsene_vg: int,
    grunds_im_alter_params: dict,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate additional allowance for individuals with disabled person's pass G.

    Parameters
    ----------
    schwerbeh_g
        See basic input variable :ref:`behinderungsgrad <schwerbeh_g>`.
    anz_erwachsene_vg
        See :func:`anz_erwachsene_vg`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    Returns
    -------

    """
    # mehrbedarf for disabilities = % of regelsatz of the person getting the mehrbedarf
    mehrbedarf_single = (arbeitsl_geld_2_params["regelsatz"][1]) * (
        grunds_im_alter_params["mehrbedarf_schwerbeh_g"]
    )
    mehrbedarf_in_couple = (arbeitsl_geld_2_params["regelsatz"][2]) * (
        grunds_im_alter_params["mehrbedarf_schwerbeh_g"]
    )

    if (schwerbeh_g) and (anz_erwachsene_vg == 1):
        out = mehrbedarf_single
    elif (schwerbeh_g) and (anz_erwachsene_vg > 1):
        out = mehrbedarf_in_couple
    else:
        out = 0.0

    return out


@dates_active(end="2020-12-31", change_name="grunds_im_alter_ges_rente_m")
def grunds_im_alter_ges_rente_m_bis_2020(
    ges_rente_m: float,
) -> float:
    """Calculate individual public pension benefits which are considered in the
    calculation of Grundsicherung im Alter until 2020.

    Until 2020: No deduction is possible.

    Parameters
    ----------
    ges_rente_m
        See basic input variable :ref:`ges_rente_m <ges_rente_m>`.

    Returns
    -------

    """
    return ges_rente_m


@dates_active(start="2021-01-01", change_name="grunds_im_alter_ges_rente_m")
def grunds_im_alter_ges_rente_m_ab_2021(
    ges_rente_m: float,
    grundr_berechtigt: bool,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> float:
    """Calculate individual public pension benefits which are considered in the
    calculation of Grundsicherung im Alter since 2021.

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

    angerechnete_rente = piecewise_polynomial(
        x=ges_rente_m,
        thresholds=grunds_im_alter_params["ges_rente_anr_frei"]["thresholds"],
        rates=grunds_im_alter_params["ges_rente_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=grunds_im_alter_params["ges_rente_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
    )

    upper = arbeitsl_geld_2_params["regelsatz"][1] / 2
    if grundr_berechtigt:
        angerechnete_rente = min(angerechnete_rente, upper)
    else:
        angerechnete_rente = 0.0

    return ges_rente_m - angerechnete_rente


def grunds_im_alter_vermög_freib_vg(
    anz_erwachsene_vg: int,
    anz_kinder_vg: int,
    grunds_im_alter_params: dict,
) -> float:
    """Calculate wealth not considered for Grundsicherung im Alter on household level.

    Parameters
    ----------
    anz_erwachsene_vg
        See :func:`anz_erwachsene_vg`.
    anz_kinder_vg
        See :func:`anz_kinder_vg`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    out = (
        grunds_im_alter_params["vermögensfreibetrag"]["adult"] * anz_erwachsene_vg
        + grunds_im_alter_params["vermögensfreibetrag"]["child"] * anz_kinder_vg
    )
    return out
