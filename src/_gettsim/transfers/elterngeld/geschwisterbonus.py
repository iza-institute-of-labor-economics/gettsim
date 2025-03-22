"""Parental leave bonus for siblings."""

from _gettsim.function_types import policy_function


@policy_function(start_date="2007-01-01")
def geschwisterbonus_m(
    basisbetrag_m: float,
    geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg: bool,
    elterngeld_params: dict,
) -> float:
    """Elterngeld bonus for (older) siblings.

    According to § 2a parents of siblings get a bonus.

    Parameters
    ----------
    basisbetrag_m
        See :func:`basisbetrag_m`.
    geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg
        See :func:`geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg:
        out = max(
            elterngeld_params["geschwisterbonus_aufschlag"] * basisbetrag_m,
            elterngeld_params["geschwisterbonus_minimum"],
        )
    else:
        out = 0.0
    return out


@policy_function(start_date="2007-01-01")
def mehrlingsbonus_m(anzahl_mehrlinge_fg: int, elterngeld_params: dict) -> float:
    """Elterngeld bonus for multiples.

    Parameters
    ----------
    anzahl_mehrlinge_fg
        See :func:`anzahl_mehrlinge_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return anzahl_mehrlinge_fg * elterngeld_params["mehrlingbonus"]


@policy_function(start_date="2007-01-01")
def geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg(
    anzahl_kinder_bis_2_fg: int,
    anzahl_kinder_bis_5_fg: int,
    elterngeld_params: dict,
) -> bool:
    """Siblings that give rise to Elterngeld siblings bonus.

    Parameters
    ----------
    anzahl_kinder_bis_2_fg
        See :func:`anzahl_kinder_bis_2_fg`.
    anzahl_kinder_bis_5_fg
        See :func:`anzahl_kinder_bis_5_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    geschwister_unter_3 = (
        anzahl_kinder_bis_2_fg >= elterngeld_params["geschwisterbonus_altersgrenzen"][3]
    )
    geschwister_unter_6 = (
        anzahl_kinder_bis_5_fg >= elterngeld_params["geschwisterbonus_altersgrenzen"][6]
    )

    return geschwister_unter_3 or geschwister_unter_6


@policy_function(start_date="2007-01-01")
def anzahl_mehrlinge_fg(
    anzahl_mehrlinge_jüngstes_kind_fg: int,
) -> int:
    """Number of multiples of the youngest child.

    Parameters
    ----------
    anzahl_mehrlinge_jüngstes_kind_fg
        See :func:`anzahl_mehrlinge_jüngstes_kind_fg`.

    Returns
    -------

    """
    out = anzahl_mehrlinge_jüngstes_kind_fg - 1
    return max(out, 0)
