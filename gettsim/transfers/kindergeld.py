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
    if kinderfreib_günstiger_tu:
        out = 0.0
    else:
        out = kindergeld_basis_m

    return out


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

    obergrenze = max(kindergeld_params["kindergeld"]).replace(
        kindergeld_params["kindergeld"]
    )

    # Make sure that only eligible children get assigned kindergeld
    if not kindergeld_anspruch:
        out = 0.0
    else:
        out = min(kumulativer_anspruch, obergrenze)

    return out


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
    out = (alter < kindergeld_params["höchstalter"]["ohne_bedingungen"]) | (
        (alter < kindergeld_params["höchstalter"]["mit_bedingungen"])
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
    out = (alter < kindergeld_params["höchstalter"]["ohne_bedingungen"]) | (
        (alter < kindergeld_params["höchstalter"]["mit_bedingungen"])
        & in_ausbildung
        & (bruttolohn_m <= kindergeld_params["einkommensgrenze"] / 12)
    )

    return out
