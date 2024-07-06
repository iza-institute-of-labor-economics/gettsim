"""Kinderzuschlag / Additional Child Benefit.

"""

from _gettsim.shared import policy_info


def kinderzuschl_m_bg(
    kinderzuschl_anspruchshöhe_m_bg: float,
    erwachsene_alle_rentner_hh: bool,
    wohngeld_kinderzuschl_statt_arbeitsl_geld_2: bool,
) -> float:
    """Aggregate child benefit on Bedarfsgemeinschaft level.

    Parameters
    ----------
    kinderzuschl_anspruchshöhe_m_bg
        See :func:`kinderzuschl_anspruchshöhe_m_bg`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh`.
    wohngeld_kinderzuschl_statt_arbeitsl_geld_2
        See :func:`wohngeld_kinderzuschl_statt_arbeitsl_geld_2`.

    Returns
    -------

    """
    if wohngeld_kinderzuschl_statt_arbeitsl_geld_2 and not erwachsene_alle_rentner_hh:
        out = kinderzuschl_anspruchshöhe_m_bg
    else:
        out = 0.0

    return out


def kinderzuschl_anspruchshöhe_m(
    kinderzuschl_anspruchshöhe_m_bg: float,
    anz_personen_bg: int,
) -> float:
    """Kinderzuschlag on individual level.

    Target necessary for aggregation to wthh level.

    Parameters
    ----------
    kinderzuschl_anspruchshöhe_m_bg
        See :func:`kinderzuschl_anspruchshöhe_m_bg`.
    anz_personen_bg
        See :func:`anz_personen_bg`.

    Returns
    -------

    """
    return kinderzuschl_anspruchshöhe_m_bg / anz_personen_bg


def kinderzuschl_anspruchshöhe_m_bg(
    _kinderzuschl_vor_vermög_check_m_bg: float,
    vermögen_bedürft_bg: float,
    kinderzuschl_vermög_freib_bg: float,
) -> float:
    """Kinderzuschlag after wealth check on Bedarfsgemeinschaft level.

    Parameters
    ----------
    _kinderzuschl_vor_vermög_check_m_bg
        See :func:`_kinderzuschl_vor_vermög_check_m_bg`.
    vermögen_bedürft_bg
        See basic input variable :ref:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.
    kinderzuschl_vermög_freib_bg
        See :func:`kinderzuschl_vermög_freib_bg`.

    Returns
    -------

    """

    if vermögen_bedürft_bg > kinderzuschl_vermög_freib_bg:
        out = max(
            _kinderzuschl_vor_vermög_check_m_bg
            - (vermögen_bedürft_bg - kinderzuschl_vermög_freib_bg),
            0.0,
        )
    else:
        out = _kinderzuschl_vor_vermög_check_m_bg
    return out


def kinderzuschl_anspruchshöhe_m_fg(
    _kinderzuschl_vor_vermög_check_m_fg: float,
    vermögen_bedürft_fg: float,
    kinderzuschl_vermög_freib_fg: float,
) -> float:
    """Kinderzuschlag after wealth check on Familiengemeinschaft level.

    Parameters
    ----------
    _kinderzuschl_vor_vermög_check_m_fg
        See :func:`_kinderzuschl_vor_vermög_check_m_fg`.
    vermögen_bedürft_fg
        See basic input variable :ref:`vermögen_bedürft_fg <vermögen_bedürft_fg>`.
    kinderzuschl_vermög_freib_fg
        See :func:`kinderzuschl_vermög_freib_fg`.

    Returns
    -------

    """

    if vermögen_bedürft_fg > kinderzuschl_vermög_freib_fg:
        out = max(
            _kinderzuschl_vor_vermög_check_m_fg
            - (vermögen_bedürft_fg - kinderzuschl_vermög_freib_fg),
            0.0,
        )
    else:
        out = _kinderzuschl_vor_vermög_check_m_fg
    return out


@policy_info(
    end_date="2019-06-30",
    name_in_dag="_kinderzuschl_vor_vermög_check_m_bg",
)
def _kinderzuschl_vor_vermög_check_m_bg_check_eink_max(  # noqa: PLR0913
    kinderzuschl_bruttoeink_eltern_m_bg: float,
    kinderzuschl_eink_eltern_m_bg: float,
    kinderzuschl_eink_min_m_bg: float,
    kinderzuschl_eink_max_m_bg: float,
    kinderzuschl_kindereink_abzug_m_bg: float,
    kinderzuschl_eink_anrechn_m_bg: float,
    anz_personen_bg: int,
) -> float:
    """Calculate Kinderzuschlag since 2005 until 06/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold and net income needs to be below the maximum income
    threshold.

    Kinderzuschlag is only paid out if parents are part of the BG (anz_personen_bg > 1).

    Parameters
    ----------
    kinderzuschl_bruttoeink_eltern_m_bg
        See :func:`kinderzuschl_bruttoeink_eltern_m_bg`.
    kinderzuschl_eink_eltern_m_bg
        See :func:`kinderzuschl_eink_eltern_m_bg`.
    kinderzuschl_eink_min_m_bg
        See :func:`kinderzuschl_eink_min_m_bg`.
    kinderzuschl_eink_max_m_bg
        See :func:`kinderzuschl_eink_max_m_bg`.
    kinderzuschl_kindereink_abzug_m_bg
        See :func:`kinderzuschl_kindereink_abzug_m_bg`.
    kinderzuschl_eink_anrechn_m_bg
        See :func:`kinderzuschl_eink_anrechn_m_bg`.
    anz_personen_bg
        See :func:`anz_personen_bg`.

    Returns
    -------

    """

    # Check if parental income is in income range for child benefit.
    if (
        (kinderzuschl_bruttoeink_eltern_m_bg >= kinderzuschl_eink_min_m_bg)
        and (kinderzuschl_eink_eltern_m_bg <= kinderzuschl_eink_max_m_bg)
        and anz_personen_bg > 1
    ):
        out = max(
            kinderzuschl_kindereink_abzug_m_bg - kinderzuschl_eink_anrechn_m_bg, 0.0
        )
    else:
        out = 0.0

    return out


@policy_info(start_date="2019-07-01")
def _kinderzuschl_vor_vermög_check_m_bg(
    kinderzuschl_bruttoeink_eltern_m_bg: float,
    kinderzuschl_eink_min_m_bg: float,
    kinderzuschl_kindereink_abzug_m_bg: float,
    kinderzuschl_eink_anrechn_m_bg: float,
    anz_personen_bg: int,
) -> float:
    """Calculate Kinderzuschlag since 07/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold.

    Kinderzuschlag is only paid out if parents are part of the BG (anz_personen_bg > 1).


    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kinderzuschl_bruttoeink_eltern_m_bg
        See :func:`kinderzuschl_bruttoeink_eltern_m_bg`.
    kinderzuschl_eink_min_m_bg
        See :func:`kinderzuschl_eink_min_m_bg`.
    kinderzuschl_kindereink_abzug_m_bg
        See :func:`kinderzuschl_kindereink_abzug_m_bg`.
    kinderzuschl_eink_anrechn_m_bg
        See :func:`kinderzuschl_eink_anrechn_m_bg`.
    anz_personen_bg
        See :func:`anz_personen_bg`.

    Returns
    -------

    """
    if (
        kinderzuschl_bruttoeink_eltern_m_bg >= kinderzuschl_eink_min_m_bg
    ) and anz_personen_bg > 1:
        out = max(
            kinderzuschl_kindereink_abzug_m_bg - kinderzuschl_eink_anrechn_m_bg, 0.0
        )
    else:
        out = 0.0

    return out


@policy_info(
    end_date="2019-06-30",
    name_in_dag="_kinderzuschl_vor_vermög_check_m_fg",
)
def _kinderzuschl_vor_vermög_check_m_fg_check_eink_max(  # noqa: PLR0913
    kinderzuschl_bruttoeink_eltern_m_fg: float,
    kinderzuschl_eink_eltern_m_fg: float,
    kinderzuschl_eink_min_m_fg: float,
    kinderzuschl_eink_max_m_fg: float,
    kinderzuschl_kindereink_abzug_m_fg: float,
    kinderzuschl_eink_anrechn_m_fg: float,
    anz_personen_fg: int,
) -> float:
    """Calculate Kinderzuschlag since 2005 until 06/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold and net income needs to be below the maximum income
    threshold.

    Kinderzuschlag is only paid out if parents are part of the BG (anz_personen_fg > 1).

    Parameters
    ----------
    kinderzuschl_bruttoeink_eltern_m_fg
        See :func:`kinderzuschl_bruttoeink_eltern_m_fg`.
    kinderzuschl_eink_eltern_m_fg
        See :func:`kinderzuschl_eink_eltern_m_fg`.
    kinderzuschl_eink_min_m_fg
        See :func:`kinderzuschl_eink_min_m_fg`.
    kinderzuschl_eink_max_m_fg
        See :func:`kinderzuschl_eink_max_m_fg`.
    kinderzuschl_kindereink_abzug_m_fg
        See :func:`kinderzuschl_kindereink_abzug_m_fg`.
    kinderzuschl_eink_anrechn_m_fg
        See :func:`kinderzuschl_eink_anrechn_m_fg`.
    anz_personen_fg
        See :func:`anz_personen_fg`.

    Returns
    -------

    """

    # Check if parental income is in income range for child benefit.
    if (
        (kinderzuschl_bruttoeink_eltern_m_fg >= kinderzuschl_eink_min_m_fg)
        and (kinderzuschl_eink_eltern_m_fg <= kinderzuschl_eink_max_m_fg)
        and anz_personen_fg > 1
    ):
        out = max(
            kinderzuschl_kindereink_abzug_m_fg - kinderzuschl_eink_anrechn_m_fg, 0.0
        )
    else:
        out = 0.0

    return out


@policy_info(start_date="2019-07-01")
def _kinderzuschl_vor_vermög_check_m_fg(
    kinderzuschl_bruttoeink_eltern_m_fg: float,
    kinderzuschl_eink_min_m_fg: float,
    kinderzuschl_kindereink_abzug_m_fg: float,
    kinderzuschl_eink_anrechn_m_fg: float,
    anz_personen_fg: int,
) -> float:
    """Calculate Kinderzuschlag since 07/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold.

    Kinderzuschlag is only paid out if parents are part of the BG (anz_personen_fg > 1).


    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kinderzuschl_bruttoeink_eltern_m_fg
        See :func:`kinderzuschl_bruttoeink_eltern_m_fg`.
    kinderzuschl_eink_min_m_fg
        See :func:`kinderzuschl_eink_min_m_fg`.
    kinderzuschl_kindereink_abzug_m_fg
        See :func:`kinderzuschl_kindereink_abzug_m_fg`.
    kinderzuschl_eink_anrechn_m_fg
        See :func:`kinderzuschl_eink_anrechn_m_fg`.
    anz_personen_fg
        See :func:`anz_personen_fg`.

    Returns
    -------

    """
    if (
        kinderzuschl_bruttoeink_eltern_m_fg >= kinderzuschl_eink_min_m_fg
    ) and anz_personen_fg > 1:
        out = max(
            kinderzuschl_kindereink_abzug_m_fg - kinderzuschl_eink_anrechn_m_fg, 0.0
        )
    else:
        out = 0.0

    return out
