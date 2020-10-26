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
    out = kumulativer_anspruch.clip(upper=4).replace(kindergeld_params["kindergeld"])
    return out


def kindergeld_m_tu_basis(
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
    """
    Nowadays, kids must not work more than 20 hour
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

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

    """
    out = alter <= 18
    out = out | (
        (19 <= alter)
        & (alter <= kindergeld_params["kindergeld_hoechstalter"])
        & in_ausbildung
        & (arbeitsstunden_w <= kindergeld_params["kindergeld_stundengrenze"])
    )

    return out


def kindergeld_anspruch_nach_lohn(
    alter: IntSeries,
    in_ausbildung: BoolSeries,
    bruttolohn_m: FloatSeries,
    kindergeld_params: dict,
) -> BoolSeries:
    """
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
    out = alter <= 18
    out = out | (
        (19 <= alter)
        & (alter <= kindergeld_params["kindergeld_hoechstalter"])
        & in_ausbildung
        & (bruttolohn_m <= kindergeld_params["kindergeld_einkommensgrenze"] / 12)
    )

    return out
