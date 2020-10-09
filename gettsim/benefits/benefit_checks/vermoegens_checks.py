import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def _regelbedarf_m_vermögens_check_hh(
        regelbedarf_m_hh: FloatSeries, 
        unter_vermögens_freibetrag_hh: BoolSeries) -> BoolSeries:
    """Set regelbedarf_m to zero if it exceeds the wealth exemption.

    If wealth exceeds the exemption, set benefits to zero (since ALG2 is not yet
    calculated, just set the need to zero)

    Parameters
    ----------
    regelbedarf_m_hh 
        See :func:`regelbedarf_m_hh`.
    unter_vermögens_freibetrag_hh 
        See :func:`unter_vermögens_freibetrag_hh`.

    Returns
    -------

    """
    regelbedarf_m_hh.loc[~unter_vermögens_freibetrag_hh] = 0
    return regelbedarf_m_hh


def kinderzuschlag_vermögens_check_hh(
    kinderzuschlag_m_vorläufig_hh: FloatSeries, 
    unter_vermögens_freibetrag_hh: BoolSeries
) -> BoolSeries:
    """Set kinderzuschlag_temp to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    kinderzuschlag_m_vorläufig_hh 
        See :func:`kinderzuschlag_m_vorläufig_hh`. 
    unter_vermögens_freibetrag_hh 
        See :func:`unter_vermögens_freibetrag_hh`.

    Returns
    -------

    """

    kinderzuschlag_m_vorläufig_hh.loc[~unter_vermögens_freibetrag_hh] = 0
    return kinderzuschlag_m_vorläufig_hh


def wohngeld_vermögens_check_hh(
        wohngeld_basis_hh: FloatSeries, 
        vermögen_hh: FloatSeries, 
        haushaltsgröße_hh: IntSeries) -> BoolSeries:
    """Calculate a lump sum payment for wohngeld

    The payment depends on the wealth of the household and the number of household
    members.

    60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)

    TODO: Need to write numbers to params.

    Parameters
    ----------
    wohngeld_basis_hh 
        See :func:`wohngeld_basis_hh`.
    vermögen_hh 
        See :refs:`vermögen_hh`. 
    haushaltsgröße_hh 
        See :func:`haushaltsgröße_hh`.

    Returns
    -------

    """
    condition = vermögen_hh <= (60_000 + (30_000 * (haushaltsgröße_hh - 1)))
    wohngeld_basis_hh.loc[~condition] = 0
    return wohngeld_basis_hh


def unter_vermögens_freibetrag_hh(
        vermögen_hh: FloatSeries, 
        freibetrag_vermögen_hh: FloatSeries) -> BoolSeries:
    """

    Parameters
    ----------
    vermögen_hh 
        See :ref:`vermögen_hh`. 
    freibetrag_vermögen_hh 
        See :func:`freibetrag_vermögen_hh`. 

    Returns
    -------

    """
    return vermögen_hh <= freibetrag_vermögen_hh


def freibetrag_vermögen_anspruch_hh(
    hh_id: IntSeries, 
    kind: BoolSeries, 
    alter: IntSeries, 
    geburtsjahr: IntSeries, 
    arbeitsl_geld_2_params: dict
):
    """Calculate exemptions based on individuals age.

    Parameters
    ----------
    hh_id 
        See :ref:`hh_id`. 
    kind 
        See :ref:`kind`. 
    alter 
        See :ref:`alter`. 
    geburtsjahr 
        See :ref:`geburtsjahr`. 
    arbeitsl_geld_2_params 
        See :ref:`arbeitsl_geld_2_params`. 

    Returns
    -------

    """

    out = alter * 0
    out.loc[geburtsjahr < 1948] = (
        arbeitsl_geld_2_params["vermögensfreibetrag"]["vor_1948"]
        * alter.loc[geburtsjahr < 1948]
    )
    out.loc[(1948 <= geburtsjahr) & ~kind] = (
        arbeitsl_geld_2_params["vermögensfreibetrag"]["standard"]
        * alter.loc[(1948 <= geburtsjahr) & ~kind]
    )

    return out.groupby(hh_id).sum()


def max_freibetrag_vermögen_hh(
        hh_id: IntSeries, 
        geburtsjahr: IntSeries, 
        kind: BoolSeries, 
        arbeitsl_geld_2_params: dict) -> FloatSeries:
    """

    Parameters
    ----------
    hh_id 
        See :ref:`hh_id`. 
    geburtsjahr 
        See :ref:`geburtsjahr`. 
    kind 
        See :ref:`kind`. 
    arbeitsl_geld_2_params 
        See :ref:`arbeitsl_geld_2_params`.

    Returns
    -------

    """
    conditions = [
        geburtsjahr < 1957,
        (1958 <= geburtsjahr) & (geburtsjahr <= 1963),
        (1964 <= geburtsjahr) & ~kind,
        True,
    ]

    choices = [
        arbeitsl_geld_2_params["vermögensfreibetrag"]["1948_bis_1957"],
        arbeitsl_geld_2_params["vermögensfreibetrag"]["1958_bis_1963"],
        arbeitsl_geld_2_params["vermögensfreibetrag"]["nach_1963"],
        0,
    ]

    data = np.select(conditions, choices)
    out = geburtsjahr * 0.0 + data

    return out.groupby(hh_id).sum()


def freibetrag_vermögen_hh(
    freibetrag_vermögen_anspruch_hh: FloatSeries,
    anz_minderj_hh: IntSeries,
    haushaltsgröße_hh: IntSeries,
    max_freibetrag_vermögen_hh: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """

    Parameters
    ----------
    freibetrag_vermögen_anspruch_hh 
        See :func:`freibetrag_vermögen_anspruch_hh`. 
    anz_minderj_hh 
        See :func:`anz_minderj_hh`. 
    haushaltsgröße_hh 
        See :func:`haushaltsgröße_hh`. 
    max_freibetrag_vermögen_hh 
        See :func:`max_freibetrag_vermögen_hh`. 
    arbeitsl_geld_2_params 
        See :ref:`arbeitsl_geld_2_params`.

    Returns
    -------

    """
    out = (
        freibetrag_vermögen_anspruch_hh
        + anz_minderj_hh * arbeitsl_geld_2_params["vermögensfreibetrag"]["kind"]
        + (haushaltsgröße_hh - anz_minderj_hh)
        * arbeitsl_geld_2_params["vermögensfreibetrag"]["ausstattung"]
    ).clip(upper=max_freibetrag_vermögen_hh)
    return out
