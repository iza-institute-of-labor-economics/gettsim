"""This module provides functions to compute alimony payments (Unterhalt)."""


def unterhaltsvors_m(
    alleinerz_bg: bool,
    alter: int,
    unterhaltsvorschuss_eink_m_bg: float,
    unterhalt_params: dict,
    kindergeld_params: dict,
) -> float:
    """Calculate advance on alimony payment (Unterhaltsvorschuss).

    Single Parents get alimony payments for themselves and for their child from the ex
    partner. If the ex partner is not able to pay the child alimony, the government pays
    the child alimony to the mother (or the father, if he has the kids)

    The amount is specified in §1612a BGB and, ultimately, in
    Mindestunterhaltsverordnung.

    # ToDo: Result was rounded up in previous code. Check if this is correct and
    # ToDo: implement rounding spec accordingly

    Parameters
    ----------
    alleinerz_bg
        See basic input variable :ref:`alleinerz_bg <alleinerz_bg>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    unterhaltsvorschuss_eink_m_bg
        See :func:`unterhaltsvorschuss_eink_m_bg`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """

    altersgrenzen = sorted(unterhalt_params["mindestunterhalt"].keys())
    if (alter < altersgrenzen[0]) and alleinerz_bg:
        out = (
            unterhalt_params["mindestunterhalt"][6] - kindergeld_params["kindergeld"][1]
        )
    elif (altersgrenzen[0] <= alter < altersgrenzen[1]) and alleinerz_bg:
        out = (
            unterhalt_params["mindestunterhalt"][12]
            - kindergeld_params["kindergeld"][1]
        )

    # Older kids get it only if the single parent has income > 600€.
    elif (
        (altersgrenzen[1] <= alter <= altersgrenzen[2])
        and alleinerz_bg
        and (
            unterhaltsvorschuss_eink_m_bg
            > unterhalt_params["unterhaltsvors_mindesteinkommen"]
        )
    ):
        out = (
            unterhalt_params["mindestunterhalt"][17]
            - kindergeld_params["kindergeld"][1]
        )
    else:
        out = 0.0

    # TODO: Check against actual transfers

    return out


def unterhaltsvorschuss_eink_m_bg(
    bruttolohn_m_bg: float,
    sonstig_eink_m_bg: float,
    eink_selbst_m_bg: float,
    eink_vermietung_m_bg: float,
    kapitaleink_brutto_m_bg: float,
    sum_ges_rente_priv_rente_m_bg: float,
    arbeitsl_geld_m_bg: float,
) -> float:
    """Calculate relevant income for advance on alimony payment on tax unit level.

    Parameters
    ----------
    bruttolohn_m_bg
        See :func:`bruttolohn_m_bg`.
    sonstig_eink_m_bg
        See :func:`sonstig_eink_m_bg`.
    eink_selbst_m_bg
        See :func:`eink_selbst_m_bg`.
    eink_vermietung_m_bg
        See :func:`eink_vermietung_m_bg`.
    kapitaleink_brutto_m_bg
        See :func:`kapitaleink_brutto_m_bg`.
    sum_ges_rente_priv_rente_m_bg
        See :func:`sum_ges_rente_priv_rente_m_bg`.
    arbeitsl_geld_m_bg
        See :func:`arbeitsl_geld_m_bg`.

    Returns
    -------

    """
    out = (
        bruttolohn_m_bg
        + sonstig_eink_m_bg
        + eink_selbst_m_bg
        + eink_vermietung_m_bg
        + kapitaleink_brutto_m_bg
        + sum_ges_rente_priv_rente_m_bg
        + arbeitsl_geld_m_bg
    )

    return out
