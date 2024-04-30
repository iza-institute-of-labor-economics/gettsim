"""This module provides functions to compute advance alimony payments
(Unterhaltsvorschuss)."""

import numpy as np

from _gettsim.shared import join_numpy, policy_info

aggregate_by_p_id_unterhaltsvors = {
    "unterhaltsvors_zahlbetrag_eltern_m": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "unterhaltsvors_m",
        "aggr": "sum",
    },
}


@policy_info(params_key_for_rounding="unterhaltsvors")
def unterhaltsvors_m(
    kind_unterh_erhalt_m: float,
    _unterhaltsvors_anspruch_kind_m: float,
    parent_alleinerz: bool,
):
    """Advance alimony payments (Unterhaltsvorschuss) on child level after deducting
    alimonies.

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
    kind_unterh_erhalt_m
        See :func:`kind_unterh_erhalt_m`.
    _unterhaltsvors_anspruch_kind_m
        See :func:`_unterhaltsvors_anspruch_kind_m`.
    parent_alleinerz
        See :fung:`parent_alleinerz`.

    Returns
    -------

    """

    if parent_alleinerz:
        out = max(_unterhaltsvors_anspruch_kind_m - kind_unterh_erhalt_m, 0.0)
    else:
        out = 0.0

    return out


@policy_info(skip_vectorization=True)
def parent_alleinerz(
    p_id_kindergeld_empf: np.ndarray[int],
    p_id: np.ndarray[int],
    alleinerz: np.ndarray[bool],
):
    """Check if parent that receives Unterhaltsvorschuss is a single parent.

    Only single parents receive Unterhaltsvorschuss.

    Parameters
    ----------
    p_id_kindergeld_empf
        See basic input variable :ref:`p_id_kindergeld_empf`.
    p_id
        See basic input variable :ref:`p_id`.
    alleinerz
        See basic input variable :ref:`alleinerz`.

    Returns
    -------

    """
    join_numpy(p_id_kindergeld_empf, p_id, alleinerz)


@policy_info(start_date="2023-01-01", name_in_dag="_kindergeld_erstes_kind_m")
def _kindergeld_erstes_kind_ohne_staffelung_m(
    kindergeld_params: dict,
    alter: int,  # noqa: ARG001
) -> float:
    """Kindergeld for first child when Kindergeld does not depend on number of children.

    Parameters
    ----------

    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Remove fake dependency (alter).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666
    return kindergeld_params["kindergeld"]


@policy_info(end_date="2022-12-31", name_in_dag="_kindergeld_erstes_kind_m")
def _kindergeld_erstes_kind_gestaffelt_m(
    kindergeld_params: dict,
    alter: int,  # noqa: ARG001
) -> float:
    """Kindergeld for first child when Kindergeld does depend on number of children.

    Parameters
    ----------

    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Remove fake dependency (alter).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666
    return kindergeld_params["kindergeld"][1]


def _unterhaltsvors_anspruch_kind_m(
    alter: int,
    _unterhaltsvorschuss_empf_eink_above_income_threshold: bool,
    _kindergeld_erstes_kind_m: float,
    unterhalt_params: dict,
    unterhaltsvors_params: dict,
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    _unterhaltsvorschuss_empf_eink_above_income_threshold
        See :func:`_unterhaltsvorschuss_empf_eink_above_income_threshold`.
    _kindergeld_erstes_kind_m
        See :func:`_kindergeld_erstes_kind_m`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.
    unterhaltsvors_params
        See params documentation :ref:`unterhaltsvors_params <unterhaltsvors_params>`.

    Returns
    -------

    """
    altersgrenzen = unterhaltsvors_params["altersgrenzen"]
    mindestunterhalt = unterhalt_params["mindestunterhalt"]

    if alter < altersgrenzen[1]:
        out = mindestunterhalt[altersgrenzen[1]] - _kindergeld_erstes_kind_m
    elif altersgrenzen[1] <= alter < altersgrenzen[2]:
        out = mindestunterhalt[altersgrenzen[2]] - _kindergeld_erstes_kind_m
    elif altersgrenzen[2] <= alter < altersgrenzen[3]:
        out = mindestunterhalt[altersgrenzen[3]] - _kindergeld_erstes_kind_m
    else:
        out = 0.0

    # Older kids get it only if the single parent has income > mindesteinkommen.
    if (
        out > 0
        and (alter >= unterhaltsvors_params["altersgrenze_mindesteinkommen"])
        and (not _unterhaltsvorschuss_empf_eink_above_income_threshold)
    ):
        out = 0.0

    return out


@policy_info(skip_vectorization=True)
def _unterhaltsvorschuss_empf_eink_above_income_threshold(
    p_id_kindergeld_empf: np.ndarray[int],
    p_id: np.ndarray[int],
    _unterhaltsvorschuss_eink_above_income_threshold: np.ndarray[bool],
) -> np.ndarray[bool]:
    """Income of Unterhaltsvorschuss recipient above threshold (this variable is
    defined on child level).

    Parameters
    ----------
    p_id_kindergeld_empf
        See basic input variable :ref:`p_id_kindergeld_empf`.
    p_id
        See basic input variable :ref:`p_id`.
    _unterhaltsvorschuss_eink_above_income_threshold
        See :func:`_unterhaltsvorschuss_eink_above_income_threshold`.

    Returns
    -------
    """
    return join_numpy(
        p_id_kindergeld_empf, p_id, _unterhaltsvorschuss_eink_above_income_threshold
    )


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
