import numpy as np
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def regelbedarf_m_vermögens_check_hh(
    regelbedarf_m_hh: FloatSeries, unter_vermögens_freibetrag_hh: BoolSeries
) -> FloatSeries:
    """Set preliminary basic subsistence to zero if it exceeds the wealth exemption.

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
    out = regelbedarf_m_hh.copy()
    out.loc[~unter_vermögens_freibetrag_hh] = 0
    return out


def kinderzuschlag_vermögens_check_hh(
    kinderzuschlag_m_vorläufig_hh: FloatSeries,
    unter_vermögens_freibetrag_hh: BoolSeries,
) -> FloatSeries:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    kinderzuschlag_m_vorläufig_hh
        See :func:`kinderzuschlag_m_vorläufig_hh`.
    unter_vermögens_freibetrag_hh
        See :func:`unter_vermögens_freibetrag_hh`.

    Returns
    -------

    """
    out = kinderzuschlag_m_vorläufig_hh.copy()
    out.loc[~unter_vermögens_freibetrag_hh] = 0
    return out


def wohngeld_vermögens_check_hh(
    wohngeld_basis_hh: FloatSeries,
    vermögen_hh: FloatSeries,
    haushaltsgröße_hh: IntSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Set preliminary housing benefit to zero if it exceeds the wealth exemption.

    The payment depends on the wealth of the household and the number of household
    members.

    Parameters
    ----------
    wohngeld_basis_hh
        See :func:`wohngeld_basis_hh`.
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    out = wohngeld_basis_hh.copy()
    condition = vermögen_hh <= (
        wohngeld_params["vermögensfreibetrag_grund"]
        + (wohngeld_params["vermögensfreibetrag_pers"] * (haushaltsgröße_hh - 1))
    )
    out.loc[~condition] = 0
    return out


def unter_vermögens_freibetrag_hh(
    vermögen_hh: FloatSeries, freibetrag_vermögen_hh: FloatSeries
) -> BoolSeries:
    """Check if wealth is under wealth exemption.

    Parameters
    ----------
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.
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
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate exemptions based on individuals age.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = pd.Series(0, index=alter.index)
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
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate maximal wealth exemptions by year of birth.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    conditions = [
        (geburtsjahr < 1957).astype(bool),
        ((1958 <= geburtsjahr) & (geburtsjahr <= 1963)).astype(bool),
        ((1964 <= geburtsjahr) & ~kind).astype(bool),
        True,
    ]

    choices = [
        arbeitsl_geld_2_params["vermögensfreibetrag"]["1948_bis_1957"],
        arbeitsl_geld_2_params["vermögensfreibetrag"]["1958_bis_1963"],
        arbeitsl_geld_2_params["vermögensfreibetrag"]["nach_1963"],
        0,
    ]

    data = np.select(conditions, choices)
    out = pd.Series(0, index=geburtsjahr.index) + data

    return out.groupby(hh_id).sum()


def freibetrag_vermögen_hh(
    freibetrag_vermögen_anspruch_hh: FloatSeries,
    anz_minderj_hh: IntSeries,
    haushaltsgröße_hh: IntSeries,
    max_freibetrag_vermögen_hh: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate actual exemptions.

    Parameters
    ----------
    freibetrag_vermögen_anspruch_hh
        See :func:`freibetrag_vermögen_anspruch_hh`.
    anz_minderj_hh
        See basic input variable :ref:`anz_minderj_hh <anz_minderj_hh>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    max_freibetrag_vermögen_hh
        See :func:`max_freibetrag_vermögen_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

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
