"""Parental leave bonus for siblings."""


def elterngeld_geschwisterbonus_m(
    elterngeld_basisbetrag_m: float,
    geschwisterbonus_anspruchsberechtigt_fg: bool,
    elterngeld_params: dict,
) -> float:
    """Elterngeld bonus for (older) siblings.

    According to § 2a parents of siblings get a bonus.

    Parameters
    ----------
    elterngeld_basisbetrag_m
        See :func:`elterngeld_basisbetrag_m`.
    geschwisterbonus_anspruchsberechtigt_fg
        See :func:`geschwisterbonus_anspruchsberechtigt_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if geschwisterbonus_anspruchsberechtigt_fg:
        out = max(
            elterngeld_params["geschwisterbonus_aufschlag"] * elterngeld_basisbetrag_m,
            elterngeld_params["geschwisterbonus_minimum"],
        )
    else:
        out = 0.0
    return out


def elterngeld_mehrlingsbonus_m(
    _elterngeld_anz_mehrlinge_fg: int, elterngeld_params: dict
) -> float:
    """Elterngeld bonus for multiples.

    Parameters
    ----------
    _elterngeld_anz_mehrlinge_fg
        See :func:`_elterngeld_anz_mehrlinge_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return _elterngeld_anz_mehrlinge_fg * elterngeld_params["mehrlingbonus"]


def geschwisterbonus_anspruchsberechtigt_fg(
    anz_kinder_bis_2_fg: int,
    anz_kinder_bis_5_fg: int,
    elterngeld_params: dict,
) -> bool:
    """Siblings that give rise to Elterngeld siblings bonus.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    geschwister_unter_3 = (
        anz_kinder_bis_2_fg >= elterngeld_params["geschwisterbonus_altersgrenzen"][3]
    )
    geschwister_unter_6 = (
        anz_kinder_bis_5_fg >= elterngeld_params["geschwisterbonus_altersgrenzen"][6]
    )

    return geschwister_unter_3 or geschwister_unter_6


def _elterngeld_anz_mehrlinge_fg(
    anz_mehrlinge_jüngstes_kind_fg: int,
) -> int:
    """Number of multiples of the youngest child.

    Parameters
    ----------
    anz_mehrlinge_jüngstes_kind_fg
        See :func:`anz_mehrlinge_jüngstes_kind_fg`.

    Returns
    -------

    """
    out = anz_mehrlinge_jüngstes_kind_fg - 1
    return max(out, 0)
