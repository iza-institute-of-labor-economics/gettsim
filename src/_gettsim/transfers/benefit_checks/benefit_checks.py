def wohngeld_vorrang_bg(
    wohngeld_vor_vorrang_check_m_bg: float,
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
) -> bool:
    """Check if housing benefit has priority.

    Parameters
    ----------
    wohngeld_vor_vorrang_check_m_bg
        See :func:`wohngeld_vor_vorrang_check_m_bg`.
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.

    Returns
    -------

    """
    return wohngeld_vor_vorrang_check_m_bg >= arbeitsl_geld_2_vor_vorrang_m_bg


def kinderzuschl_vorrang_bg(
    _kinderzuschl_nach_vermög_check_m_bg: float,
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
) -> bool:
    """Check if child benefit has priority.

    Parameters
    ----------
    _kinderzuschl_nach_vermög_check_m_bg
        See :func:`_kinderzuschl_nach_vermög_check_m_bg`.
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.

    Returns
    -------

    """
    return _kinderzuschl_nach_vermög_check_m_bg >= arbeitsl_geld_2_vor_vorrang_m_bg


def wohngeld_kinderzuschl_vorrang_bg(
    wohngeld_vor_vorrang_check_m_bg: float,
    _kinderzuschl_nach_vermög_check_m_bg: float,
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
) -> bool:
    """Check if housing and child benefit have priority.

    Parameters
    ----------
    wohngeld_vor_vorrang_check_m_bg
        See :func:`wohngeld_vor_vorrang_check_m_bg`.
    _kinderzuschl_nach_vermög_check_m_bg
        See :func:`_kinderzuschl_nach_vermög_check_m_bg`.
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.

    Returns
    -------

    """
    sum_wohngeld_kinderzuschl = (
        wohngeld_vor_vorrang_check_m_bg + _kinderzuschl_nach_vermög_check_m_bg
    )
    return sum_wohngeld_kinderzuschl >= arbeitsl_geld_2_vor_vorrang_m_bg
