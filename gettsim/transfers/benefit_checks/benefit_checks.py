from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries


def arbeitsl_geld_2_vor_vorrang_m_hh(
    regelbedarf_m_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    arbeitsl_geld_2_eink_hh: FloatSeries,
    vermögen_hh: FloatSeries,
    arbeitsl_geld_2_vermög_freib_hh: FloatSeries,
) -> FloatSeries:
    """Calculate potential basic subsistence (after income deduction and
    wealth check).

    Parameters
    ----------
    regelbedarf_m_hh
        See :func:`regelbedarf_m_hh`.
    kindergeld_m_hh
        See :func:`kindergeld_m_hh`.
    unterhaltsvors_m_hh
        See :func:`unterhaltsvors_m_hh`.
    arbeitsl_geld_2_eink_hh
        See :func:`arbeitsl_geld_2_eink_hh`.
    arbeitsl_geld_2_vermög_freib_hh
        See :func:`arbeitsl_geld_2_vermög_freib_hh`.
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.

    Returns
    -------

    """

    # Deduct income from other sources
    out = (
        regelbedarf_m_hh
        - arbeitsl_geld_2_eink_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    ).clip(lower=0)

    # Check wealth exemption
    out.loc[vermögen_hh > arbeitsl_geld_2_vermög_freib_hh] = 0

    return out


def wohngeld_vorrang_hh(
    wohngeld_vermögens_check_hh: FloatSeries,
    arbeitsl_geld_2_vor_vorrang_m_hh: FloatSeries,
) -> BoolSeries:
    """Check if housing benefit has priority.

    Parameters
    ----------
    wohngeld_vermögens_check_hh
        See :func:`wohngeld_vermögens_check_hh`.
    arbeitsl_geld_2_vor_vorrang_m_hh
        See :func:`arbeitsl_geld_2_vor_vorrang_m_hh`.

    Returns
    -------

    """
    return wohngeld_vermögens_check_hh >= arbeitsl_geld_2_vor_vorrang_m_hh


def kinderzuschl_vorrang_hh(
    kinderzuschl_vermögens_check_hh: FloatSeries,
    arbeitsl_geld_2_vor_vorrang_m_hh: FloatSeries,
) -> BoolSeries:
    """Check if child benefit has priority.

    Parameters
    ----------
    kinderzuschl_vermögens_check_hh
        See :func:`kinderzuschl_vermögens_check_hh`.
    arbeitsl_geld_2_vor_vorrang_m_hh
        See :func:`arbeitsl_geld_2_vor_vorrang_m_hh`.

    Returns
    -------

    """
    return kinderzuschl_vermögens_check_hh >= arbeitsl_geld_2_vor_vorrang_m_hh


def wohngeld_kinderzuschl_vorrang_hh(
    wohngeld_vermögens_check_hh: FloatSeries,
    kinderzuschl_vermögens_check_hh: FloatSeries,
    arbeitsl_geld_2_vor_vorrang_m_hh: FloatSeries,
) -> BoolSeries:
    """Check if housing and child benefit have priority.

    Parameters
    ----------
    wohngeld_vermögens_check_hh
        See :func:`wohngeld_vermögens_check_hh`.
    kinderzuschl_vermögens_check_hh
        See :func:`kinderzuschl_vermögens_check_hh`.
    arbeitsl_geld_2_vor_vorrang_m_hh
        See :func:`arbeitsl_geld_2_vor_vorrang_m_hh`.

    Returns
    -------

    """
    sum_wohngeld_kinderzuschl = (
        wohngeld_vermögens_check_hh + kinderzuschl_vermögens_check_hh
    )
    return sum_wohngeld_kinderzuschl >= arbeitsl_geld_2_vor_vorrang_m_hh
