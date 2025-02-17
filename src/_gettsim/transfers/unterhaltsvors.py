"""This module provides functions to compute advance alimony payments
(Unterhaltsvorschuss)."""

import numpy

from _gettsim.shared import join_numpy, policy_info

aggregate_by_p_id_unterhaltsvors = {
    "unterhaltsvors_zahlbetrag_eltern_m": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "unterhaltsvors_m",
        "aggr": "sum",
    },
}


@policy_info(start_date="2009-01-01", params_key_for_rounding="unterhaltsvors")
def unterhaltsvors_m(
    kind_unterh_erhalt_m: float,
    _unterhaltsvors_anspruch_kind_m: float,
    parent_alleinerz: bool,
) -> float:
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
        See basic input variable `kind_unterh_erhalt_m`.
    _unterhaltsvors_anspruch_kind_m
        See :func:`_unterhaltsvors_anspruch_kind_m`.
    parent_alleinerz
        See :func:`parent_alleinerz`.

    Returns
    -------

    """
    if parent_alleinerz:
        out = max(_unterhaltsvors_anspruch_kind_m - kind_unterh_erhalt_m, 0.0)
    else:
        out = 0.0

    return out


@policy_info(
    end_date="2008-12-31",
    name_in_dag="unterhaltsvors_m",
    params_key_for_rounding="unterhaltsvors",
)
def unterhaltsvors_not_implemented_m() -> float:
    raise NotImplementedError(
        """
        Unterhaltsvorschuss is not implemented prior to 2009.
    """
    )


@policy_info(skip_vectorization=True)
def parent_alleinerz(
    p_id_kindergeld_empf: numpy.ndarray[int],
    p_id: numpy.ndarray[int],
    alleinerz: numpy.ndarray[bool],
) -> numpy.ndarray[bool]:
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
    return join_numpy(
        p_id_kindergeld_empf, p_id, alleinerz, value_if_foreign_key_is_missing=False
    )


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


@policy_info(
    start_date="2009-01-01",
    end_date="2014-12-31",
    name_in_dag="_unterhaltsvors_anspruch_kind_m",
)
def _unterhaltsvors_anspruch_kind_m_2009_bis_2014(
    alter: int,
    _kindergeld_erstes_kind_m: float,
    unterhaltsvors_params: dict,
    eink_st_abzuege_params: dict,
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Relevant parameter is directly 'steuerfrei zu stellenden sächlichen Existenzminimum
    des minderjährigen Kindes' § 1612a (1). Modeling relative to the child allowance for
    this. The amout for the lower age group is defined relative to the middle age group
    with a factor of 0.87.

    Rule was in priciple also active for 2015 but has been overwritten by an
    Anwendungsvorschrift as Kinderfreibetrag and Kindergeld changed on July 2015.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    _kindergeld_erstes_kind_m
        See :func:`_kindergeld_erstes_kind_m`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    unterhaltsvors_params
        See params documentation :ref:`unterhaltsvors_params <unterhaltsvors_params>`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Remove explicit parameter conversion.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/575
    altersgrenzen = unterhaltsvors_params["altersgrenzen_bezug"]

    kinderfreib_sächl_existenzmin = eink_st_abzuege_params["kinderfreib"][
        "sächl_existenzmin"
    ]

    if altersgrenzen[1]["min_alter"] <= alter <= altersgrenzen[1]["max_alter"]:
        out = (
            unterhaltsvors_params["faktor_jüngste_altersgruppe"]
            * (2 * kinderfreib_sächl_existenzmin / 12)
            - _kindergeld_erstes_kind_m
        )
    elif altersgrenzen[2]["min_alter"] <= alter <= altersgrenzen[2]["max_alter"]:
        out = 2 * kinderfreib_sächl_existenzmin / 12 - _kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_info(
    start_date="2015-01-01",
    end_date="2015-12-31",
    name_in_dag="_unterhaltsvors_anspruch_kind_m",
)
def _unterhaltsvors_anspruch_kind_m_anwendungsvors(
    alter: int,
    unterhaltsvors_params: dict,
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Rule _unterhaltsvors_anspruch_kind_m_2009_bis_2014 was in priciple also active for
    2015 but has been overwritten by an Anwendungsvorschrift as Kinderfreibetrag and
    Kindergeld changed in July 2015.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    unterhaltsvors_params
        See params documentation :ref:`unterhaltsvors_params <unterhaltsvors_params>`.

    Returns
    -------

    """
    altersgrenzen = unterhaltsvors_params["altersgrenzen_bezug"]

    unterhaltsvors = unterhaltsvors_params["unterhaltsvors_anwendungsvors"]

    if altersgrenzen[1]["min_alter"] <= alter <= altersgrenzen[1]["max_alter"]:
        out = unterhaltsvors[1]
    elif altersgrenzen[2]["min_alter"] <= alter <= altersgrenzen[2]["max_alter"]:
        out = unterhaltsvors[2]
    else:
        out = 0.0

    return out


@policy_info(
    start_date="2016-01-01",
    end_date="2017-06-30",
    name_in_dag="_unterhaltsvors_anspruch_kind_m",
)
def _unterhaltsvors_anspruch_kind_m_2016_bis_201706(
    alter: int,
    _kindergeld_erstes_kind_m: float,
    unterhalt_params: dict,
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    § 2 Unterhaltsvorschussgesetz refers to Section § 1612a BGB. There still is the
    reference to 'steuerfrei zu stellenden sächlichen Existenzminimum des minderjährigen
    Kindes' (§ 1612a (1)) as well as a Verordnungsermächtigung (§ 1612a (4)). The § 1
    Mindesunterhaltsverordnung applies fixed amounts and no relative definition as
    before.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    _kindergeld_erstes_kind_m
        See :func:`_kindergeld_erstes_kind_m`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.

    Returns
    -------

    """
    mindestunterhalt = unterhalt_params["mindestunterhalt"]

    if mindestunterhalt[1]["min_alter"] <= alter <= mindestunterhalt[1]["max_alter"]:
        out = mindestunterhalt[1]["betrag"] - _kindergeld_erstes_kind_m
    elif mindestunterhalt[2]["min_alter"] <= alter <= mindestunterhalt[2]["max_alter"]:
        out = mindestunterhalt[2]["betrag"] - _kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_info(start_date="2017-07-01", name_in_dag="_unterhaltsvors_anspruch_kind_m")
def _unterhaltsvors_anspruch_kind_m_ab_201707(
    alter: int,
    _unterhaltsvorschuss_empf_eink_above_income_threshold: bool,
    _kindergeld_erstes_kind_m: float,
    unterhalt_params: dict,
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Introduction of a minimum income threshold if child is older than some threshold and
    third age group (12-17) via Artikel 23 G. v. 14.08.2017 BGBl. I S. 3122.

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

    Returns
    -------

    """
    mindestunterhalt = unterhalt_params["mindestunterhalt"]

    if mindestunterhalt[1]["min_alter"] <= alter <= mindestunterhalt[1]["max_alter"]:
        out = mindestunterhalt[1]["betrag"] - _kindergeld_erstes_kind_m
    elif mindestunterhalt[2]["min_alter"] <= alter <= mindestunterhalt[2]["max_alter"]:
        out = mindestunterhalt[2]["betrag"] - _kindergeld_erstes_kind_m
    elif (
        mindestunterhalt[3]["min_alter"] <= alter <= mindestunterhalt[3]["max_alter"]
        and _unterhaltsvorschuss_empf_eink_above_income_threshold
    ):
        out = mindestunterhalt[3]["betrag"] - _kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_info(start_date="2017-01-01", skip_vectorization=True)
def _unterhaltsvorschuss_empf_eink_above_income_threshold(
    p_id_kindergeld_empf: numpy.ndarray[int],
    p_id: numpy.ndarray[int],
    _unterhaltsvorschuss_eink_above_income_threshold: numpy.ndarray[bool],
) -> numpy.ndarray[bool]:
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
        p_id_kindergeld_empf,
        p_id,
        _unterhaltsvorschuss_eink_above_income_threshold,
        value_if_foreign_key_is_missing=False,
    )


@policy_info(start_date="2017-01-01")
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


@policy_info(start_date="2017-01-01")
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
