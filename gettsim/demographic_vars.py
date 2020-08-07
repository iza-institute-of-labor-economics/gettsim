"""This module provides functions to compute demographic variables."""
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def alleinerziehend_tu(tu_id: IntSeries, alleinerziehend: BoolSeries) -> BoolSeries:
    """Check if single parent is in tax unit.

    The returned pandas.Series is intdexed by the tax unit id (:ref:`tu_id`). For more
    details on tax unit Series, see the documentation on reduced Series :ref:`reduced`.

    Parameters
    ----------
    tu_id
        See :ref:`tu_id`
    alleinerziehend
        See :ref:`alleinerziehend`
    Returns
    -------
    BoolSeries indicating single parent in tax unit.
    """
    return alleinerziehend.groupby(tu_id).any()


def alleinerziehend_hh(hh_id: IntSeries, alleinerziehend: BoolSeries) -> BoolSeries:
    """Create household unit BoolSeries for single parent.

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    alleinerziehend
        See :ref:`alleinerziehend`

    Returns
    -------

    """
    return alleinerziehend.groupby(hh_id).any()


def _anz_kinder_in_tu(tu_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Create number of children per tax unit.

    Parameters
    ----------
    tu_id
        See :ref:`tu_id`
    kind
        See :ref:`kind`

    Returns
    -------

    """
    return (kind.astype(int)).groupby(tu_id).sum()


def _anz_erwachsene_tu(tu_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Create number of adults in tax unit.

    Parameters
    ----------
    tu_id
        See :ref:`tu_id`
    kind
        See :ref:`kind`

    Returns
    -------

    """
    return (~kind).astype(int).groupby(tu_id).sum()


def gemeinsam_veranlagt(tu_id: IntSeries, _anz_erwachsene_tu: IntSeries) -> BoolSeries:
    """

    Parameters
    ----------
    tu_id
        See :ref:`tu_id`.
    _anz_erwachsene_tu
        See :func:`gettsim.demograhphic_vars._anz_erwachsene_tu`.

    Returns
    -------

    """
    return tu_id.replace(_anz_erwachsene_tu) == 2


def gemeinsam_veranlagte_tu(
    tu_id: IntSeries, gemeinsam_veranlagt: BoolSeries
) -> BoolSeries:
    """Create number of households with shared tax tarif unit BoolSeries.

    Parameters
    ----------
    gemeinsam_veranlagt
    tu_id
        See :ref:`tu_id`

    Returns
    -------

    """
    return gemeinsam_veranlagt.groupby(tu_id).any()


def bruttolohn_m_tu(bruttolohn_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Create monthly wage of each individual.

    Parameters
    ----------
    bruttolohn_m
        See :ref:`bruttolohn_m`
    tu_id
        See :ref:`tu_id`

    Returns
    -------

    """
    return bruttolohn_m.groupby(tu_id).sum()


def anz_kind_zwischen_0_6_hh(
    hh_id: IntSeries, kind: BoolSeries, alter: IntSeries
) -> IntSeries:
    """Create number of children age 0-6 in households.

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    kind
        See :ref:`kind`
    alter
        See :ref:`alter`

    Returns
    -------

    """
    kind_0_bis_6 = kind & (0 <= alter) & (alter <= 6)
    return kind_0_bis_6.astype(int).groupby(hh_id).sum()


def anz_kind_zwischen_0_15_hh(
    hh_id: IntSeries, kind: BoolSeries, alter: IntSeries
) -> IntSeries:
    """Create number of children age 0-15 in households.

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    kind
        See :ref:`kind`
    alter
        See :ref:`alter`

    Returns
    -------

    """
    kind_0_bis_15 = kind & (0 <= alter) & (alter <= 15)
    return kind_0_bis_15.astype(int).groupby(hh_id).sum()


def anz_kind_zwischen_7_13_hh(
    hh_id: IntSeries, kind: BoolSeries, alter: IntSeries
) -> IntSeries:
    """Create numer of children age 7-13 in households.

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    kind
        See :ref:`kind`
    alter
        See :ref:`alter`

    Returns
    -------

    """
    kind_7_bis_13 = kind & (7 <= alter) & (alter <= 13)
    return kind_7_bis_13.astype(int).groupby(hh_id).sum()


def anz_kind_zwischen_14_24_hh(
    hh_id: IntSeries, kind: BoolSeries, alter: IntSeries
) -> IntSeries:
    """Create number of children age 7-13 in households.

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    kind
        See :ref:`kind`
    alter
        See :ref:`alter`

    Returns
    -------

    """
    kind_14_bis_24 = kind & (14 <= alter) & (alter <= 24)
    return kind_14_bis_24.astype(int).groupby(hh_id).sum()


def anz_kinder_hh(hh_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Create number of children age 0-18 in households.

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    kind
        See :ref:`kind`

    Returns
    -------

    """
    return kind.astype(int).groupby(hh_id).sum()


def anz_kinder_tu(tu_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Create number of children per tax unit.

    Parameters
    ----------
    tu_id
        See :ref:`tu_id`
    kind
        See :ref:`kind`
    Returns
    -------

    """
    return (kind.astype(int)).groupby(tu_id).sum()


def anz_erwachsene_hh(hh_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Create number of adults in households.

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    kind
        See :ref:`kind`

    Returns
    -------

    """
    return (~kind).groupby(hh_id).sum()


def kinder_in_hh(kind: BoolSeries, hh_id: IntSeries) -> BoolSeries:
    """Create number of children in households.

    Parameters
    ----------
    kind
        See :ref:`kind`
    hh_id
        See :ref:`hh_id`

    Returns
    -------

    """
    return kind.groupby(hh_id).any()


def haushaltsgröße(hh_id: IntSeries) -> IntSeries:
    """Create number of persons in households.

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`

    Returns
    -------

    """
    return hh_id.groupby(hh_id).transform("size")


def haushaltsgröße_hh(hh_id: IntSeries) -> IntSeries:
    """

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    Returns
    -------

    """
    return hh_id.groupby(hh_id).size()


def rentner_in_hh(hh_id: IntSeries, rentner: BoolSeries) -> BoolSeries:
    """

    Parameters
    ----------
    hh_id
        See :ref:`hh_id`
    rentner
        See :ref:`rentner`

    Returns
    -------

    """
    return rentner.groupby(hh_id).any()
