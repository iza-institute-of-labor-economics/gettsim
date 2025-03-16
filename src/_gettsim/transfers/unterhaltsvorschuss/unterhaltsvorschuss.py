"""Advance alimony payments (Unterhaltsvorschuss)."""

import numpy

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.function_types import policy_function
from _gettsim.shared import join_numpy

aggregation_specs = {
    "an_elternteil_auszuzahlender_betrag_m": AggregateByPIDSpec(
        p_id_to_aggregate_by="kindergeld__p_id_empfänger",
        source_col="betrag_m",
        aggr="sum",
    ),
}


@policy_function(start_date="2009-01-01", params_key_for_rounding="unterhaltsvors")
def betrag_m(
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    anspruchshöhe_m: float,
    elternteil_alleinerziehend: bool,
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
    unterhalt__tatsächlich_erhaltener_betrag_m
        See basic input variable `unterhalt__tatsächlich_erhaltener_betrag_m`.
    anspruchshöhe_m
        See :func:`anspruchshöhe_m`.
    elternteil_alleinerziehend
        See :func:`elternteil_alleinerziehend`.

    Returns
    -------

    """
    if elternteil_alleinerziehend:
        out = max(anspruchshöhe_m - unterhalt__tatsächlich_erhaltener_betrag_m, 0.0)
    else:
        out = 0.0

    return out


@policy_function(skip_vectorization=True)
def elternteil_alleinerziehend(
    kindergeld__p_id_empfänger: numpy.ndarray[int],
    demographics__p_id: numpy.ndarray[int],
    demographics__alleinerziehend: numpy.ndarray[bool],
) -> numpy.ndarray[bool]:
    """Check if parent that receives Kindergeld is a single parent.

    Only single parents receive Kindergeld.

    Parameters
    ----------
    kindergeld__p_id_empfänger
        See basic input variable :ref:`kindergeld__p_id_empfänger`.
    demographics__p_id
        See basic input variable :ref:`p_id`.
    demographics__alleinerziehend
        See basic input variable :ref:`alleinerziehend`.

    Returns
    -------

    """
    return join_numpy(
        foreign_key=kindergeld__p_id_empfänger,
        primary_key=demographics__p_id,
        target=demographics__alleinerziehend,
        value_if_foreign_key_is_missing=False,
    )


@policy_function(
    end_date="2008-12-31",
    leaf_name="betrag_m",
    params_key_for_rounding="unterhaltsvors",
)
def not_implemented_m() -> float:
    raise NotImplementedError(
        """
        Unterhaltsvorschuss is not implemented prior to 2009.
    """
    )


@policy_function(start_date="2023-01-01", leaf_name="kindergeld_erstes_kind_m")
def kindergeld_erstes_kind_ohne_staffelung_m(
    kindergeld_params: dict,
    demographics__alter: int,  # noqa: ARG001
) -> float:
    """Kindergeld for first child when Kindergeld does not depend on number of children.

    Parameters
    ----------

    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Remove fake dependency (demographics__alter).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666
    return kindergeld_params["kindergeld"]


@policy_function(end_date="2022-12-31", leaf_name="kindergeld_erstes_kind_m")
def kindergeld_erstes_kind_gestaffelt_m(
    kindergeld_params: dict,
    demographics__alter: int,  # noqa: ARG001
) -> float:
    """Kindergeld for first child when Kindergeld does depend on number of children.

    Parameters
    ----------

    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Remove fake dependency (demographics__alter).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666
    return kindergeld_params["kindergeld"][1]


@policy_function(
    start_date="2009-01-01",
    end_date="2014-12-31",
    leaf_name="anspruchshöhe_m",
)
def unterhaltsvorschuss_anspruch_m_2009_bis_2014(
    demographics__alter: int,
    kindergeld_erstes_kind_m: float,
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
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    kindergeld_erstes_kind_m
        See :func:`kindergeld_erstes_kind_m`.
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

    kinderfreibetrag_sächl_existenzmin = eink_st_abzuege_params["kinderfreib"][
        "sächl_existenzmin"
    ]

    if (
        altersgrenzen[1]["min_alter"]
        <= demographics__alter
        <= altersgrenzen[1]["max_alter"]
    ):
        out = (
            unterhaltsvors_params["faktor_jüngste_altersgruppe"]
            * (2 * kinderfreibetrag_sächl_existenzmin / 12)
            - kindergeld_erstes_kind_m
        )
    elif (
        altersgrenzen[2]["min_alter"]
        <= demographics__alter
        <= altersgrenzen[2]["max_alter"]
    ):
        out = 2 * kinderfreibetrag_sächl_existenzmin / 12 - kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2015-01-01",
    end_date="2015-12-31",
    leaf_name="anspruchshöhe_m",
)
def anspruchshöhe_m_anwendungsvors(
    demographics__alter: int,
    unterhaltsvors_params: dict,
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Rule anspruchshöhe_m_2009_bis_2014 was in priciple also active for
    2015 but has been overwritten by an Anwendungsvorschrift as Kinderfreibetrag and
    Kindergeld changed in July 2015.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    unterhaltsvors_params
        See params documentation :ref:`unterhaltsvors_params <unterhaltsvors_params>`.

    Returns
    -------

    """
    altersgrenzen = unterhaltsvors_params["altersgrenzen_bezug"]

    unterhaltsvors = unterhaltsvors_params["anwendungsvorschrift"]

    if (
        altersgrenzen[1]["min_alter"]
        <= demographics__alter
        <= altersgrenzen[1]["max_alter"]
    ):
        out = unterhaltsvors[1]
    elif (
        altersgrenzen[2]["min_alter"]
        <= demographics__alter
        <= altersgrenzen[2]["max_alter"]
    ):
        out = unterhaltsvors[2]
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2016-01-01",
    end_date="2017-06-30",
    leaf_name="anspruchshöhe_m",
)
def anspruchshöhe_m_2016_bis_2017_06(
    demographics__alter: int,
    kindergeld_erstes_kind_m: float,
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
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    kindergeld_erstes_kind_m
        See :func:`kindergeld_erstes_kind_m`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.

    Returns
    -------

    """
    mindestunterhalt = unterhalt_params["mindestunterhalt"]

    if (
        mindestunterhalt[1]["min_alter"]
        <= demographics__alter
        <= mindestunterhalt[1]["max_alter"]
    ):
        out = mindestunterhalt[1]["betrag"] - kindergeld_erstes_kind_m
    elif (
        mindestunterhalt[2]["min_alter"]
        <= demographics__alter
        <= mindestunterhalt[2]["max_alter"]
    ):
        out = mindestunterhalt[2]["betrag"] - kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_function(start_date="2017-07-01", leaf_name="anspruchshöhe_m")
def anspruchshöhe_m_ab_201707(
    demographics__alter: int,
    elternteil_mindesteinkommen_erreicht: bool,
    kindergeld_erstes_kind_m: float,
    unterhalt_params: dict,
) -> float:
    """Claim for advance on alimony payment (Unterhaltsvorschuss) on child level.

    Introduction of a minimum income threshold if child is older than some threshold and
    third age group (12-17) via Artikel 23 G. v. 14.08.2017 BGBl. I S. 3122.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    elternteil_mindesteinkommen_erreicht
        See :func:`elternteil_mindesteinkommen_erreicht`.
    kindergeld_erstes_kind_m
        See :func:`kindergeld_erstes_kind_m`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.

    Returns
    -------

    """
    mindestunterhalt = unterhalt_params["mindestunterhalt"]

    if (
        mindestunterhalt[1]["min_alter"]
        <= demographics__alter
        <= mindestunterhalt[1]["max_alter"]
    ):
        out = mindestunterhalt[1]["betrag"] - kindergeld_erstes_kind_m
    elif (
        mindestunterhalt[2]["min_alter"]
        <= demographics__alter
        <= mindestunterhalt[2]["max_alter"]
    ):
        out = mindestunterhalt[2]["betrag"] - kindergeld_erstes_kind_m
    elif (
        mindestunterhalt[3]["min_alter"]
        <= demographics__alter
        <= mindestunterhalt[3]["max_alter"]
        and elternteil_mindesteinkommen_erreicht
    ):
        out = mindestunterhalt[3]["betrag"] - kindergeld_erstes_kind_m
    else:
        out = 0.0

    return out


@policy_function(start_date="2017-01-01", skip_vectorization=True)
def elternteil_mindesteinkommen_erreicht(
    kindergeld__p_id_empfänger: numpy.ndarray[int],
    demographics__p_id: numpy.ndarray[int],
    mindesteinkommen_erreicht: numpy.ndarray[bool],
) -> numpy.ndarray[bool]:
    """Income of Unterhaltsvorschuss recipient above threshold (this variable is
    defined on child level).

    Parameters
    ----------
    kindergeld__p_id_empfänger
        See basic input variable :ref:`kindergeld__p_id_empfänger`.
    demographics__p_id
        See basic input variable :ref:`demographics__p_id`.
    mindesteinkommen_erreicht
        See :func:`mindesteinkommen_erreicht`.

    Returns
    -------
    """
    return join_numpy(
        kindergeld__p_id_empfänger,
        demographics__p_id,
        mindesteinkommen_erreicht,
        value_if_foreign_key_is_missing=False,
    )


@policy_function(start_date="2017-01-01")
def mindesteinkommen_erreicht(
    einkommen_m: float,
    unterhaltsvors_params: dict,
) -> bool:
    """Check if income is above the threshold for advance alimony payments.

    Parameters
    ----------
    einkommen_m
        See :func:`einkommen_m`.
    unterhaltsvors_params
        See params documentation :ref:`unterhaltsvors_params <unterhaltsvors_params>`.

    Returns
    -------

    """
    return einkommen_m >= unterhaltsvors_params["mindesteinkommen"]


@policy_function(start_date="2017-01-01")
def einkommen_m(  # noqa: PLR0913
    einnahmen__bruttolohn_m: float,
    einnahmen__sonstige_m: float,
    einkünfte__aus_selbstständigkeit_m: float,
    einkünfte__aus_vermietung_und_verpachtung_m: float,
    einnahmen__kapitalerträge_m: float,
    sozialversicherung__rente__altersrente__betrag_m: float,
    sozialversicherung__rente__private_rente_betrag_m: float,
    sozialversicherung__arbeitslosen__betrag_m: float,
) -> float:
    """Calculate relevant income for advance on alimony payment.

    Parameters
    ----------
    einnahmen__bruttolohn_m
        See :func:`einnahmen__bruttolohn_m`.
    einnahmen__sonstige_m
        See :func:`einnahmen__sonstige_m`.
    einkünfte__aus_selbstständigkeit_m
        See :func:`einkünfte__aus_selbstständigkeit_m`.
    einkünfte__aus_vermietung_und_verpachtung_m
        See :func:`einkünfte__aus_vermietung_und_verpachtung_m`.
    einnahmen__kapitalerträge_m
        See :func:`einnahmen__kapitalerträge_m`.
    sozialversicherung__rente__altersrente__betrag_m
        See :func:`sozialversicherung__rente__altersrente__betrag_m`.
    sozialversicherung__rente__private_rente_betrag_m
        See :func:`sozialversicherung__rente__private_rente_betrag_m`.
    sozialversicherung__arbeitslosen__betrag_m
        See :func:`sozialversicherung__arbeitslosen__betrag_m`.

    Returns
    -------

    """
    out = (
        einnahmen__bruttolohn_m
        + einnahmen__sonstige_m
        + einkünfte__aus_selbstständigkeit_m
        + einkünfte__aus_vermietung_und_verpachtung_m
        + einnahmen__kapitalerträge_m
        + sozialversicherung__rente__altersrente__betrag_m
        + sozialversicherung__rente__private_rente_betrag_m
        + sozialversicherung__arbeitslosen__betrag_m
    )

    return out
