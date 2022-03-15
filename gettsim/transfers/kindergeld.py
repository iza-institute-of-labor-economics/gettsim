from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kindergeld_m_bis_1996(kindergeld_basis_m: FloatSeries) -> FloatSeries:
    """Kindergeld calculation until 1996.

    Until 1996 individuals could claim child allowance and recieve child benefit.

    Parameters
    ----------
    kindergeld_basis_m
        See :func:`kindergeld_basis_m`.

    Returns
    -------

    """
    return kindergeld_basis_m


def kindergeld_m_ab_1997(
    kinderfreib_günstiger_tu: BoolSeries, kindergeld_basis_m: FloatSeries,
) -> FloatSeries:
    """Kindergeld calculation since 1997.

    Parameters
    ----------
    kinderfreib_günstiger_tu
        See :func:`kinderfreib_günstiger_tu`.
    kindergeld_basis_m
        See :func:`kindergeld_basis_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    beantrage_kinderfreib = kinderfreib_günstiger_tu
    out = kindergeld_basis_m
    if beantrage_kinderfreib:
        return 0
    else:
        return out


def kindergeld_m_hh(kindergeld_m: FloatSeries, hh_id: IntSeries) -> FloatSeries:
    """Aggregate Child benefit on the household level.

    Aggregate Child benefit on the household level, as we could have several tax_units
    in one household.

    Parameters
    ----------
    kindergeld_m
        See :func:`kindergeld_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return kindergeld_m.groupby(hh_id).sum()


def kindergeld_m_tu(kindergeld_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate Child benefit on the tax unit level.

    Parameters
    ----------
    kindergeld_m
        See :func:`kindergeld_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kindergeld_m.groupby(tu_id).sum()


def kindergeld_basis_m(
    tu_id: IntSeries, kindergeld_anspruch: BoolSeries, kindergeld_params: dict
) -> FloatSeries:
    """Calculate the preliminary kindergeld.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # Kindergeld_Anspruch is the cumulative sum of eligible children.
    kumulativer_anspruch = int(kindergeld_anspruch).groupby(tu_id).transform("cumsum")

    grenze = max(kindergeld_params["kindergeld"]).replace(
        kindergeld_params["kindergeld"]
    )

    # Make sure that only eligible children get assigned kindergeld
    if not kindergeld_anspruch:
        return 0
    elif kindergeld_anspruch & (kumulativer_anspruch > grenze):
        return grenze
    else:
        return kumulativer_anspruch


def kindergeld_basis_m_tu(
    kindergeld_basis_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate the preliminary kindergeld on tax unit level.

    Parameters
    ----------
    kindergeld_basis_m
        See :func:`kindergeld_basis_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kindergeld_basis_m.groupby(tu_id).sum()


def kindergeld_anspruch_nach_stunden(
    alter: IntSeries,
    in_ausbildung: BoolSeries,
    arbeitsstunden_w: FloatSeries,
    kindergeld_params: dict,
) -> BoolSeries:
    """Determine kindergeld eligibility depending on working hours.

    The current eligibility rule is, that kids must not work more than 20
    hour and are below 25.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    in_ausbildung
        See :func:`in_ausbildung`.
    arbeitsstunden_w
        See :func:`arbeitsstunden_w`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------
    BoolSeries indiciating kindergeld eligibility.
    """
    out = alter < kindergeld_params["höchstalter"]["ohne_bedingungen"]
    out = out | (
        (kindergeld_params["höchstalter"]["ohne_bedingungen"] <= alter)
        & (alter <= kindergeld_params["höchstalter"]["mit_bedingungen"])
        & in_ausbildung
        & (arbeitsstunden_w <= kindergeld_params["stundengrenze"])
    )

    return out


def kindergeld_anspruch_nach_lohn(
    alter: IntSeries,
    in_ausbildung: BoolSeries,
    bruttolohn_m: FloatSeries,
    kindergeld_params: dict,
) -> BoolSeries:
    """Determine kindergeld eligibility depending on kids wage.

    Before 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    in_ausbildung
        See basic input variable :ref:`in_ausbildung <in_ausbildung>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.

    Returns
    -------

    """
    out = alter < kindergeld_params["höchstalter"]["ohne_bedingungen"]
    out = out | (
        (kindergeld_params["höchstalter"]["ohne_bedingungen"] <= alter)
        & (alter <= kindergeld_params["höchstalter"]["mit_bedingungen"])
        & in_ausbildung
        & (bruttolohn_m <= kindergeld_params["einkommensgrenze"] / 12)
    )

    return out


def kinderbonus_basis_m(
    kindergeld_basis_m: FloatSeries, kindergeld_params: dict
) -> FloatSeries:
    """Calculate the kinderbonus.

    (one-time payment, non-allowable against transfer payments)

    Parameters
    ----------
    kindergeld_basis_m
        See :func:`kindergeld_basis_m`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # Kinderbonus is payed for all children who are eligible for Kindergeld
    out = kindergeld_basis_m.copy()

    # Kinderbonus parameter is specified on the yearly level
    if kindergeld_basis_m > 0:
        return kindergeld_params["kinderbonus"] / 12
    else:
        return out


def kinderbonus_basis_m_tu(
    kinderbonus_basis_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate the Kinderbonus on tax unit level.

    Parameters
    ----------
    kinderbonus_basis_m
        See :func:`kinderbonus_basis_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kinderbonus_basis_m.groupby(tu_id).sum()
