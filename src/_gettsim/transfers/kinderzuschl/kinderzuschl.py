"""Kinderzuschlag / Additional Child Benefit.

"""

from _gettsim.shared import policy_info


def kinderzuschl_m_bg(
    _kinderzuschl_nach_vermög_check_m_bg: float,
    kinderzuschl_vorrang_bg: bool,
    wohngeld_kinderzuschl_vorrang_hh: bool,
    anz_rentner_hh: int,
) -> float:
    """Aggregate child benefit on household level.

    Parameters
    ----------
    _kinderzuschl_nach_vermög_check_m_bg
        See :func:`_kinderzuschl_nach_vermög_check_m_bg`.
    kinderzuschl_vorrang_bg
        See :func:`kinderzuschl_vorrang_bg`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.

    Returns
    -------

    """
    if ((not kinderzuschl_vorrang_bg) and (not wohngeld_kinderzuschl_vorrang_hh)) or (
        anz_rentner_hh > 0
    ):
        out = 0.0
    else:
        out = _kinderzuschl_nach_vermög_check_m_bg

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
) -> float:
    """Calculate Kinderzuschlag since 2005 until 06/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold and net income needs to be below the maximum income
    threshold.

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

    Returns
    -------

    """

    # Check if parental income is in income range for child benefit.
    if (kinderzuschl_bruttoeink_eltern_m_bg >= kinderzuschl_eink_min_m_bg) and (
        kinderzuschl_eink_eltern_m_bg <= kinderzuschl_eink_max_m_bg
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
) -> float:
    """Calculate Kinderzuschlag since 07/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold.

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

    Returns
    -------

    """
    if kinderzuschl_bruttoeink_eltern_m_bg >= kinderzuschl_eink_min_m_bg:
        out = max(
            kinderzuschl_kindereink_abzug_m_bg - kinderzuschl_eink_anrechn_m_bg, 0.0
        )
    else:
        out = 0.0

    return out
