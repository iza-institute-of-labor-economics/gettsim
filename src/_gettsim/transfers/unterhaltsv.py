"""This module provides functions to compute alimony payments (Unterhalt)."""


def unterhaltsvors_m(
    alleinerz_tu: bool,
    alter: int,
    unterhaltsvorschuss_eink_m_tu: float,
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
    alleinerz_tu
        See basic input variable :ref:`alleinerz_tu <alleinerz_tu>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    unterhaltsvorschuss_eink_m_tu
        See :func:`unterhaltsvorschuss_eink_m_tu`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """

    altersgrenzen = sorted(unterhalt_params["mindestunterhalt"].keys())
    if (alter < altersgrenzen[0]) and alleinerz_tu:
        out = (
            unterhalt_params["mindestunterhalt"][6] - kindergeld_params["kindergeld"][1]
        )
    elif (altersgrenzen[0] <= alter < altersgrenzen[1]) and alleinerz_tu:
        out = (
            unterhalt_params["mindestunterhalt"][12]
            - kindergeld_params["kindergeld"][1]
        )

    # Older kids get it only if the single parent has income > 600€.
    elif (
        (altersgrenzen[1] <= alter <= altersgrenzen[2])
        and alleinerz_tu
        and (
            unterhaltsvorschuss_eink_m_tu
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


def unterhaltsvorschuss_eink_m_tu(
    bruttolohn_m_tu: float,
    sonstig_eink_m_tu: float,
    eink_selbst_m_tu: float,
    eink_vermietung_m_tu: float,
    kapitaleink_brutto_m_tu: float,
    sum_ges_rente_priv_rente_m_tu: float,
    arbeitsl_geld_m_tu: float,
) -> float:
    """Calculate relevant income for advance on alimony payment on tax unit level.

    Parameters
    ----------
    bruttolohn_m_tu
        See :func:`bruttolohn_m_tu`.
    sonstig_eink_m_tu
        See :func:`sonstig_eink_m_tu`.
    eink_selbst_m_tu
        See :func:`eink_selbst_m_tu`.
    eink_vermietung_m_tu
        See :func:`eink_vermietung_m_tu`.
    kapitaleink_brutto_m_tu
        See :func:`kapitaleink_brutto_m_tu`.
    sum_ges_rente_priv_rente_m_tu
        See :func:`sum_ges_rente_priv_rente_m_tu`.
    arbeitsl_geld_m_tu
        See :func:`arbeitsl_geld_m_tu`.

    Returns
    -------

    """
    out = (
        bruttolohn_m_tu
        + sonstig_eink_m_tu
        + eink_selbst_m_tu
        + eink_vermietung_m_tu
        + kapitaleink_brutto_m_tu
        + sum_ges_rente_priv_rente_m_tu
        + arbeitsl_geld_m_tu
    )

    return out
