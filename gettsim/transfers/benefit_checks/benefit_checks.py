from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries


def wohngeld_vorrang_hh(
    wohngeld_nach_vermög_check_hh: FloatSeries,
    arbeitsl_geld_2_vor_vorrang_m_hh: FloatSeries,
) -> BoolSeries:
    """Check if housing benefit has priority.

    Parameters
    ----------
    wohngeld_nach_vermög_check_hh
        See :func:`wohngeld_nach_vermög_check_hh`.
    arbeitsl_geld_2_vor_vorrang_m_hh
        See :func:`arbeitsl_geld_2_vor_vorrang_m_hh`.

    Returns
    -------

    """
    return wohngeld_nach_vermög_check_hh >= arbeitsl_geld_2_vor_vorrang_m_hh


def kinderzuschl_vorrang_hh(
    kinderzuschl_nach_vermög_check_hh: FloatSeries,
    arbeitsl_geld_2_vor_vorrang_m_hh: FloatSeries,
) -> BoolSeries:
    """Check if child benefit has priority.

    Parameters
    ----------
    kinderzuschl_nach_vermög_check_hh
        See :func:`kinderzuschl_nach_vermög_check_hh`.
    arbeitsl_geld_2_vor_vorrang_m_hh
        See :func:`arbeitsl_geld_2_vor_vorrang_m_hh`.

    Returns
    -------

    """
    return kinderzuschl_nach_vermög_check_hh >= arbeitsl_geld_2_vor_vorrang_m_hh


def wohngeld_kinderzuschl_vorrang_hh(
    wohngeld_nach_vermög_check_hh: FloatSeries,
    kinderzuschl_nach_vermög_check_hh: FloatSeries,
    arbeitsl_geld_2_vor_vorrang_m_hh: FloatSeries,
) -> BoolSeries:
    """Check if housing and child benefit have priority.

    Parameters
    ----------
    wohngeld_nach_vermög_check_hh
        See :func:`wohngeld_nach_vermög_check_hh`.
    kinderzuschl_nach_vermög_check_hh
        See :func:`kinderzuschl_nach_vermög_check_hh`.
    arbeitsl_geld_2_vor_vorrang_m_hh
        See :func:`arbeitsl_geld_2_vor_vorrang_m_hh`.

    Returns
    -------

    """
    sum_wohngeld_kinderzuschl = (
        wohngeld_nach_vermög_check_hh + kinderzuschl_nach_vermög_check_hh
    )
    return sum_wohngeld_kinderzuschl >= arbeitsl_geld_2_vor_vorrang_m_hh
