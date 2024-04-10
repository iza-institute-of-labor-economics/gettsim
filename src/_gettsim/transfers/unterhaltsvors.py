"""This module provides functions to compute advance alimony payments
(Unterhaltsvorschuss)."""

from _gettsim.shared import add_rounding_spec

aggregate_by_group_id_unterhaltsvors = {
    "_unterhaltsvorschuss_eink_above_income_threshold_fg": {
        "group_id_to_aggregate_by": "fg_id",
        "source_col": "_unterhaltsvorschuss_eink_above_income_threshold",
        "aggr": "any",
    },
}

aggregate_by_p_id_unterhaltsvors = {
    "_unterhaltsvors_anspruch_eltern_m": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "_unterhaltsvors_anspruch_pro_kind_m",
        "aggr": "sum",
    },
}


@add_rounding_spec(rounding_key="unterhaltsvors")
def unterhaltsvors_m(
    alleinerz: bool,
    kind_unterh_erhalt_m: float,
    _unterhaltsvors_anspruch_eltern_m: float,
) -> float:
    """Advance alimony payments (Unterhaltsvorschuss).

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

    Parameters
    ----------
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    kind_unterh_erhalt_m
        See :func:`kind_unterh_erhalt_m`.
    _unterhaltsvors_anspruch_eltern_m
        See :func:`_unterhaltsvors_anspruch_eltern_m`.

    Returns
    -------

    """

    if alleinerz:
        out = max(_unterhaltsvors_anspruch_eltern_m - kind_unterh_erhalt_m, 0.0)
    else:
        out = 0.0

    return out


def _unterhaltsvors_anspruch_pro_kind_m(
    alter: int,
    _unterhaltsvorschuss_eink_above_income_threshold_fg: bool,
    unterhalt_params: dict,
    unterhaltsvors_params: dict,
    kindergeld_params: dict,
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) per child.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    _unterhaltsvorschuss_eink_above_income_threshold_fg
        See :func:`_unterhaltsvorschuss_eink_above_income_threshold_fg`.
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

    if alter < altersgrenzen[1]:
        out = mindestunterhalt[altersgrenzen[1]] - kindergeld_first_child
    elif altersgrenzen[1] <= alter < altersgrenzen[2]:
        out = mindestunterhalt[altersgrenzen[2]] - kindergeld_first_child
    elif altersgrenzen[2] <= alter < altersgrenzen[3]:
        out = mindestunterhalt[altersgrenzen[3]] - kindergeld_first_child
    else:
        out = 0.0

    # Older kids get it only if the single parent has income > mindesteinkommen.
    if (
        out > 0
        and (alter >= unterhaltsvors_params["altersgrenze_mindesteinkommen"])
        and (not _unterhaltsvorschuss_eink_above_income_threshold_fg)
    ):
        out = 0.0

    return out


def _unterhaltsvorschuss_eink_above_income_threshold(
    unterhaltsvorschuss_eink_m: float,
    unterhaltsvors_params: dict,
) -> bool:
    """Check if income is above the threshold for advance alimony payments.

    Parameters
    ----------
    unterhaltsvorschuss_eink_m
        See :func:`unterhaltsvorschuss_eink_m`.
    unterhaltsvors_params
        See params documentation :ref:`unterhaltsvors_params <unterhaltsvors_params>`.

    Returns
    -------

    """
    return unterhaltsvorschuss_eink_m >= unterhaltsvors_params["mindesteinkommen"]


def unterhaltsvorschuss_eink_m(  # noqa: PLR0913
    bruttolohn_m: float,
    sonstig_eink_m: float,
    eink_selbst_m: float,
    eink_vermietung_m: float,
    kapitaleink_brutto_m: float,
    sum_ges_rente_priv_rente_m: float,
    arbeitsl_geld_m: float,
) -> float:
    """Calculate relevant income for advance on alimony payment.

    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    sonstig_eink_m
        See :func:`sonstig_eink_m`.
    eink_selbst_m
        See :func:`eink_selbst_m`.
    eink_vermietung_m
        See :func:`eink_vermietung_m`.
    kapitaleink_brutto_m
        See :func:`kapitaleink_brutto_m`.
    sum_ges_rente_priv_rente_m
        See :func:`sum_ges_rente_priv_rente_m`.
    arbeitsl_geld_m
        See :func:`arbeitsl_geld_m`.

    Returns
    -------

    """
    out = (
        bruttolohn_m
        + sonstig_eink_m
        + eink_selbst_m
        + eink_vermietung_m
        + kapitaleink_brutto_m
        + sum_ges_rente_priv_rente_m
        + arbeitsl_geld_m
    )

    return out
