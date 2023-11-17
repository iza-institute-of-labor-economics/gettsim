def wohngeld_vorrang_hh(
    wohngeld_nach_vermög_check_m_hh: float,
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
) -> bool:
    """Check if housing benefit has priority.

    Parameters
    ----------
    wohngeld_nach_vermög_check_m_hh
        See :func:`wohngeld_nach_vermög_check_m_hh`.
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.

    Returns
    -------

    """
    return wohngeld_nach_vermög_check_m_hh >= arbeitsl_geld_2_vor_vorrang_m_bg


def kinderzuschl_vorrang_hh(
    _kinderzuschl_nach_vermög_check_m_tu: float,
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
) -> bool:
    """Check if child benefit has priority.

    Parameters
    ----------
    _kinderzuschl_nach_vermög_check_m_tu
        See :func:`_kinderzuschl_nach_vermög_check_m_tu`.
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.

    Returns
    -------

    """
    return _kinderzuschl_nach_vermög_check_m_tu >= arbeitsl_geld_2_vor_vorrang_m_bg


def wohngeld_kinderzuschl_vorrang_hh(
    wohngeld_nach_vermög_check_m_hh: float,
    _kinderzuschl_nach_vermög_check_m_tu: float,
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
) -> bool:
    """Check if housing and child benefit have priority.

    Parameters
    ----------
    wohngeld_nach_vermög_check_m_hh
        See :func:`wohngeld_nach_vermög_check_m_hh`.
    _kinderzuschl_nach_vermög_check_m_tu
        See :func:`_kinderzuschl_nach_vermög_check_m_tu`.
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.

    Returns
    -------

    """
    sum_wohngeld_kinderzuschl = (
        wohngeld_nach_vermög_check_m_hh + _kinderzuschl_nach_vermög_check_m_tu
    )
    return sum_wohngeld_kinderzuschl >= arbeitsl_geld_2_vor_vorrang_m_bg
