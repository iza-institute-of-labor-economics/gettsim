"""Income considered in the calculation of Grundsicherung im Alter."""

from _gettsim.functions.policy_function import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial


@policy_function
def einkommen_m(  # noqa: PLR0913
    erwerbseinkommen_m: float,
    private_rente_m: float,
    gesetzliche_rente_m: float,
    sonstig_eink_m: float,
    eink_vermietung_m: float,
    kapitaleinkommen_brutto_m: float,
    eink_st_m_sn: float,
    soli_st_m_sn: float,
    anz_personen_sn: int,
    sozialversicherungsbeitraege__betrag_arbeitnehmer_m: float,
    elterngeld__anrechenbarer_betrag_m: float,
) -> float:
    """Calculate individual income considered in the calculation of Grundsicherung im
    Alter.

    Parameters
    ----------
    erwerbseinkommen_m
        See :func:`erwerbseinkommen_m`.
    private_rente_m
        See :func:`private_rente_m`.
    gesetzliche_rente_m
        See :func:`gesetzliche_rente_m`.
    sonstig_eink_m
        See :func:`sonstig_eink_m`.
    eink_vermietung_m
        See :func:`eink_vermietung_m`.
    kapitaleinkommen_brutto_m
        See :func:`kapitaleinkommen_brutto_m`.
    eink_st_m_sn
        See :func:`eink_st_m_sn`.
    soli_st_m_sn
        See :func:`soli_st_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    sozialversicherungsbeitraege__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeitraege__betrag_arbeitnehmer_m`.
    elterngeld__anrechenbarer_betrag_m
        See :func:`elterngeld__anrechenbarer_betrag_m`.

    Returns
    -------

    """

    # Income
    total_income = (
        erwerbseinkommen_m
        + gesetzliche_rente_m
        + private_rente_m
        + sonstig_eink_m
        + eink_vermietung_m
        + kapitaleinkommen_brutto_m
        + elterngeld__anrechenbarer_betrag_m
    )

    out = (
        total_income
        - (eink_st_m_sn / anz_personen_sn)
        - (soli_st_m_sn / anz_personen_sn)
        - sozialversicherungsbeitraege__betrag_arbeitnehmer_m
    )

    return max(out, 0.0)


@policy_function
def erwerbseinkommen_m(
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


@policy_function
def kapitaleinkommen_brutto_m(
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


@policy_function
def private_rente_m(
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


@policy_function(end_date="2020-12-31", name_in_dag="gesetzliche_rente_m")
def gesetzliche_rente_m_bis_2020(
    rente__altersrente__betrag_m: float,
) -> float:
    """Calculate individual public pension benefits which are considered in the
    calculation of Grundsicherung im Alter until 2020.

    Until 2020: No deduction is possible.

    Parameters
    ----------
    rente__altersrente__betrag_m
        See basic input variable :ref:`rente__altersrente__betrag_m <rente__altersrente__betrag_m>`.

    Returns
    -------

    """  # noqa: E501
    return rente__altersrente__betrag_m


@policy_function(start_date="2021-01-01", leaf_name="gesetzliche_rente_m")
def gesetzliche_rente_m_ab_2021(
    rente__altersrente__betrag_m: float,
    rente__grundrente__grundsätzlich_anspruchsberechtigt: bool,
    arbeitsl_geld_2_params: dict,
    grunds_im_alter_params: dict,
) -> float:
    """Calculate individual public pension benefits which are considered in the
    calculation of Grundsicherung im Alter since 2021.

    Starting from 2021: If eligible for Grundrente, can deduct 100€ completely and 30%
    of private pension above 100 (but no more than 1/2 of regelbedarf)

    Parameters
    ----------
    rente__altersrente__betrag_m
        See basic input variable :ref:`rente__altersrente__betrag_m <rente__altersrente__betrag_m>`.
    rente__grundrente__grundsätzlich_anspruchsberechtigt
        See :func:`rente__grundrente__grundsätzlich_anspruchsberechtigt`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """  # noqa: E501

    angerechnete_rente = piecewise_polynomial(
        x=rente__altersrente__betrag_m,
        thresholds=grunds_im_alter_params["ges_rente_anr_frei"]["thresholds"],
        rates=grunds_im_alter_params["ges_rente_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=grunds_im_alter_params["ges_rente_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
    )

    upper = arbeitsl_geld_2_params["regelsatz"][1] / 2
    if rente__grundrente__grundsätzlich_anspruchsberechtigt:
        angerechnete_rente = min(angerechnete_rente, upper)
    else:
        angerechnete_rente = 0.0

    return rente__altersrente__betrag_m - angerechnete_rente
