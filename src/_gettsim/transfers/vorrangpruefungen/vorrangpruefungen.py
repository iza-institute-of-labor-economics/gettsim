"""Priority checks of transfers against each other."""

aggregate_by_group_benefit_checks = {
    "wohngeld_vorrang_wthh": {
        "source_col": "wohngeld_vorrang_bg",
        "aggr": "any",
    },
    "wohngeld_kinderzuschlag_vorrang_wthh": {
        "source_col": "wohngeld_kinderzuschlag_vorrang_bg",
        "aggr": "any",
    },
}


def wohngeld_vorrang_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_eink_m_bg: float,
    wohngeld__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if housing benefit has priority.

    Housing benefit has priority if the sum of housing benefit and income covers the
    needs according to SGB II of the Bedarfsgemeinschaft.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_eink_m_bg
        See :func:`arbeitsl_geld_2_eink_m_bg`.
    wohngeld__anspruchshöhe_m_bg
        See :func:`wohngeld__anspruchshöhe_m_bg`.

    Returns
    -------

    """
    return (
        arbeitsl_geld_2_eink_m_bg + wohngeld__anspruchshöhe_m_bg
        >= arbeitsl_geld_2_regelbedarf_m_bg
    )


def kinderzuschlag_vorrang_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_eink_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if child benefit has priority.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_eink_m_bg
        See :func:`arbeitsl_geld_2_eink_m_bg`.
    kinderzuschlag__anspruchshöhe_m_bg
        See :func:`kinderzuschlag__anspruchshöhe_m_bg`.

    Returns
    -------

    """
    return (
        arbeitsl_geld_2_eink_m_bg + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitsl_geld_2_regelbedarf_m_bg
    )


def wohngeld_kinderzuschlag_vorrang_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_eink_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
    wohngeld__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if housing and child benefit have priority.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_eink_m_bg
        See :func:`arbeitsl_geld_2_eink_m_bg`.
    kinderzuschlag__anspruchshöhe_m_bg
        See :func:`kinderzuschlag__anspruchshöhe_m_bg`.
    wohngeld__anspruchshöhe_m_bg
        See :func:`wohngeld__anspruchshöhe_m_bg`.

    Returns
    -------

    """

    return (
        arbeitsl_geld_2_eink_m_bg
        + wohngeld__anspruchshöhe_m_bg
        + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitsl_geld_2_regelbedarf_m_bg
    )
