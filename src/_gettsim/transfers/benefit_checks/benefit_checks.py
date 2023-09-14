def wohngeld_vorrang_vg(
    wohngeld_nach_vermög_check_m_vg: float,
    arbeitsl_geld_2_vor_vorrang_m_vg: float,
) -> bool:
    """Check if housing benefit has priority.

    Parameters
    ----------
    wohngeld_nach_vermög_check_m_vg
        See :func:`wohngeld_nach_vermög_check_m_vg`.
    arbeitsl_geld_2_vor_vorrang_m_vg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_vg`.

    Returns
    -------

    """
    return wohngeld_nach_vermög_check_m_vg >= arbeitsl_geld_2_vor_vorrang_m_vg


def kinderzuschl_vorrang_vg(
    _kinderzuschl_nach_vermög_check_m_tu: float,
    arbeitsl_geld_2_vor_vorrang_m_vg: float,
) -> bool:
    """Check if child benefit has priority.

    Parameters
    ----------
    _kinderzuschl_nach_vermög_check_m_tu
        See :func:`_kinderzuschl_nach_vermög_check_m_tu`.
    arbeitsl_geld_2_vor_vorrang_m_vg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_vg`.

    Returns
    -------

    """
    return _kinderzuschl_nach_vermög_check_m_tu >= arbeitsl_geld_2_vor_vorrang_m_vg


def wohngeld_kinderzuschl_vorrang_vg(
    wohngeld_nach_vermög_check_m_vg: float,
    _kinderzuschl_nach_vermög_check_m_tu: float,
    arbeitsl_geld_2_vor_vorrang_m_vg: float,
) -> bool:
    """Check if housing and child benefit have priority.

    Parameters
    ----------
    wohngeld_nach_vermög_check_m_vg
        See :func:`wohngeld_nach_vermög_check_m_vg`.
    _kinderzuschl_nach_vermög_check_m_tu
        See :func:`_kinderzuschl_nach_vermög_check_m_tu`.
    arbeitsl_geld_2_vor_vorrang_m_vg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_vg`.

    Returns
    -------

    """
    sum_wohngeld_kinderzuschl = (
        wohngeld_nach_vermög_check_m_vg + _kinderzuschl_nach_vermög_check_m_tu
    )
    return sum_wohngeld_kinderzuschl >= arbeitsl_geld_2_vor_vorrang_m_vg
