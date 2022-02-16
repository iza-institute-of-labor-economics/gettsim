import numpy as np
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderzuschl_vermögens_check_hh(
    kinderzuschl_vorläufig_m_hh: FloatSeries,
    vermögen_hh: FloatSeries,
    freibetrag_vermögen_hh: FloatSeries,
) -> FloatSeries:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    kinderzuschl_vorläufig_m_hh
        See :func:`kinderzuschl_vorläufig_m_hh`.
    freibetrag_vermögen_hh
        See :func:`freibetrag_vermögen_hh`.
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.

    Returns
    -------

    """
    out = kinderzuschl_vorläufig_m_hh.copy()
    out.loc[vermögen_hh > freibetrag_vermögen_hh] = 0
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
        wohngeld_params["vermög_freib_grund"]
        + (wohngeld_params["vermög_freib_pers"] * (haushaltsgröße_hh - 1))
    )
    out.loc[~condition] = 0
    return out


def vermög_freib_arbeitsl_geld_2_hh(
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
        arbeitsl_geld_2_params["vermög_freib"]["vor_1948"]
        * alter.loc[geburtsjahr < 1948]
    )
    out.loc[(1948 <= geburtsjahr) & ~kind] = (
        arbeitsl_geld_2_params["vermög_freib"]["standard"]
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
        arbeitsl_geld_2_params["vermög_freib"]["1948_bis_1957"],
        arbeitsl_geld_2_params["vermög_freib"]["1958_bis_1963"],
        arbeitsl_geld_2_params["vermög_freib"]["nach_1963"],
        0,
    ]

    data = np.select(conditions, choices)
    out = pd.Series(0, index=geburtsjahr.index) + data

    return out.groupby(hh_id).sum()


def freibetrag_vermögen_hh(
    vermög_freib_arbeitsl_geld_2_hh: FloatSeries,
    anz_minderj_hh: IntSeries,
    haushaltsgröße_hh: IntSeries,
    max_freibetrag_vermögen_hh: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate actual exemptions.

    Parameters
    ----------
    vermög_freib_arbeitsl_geld_2_hh
        See :func:`vermög_freib_arbeitsl_geld_2_hh`.
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
        vermög_freib_arbeitsl_geld_2_hh
        + anz_minderj_hh * arbeitsl_geld_2_params["vermög_freib"]["kind"]
        + (haushaltsgröße_hh - anz_minderj_hh)
        * arbeitsl_geld_2_params["vermög_freib"]["ausstattung"]
    ).clip(upper=max_freibetrag_vermögen_hh)
    return out
