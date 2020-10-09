from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries

def arbeitsl_geld_2_m_minus_eink_hh(
    _regelbedarf_m_vermögens_check_hh: BoolSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    arbeitsl_geld_2_eink_hh: FloatSeries
) -> FloatSeries:
    """

    Parameters
    ----------
    _regelbedarf_m_vermögens_check_hh 
        See :func:`_regelbedarf_m_vermögens_check_hh`.
    kindergeld_m_hh 
        See :func:`kindergeld_m_hh`.
    unterhaltsvors_m_hh 
        See :func:`unterhaltsvors_m_hh`.
    arbeitsl_geld_2_eink_hh 
        See :func:`arbeitsl_geld_2_eink_hh`.

    Returns
    -------

    """
    out = (
        _regelbedarf_m_vermögens_check_hh
        - arbeitsl_geld_2_eink_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return out


def wohngeld_vorrang_hh(
    wohngeld_vermögens_check_hh: BoolSeries, 
    arbeitsl_geld_2_m_minus_eink_hh: FloatSeries,
) -> BoolSeries:
    """

    Parameters
    ----------
    wohngeld_vermögens_check_hh 
        See :func:`wohngeld_vermögens_check_hh`.
    arbeitsl_geld_2_m_minus_eink_hh 
        See :func:`arbeitsl_geld_2_m_minus_eink_hh`.

    Returns
    -------

    """
    return wohngeld_vermögens_check_hh >= arbeitsl_geld_2_m_minus_eink_hh


def kinderzuschlag_vorrang_hh(
    kinderzuschlag_vermögens_check_hh: BoolSeries, 
    arbeitsl_geld_2_m_minus_eink_hh: FloatSeries
) -> BoolSeries:
    """

    Parameters
    ----------
    kinderzuschlag_vermögens_check_hh 
        See :func:`kinderzuschlag_vermögens_check_hh`.
    arbeitsl_geld_2_m_minus_eink_hh 
        See :func:`arbeitsl_geld_2_m_minus_eink_hh`.

    Returns
    -------

    """
    return kinderzuschlag_vermögens_check_hh >= arbeitsl_geld_2_m_minus_eink_hh


def wohngeld_kinderzuschlag_vorrang_hh(
    wohngeld_vermögens_check_hh: BoolSeries,
    kinderzuschlag_vermögens_check_hh: BoolSeries,
    arbeitsl_geld_2_m_minus_eink_hh: FloatSeries,
) -> BoolSeries:
    """

    Parameters
    ----------
    wohngeld_vermögens_check_hh 
        See :func:`wohngeld_vermögens_check_hh`. 
    kinderzuschlag_vermögens_check_hh 
        See :func:`kinderzuschlag_vermögens_check_hh`. 
    arbeitsl_geld_2_m_minus_eink_hh 
        See :func:`arbeitsl_geld_2_m_minus_eink_hh`. 

    Returns
    -------

    """
    sum_wohngeld_kinderzuschlag = (
        wohngeld_vermögens_check_hh + kinderzuschlag_vermögens_check_hh
    )
    return sum_wohngeld_kinderzuschlag >= arbeitsl_geld_2_m_minus_eink_hh
