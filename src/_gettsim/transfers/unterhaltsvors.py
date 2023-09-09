"""This module provides functions to compute advance alimony payments
(Unterhaltsvorschuss)."""


def unterhaltsvors_m(  # noqa: PLR0913
    alleinerz_bg: bool,
    alter: int,
    unterhaltsvorschuss_eink_m_bg: float,
    kind_unterh_erhalt_m: float,
    unterhalt_params: dict,
    unterhaltsvors_params: dict,
    kindergeld_params: dict,
) -> float:
    """Calculate advance on alimony payment (Unterhaltsvorschuss).

    Single Parents get alimony payments for themselves and for their child from the ex
    partner. If the ex partner is not able to pay the child alimony, the government pays
    the child alimony to the mother (or the father, if he has the kids).

    According to §1 Abs.1 Nr.3 UhVorschG those single parents are entitled to
    advance alimony payments, who do not or not regularly receive child alimony
    payments or orphans' benefits (Waisenbezüge) in at least the amount specified in
    §2 Abs.1 and 2 UhVorschG. The child alimonay payment paid by the other parent
    is credited against the amount of the advance alimony payments
    (§2 Abs.3 Nr.1 UhVorschG).

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
    kind_unterh_erhalt_m
        See basic input variable :ref:`kind_unterh_erhalt_m <kind_unterh_erhalt_m>`
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.
    unterhaltsvors_params
        See params documentation :ref:`unterhaltsvors_params <unterhaltsvors_params>`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    altersgrenzen = unterhaltsvors_params["altersgrenzen"]
    mindestunterhalt = unterhalt_params["mindestunterhalt"]
    kindergeld_first_child = kindergeld_params["kindergeld"][1]
    if (alter < altersgrenzen[1]) and alleinerz_bg:
        out = mindestunterhalt[altersgrenzen[1]] - kindergeld_first_child
    elif (altersgrenzen[1] <= alter < altersgrenzen[2]) and alleinerz_bg:
        out = mindestunterhalt[altersgrenzen[2]] - kindergeld_first_child

    elif (altersgrenzen[2] <= alter < altersgrenzen[3]) and alleinerz_bg:
        out = mindestunterhalt[altersgrenzen[3]] - kindergeld_first_child
    else:
        out = 0.0

    # Older kids get it only if the single parent has income > mindesteinkommen.
    if (
        out > 0
        and (unterhaltsvors_params["altersgrenze_mindesteinkommen"] <= alter)
        and (unterhaltsvorschuss_eink_m_bg < unterhaltsvors_params["mindesteinkommen"])
    ):
        out = 0.0

    # Check against the actual child alimony payments given by kindesunterhalt_m
    out = max(out - kind_unterh_erhalt_m, 0.0)

    return out


def unterhaltsvorschuss_eink_m_bg(  # noqa: PLR0913
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
