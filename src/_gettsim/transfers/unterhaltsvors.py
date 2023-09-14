"""This module provides functions to compute advance alimony payments
(Unterhaltsvorschuss)."""


def unterhaltsvors_m(  # noqa: PLR0913
    alleinerz_tu: bool,
    alter: int,
    unterhaltsvorschuss_eink_m_tu: float,
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
    alleinerz_tu
        See basic input variable :ref:`alleinerz_tu <alleinerz_tu>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    unterhaltsvorschuss_eink_m_tu
        See :func:`unterhaltsvorschuss_eink_m_tu`.
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

    if (alter < altersgrenzen[1]) and alleinerz_tu:
        out = mindestunterhalt[altersgrenzen[1]] - kindergeld_first_child
    elif (altersgrenzen[1] <= alter < altersgrenzen[2]) and alleinerz_tu:
        out = mindestunterhalt[altersgrenzen[2]] - kindergeld_first_child
    elif (altersgrenzen[2] <= alter < altersgrenzen[3]) and alleinerz_tu:
        out = mindestunterhalt[altersgrenzen[3]] - kindergeld_first_child
    else:
        out = 0.0

    # Older kids get it only if the single parent has income > mindesteinkommen.
    if (
        out > 0
        and (alter >= unterhaltsvors_params["altersgrenze_mindesteinkommen"])
        and (unterhaltsvorschuss_eink_m_tu < unterhaltsvors_params["mindesteinkommen"])
    ):
        out = 0.0

    # Check against the actual child alimony payments given by kindesunterhalt_m
    out = max(out - kind_unterh_erhalt_m, 0.0)

    return out


def unterhaltsvorschuss_eink_m_tu(  # noqa: PLR0913
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
