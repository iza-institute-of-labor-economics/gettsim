from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kindergeld_m_basis(
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
    kumulativer_anspruch = (
        (kindergeld_anspruch.astype(int)).groupby(tu_id).transform("cumsum")
    )
    # Make sure that only eligible children get assigned kindergeld
    kumulativer_anspruch.loc[~kindergeld_anspruch] = 0
    out = kumulativer_anspruch.clip(
        upper=max(kindergeld_params["kindergeld"].keys())
    ).replace(kindergeld_params["kindergeld"])
    return out


def kindergeld_m_basis_tu(
    kindergeld_m_basis: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate the preliminary kindergeld on tax unit level.

    Parameters
    ----------
    kindergeld_m_basis
        See :func:`kindergeld_m_basis`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kindergeld_m_basis.groupby(tu_id).sum()


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


def kinderbonus_m_basis(
    kindergeld_m_basis: FloatSeries, kindergeld_params: dict
) -> FloatSeries:
    """Calculate the kinderbonus.

    (one-time payment, non-allowable against transfer payments)

    Parameters
    ----------
    kindergeld_m_basis
        See :func:`kindergeld_m_basis`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # Kinderbonus is payed for all children who are eligible for Kindergeld
    out = kindergeld_m_basis.copy()

    # Kinderbonus parameter is specified on the yearly level
    out.loc[kindergeld_m_basis > 0] = kindergeld_params["kinderbonus"] / 12
    return out


def kinderbonus_m_basis_tu(
    kinderbonus_m_basis: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate the Kinderbonus on tax unit level.

    Parameters
    ----------
    kinderbonus_m_basis
        See :func:`kinderbonus_m_basis`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kinderbonus_m_basis.groupby(tu_id).sum()
