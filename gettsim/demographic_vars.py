"""This module computes demographic variables directly on the data. These information
are used throughout modules of gettsim."""
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def alter(geburtsjahr: IntSeries, evaluating_date: IntSeries) -> IntSeries:
    """Calculate the age of a person at an evaluating date.

    Parameters
    ----------
    geburtsjahr: IntSeries
        See basic input variable :ref: `geburtsjahr <geburtsjahr>`.
    evaluating_date: IntSeries
        See :func:`compute_taxes_and_transfers`.

    Returns
    -------

     """

     alter = evaluating_date - geburtsjahr
     return alter


def anz_minderj_hh(hh_id: IntSeries, alter: IntSeries, kind: BoolSeries) -> IntSeries:
    """Calculate the number of underage persons in household.

    Parameters
    ----------
    hh_id : IntSeries
        See basic input variable :ref:`hh_id <hh_id>`.
    alter : IntSeries
        See :func:`alter`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    minderj = (alter < 18) & (alter > 0)
    return (minderj & kind).groupby(hh_id).sum()


def alleinerziehend_tu(tu_id: IntSeries, alleinerziehend: BoolSeries) -> BoolSeries:
    """Check if single parent is in tax unit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    alleinerziehend
        See basic input variable :ref:`alleinerziehend <alleinerziehend>`.
    Returns
    -------
    BoolSeries indicating single parent in tax unit.
    """
    return alleinerziehend.groupby(tu_id).any()


def alleinerziehend_hh(hh_id: IntSeries, alleinerziehend: BoolSeries) -> BoolSeries:
    """Check if single parent is in household.

    Parameters
    ----------
    hh_id : IntSeries
        See basic input variable :ref:`hh_id <hh_id>`.
    alleinerziehend : BoolSeries
        See basic input variable :ref:`alleinerziehend <alleinerziehend>`.

    Returns
    -------
    BoolSeries indicating single parent in household.
    """
    return alleinerziehend.groupby(hh_id).any()


def anz_erwachsene_tu(tu_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Count number of adults in tax unit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------
    IntSeries with the number of adults per tax unit.
    """
    return (~kind).astype(int).groupby(tu_id).sum()


def gemeinsam_veranlagt(tu_id: IntSeries, anz_erwachsene_tu: IntSeries) -> BoolSeries:
    """Check if the tax unit consists of two wage earners.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    Returns
    -------
    BoolSeries indicating two wage earners in tax unit.
    """
    return tu_id.replace(anz_erwachsene_tu) == 2


def gemeinsam_veranlagte_tu(
    tu_id: IntSeries, gemeinsam_veranlagt: BoolSeries
) -> BoolSeries:
    """Check for each tax unit if it consists of two wage earners.

    Parameters
    ----------
    gemeinsam_veranlagt
        Return of :func:`gemeinsam_veranlagt`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------
    BoolSeries indicating for each tax unit two wage earners.
    """
    return gemeinsam_veranlagt.groupby(tu_id).any()


def bruttolohn_m_tu(bruttolohn_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Sum monthly wages in tax unit.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------
    FloatSeries with sum of monthly wages per tax unit.
    """
    return bruttolohn_m.groupby(tu_id).sum()


def anz_kind_zwischen_0_6_hh(
    hh_id: IntSeries, kind: BoolSeries, alter: IntSeries
) -> IntSeries:
    """Count children from 0 to 6.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    alter : IntSeries
        See :func:`alter`.

    Returns
    -------
    IntSeries with the number of children from 0 to 6 per household.
    """
    kind_0_bis_6 = kind & (0 <= alter) & (alter <= 6)
    return kind_0_bis_6.astype(int).groupby(hh_id).sum()


def anz_kind_zwischen_0_15_hh(
    hh_id: IntSeries, kind: BoolSeries, alter: IntSeries
) -> IntSeries:
    """Count children from 0 to 15.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    alter : IntSeries
        See :func:`alter`.

    Returns
    -------
    IntSeries with the number of children from 0 to 15 per household.
    """
    kind_0_bis_15 = kind & (0 <= alter) & (alter <= 15)
    return kind_0_bis_15.astype(int).groupby(hh_id).sum()


def anz_kind_zwischen_7_13_hh(
    hh_id: IntSeries, kind: BoolSeries, alter: IntSeries
) -> IntSeries:
    """Count children from 7 to 13.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    alter : IntSeries
        See :func:`alter`.

    Returns
    -------
    IntSeries with the number of children from 7 to 13 per household.
    """
    kind_7_bis_13 = kind & (7 <= alter) & (alter <= 13)
    return kind_7_bis_13.astype(int).groupby(hh_id).sum()


def anz_kind_zwischen_14_24_hh(
    hh_id: IntSeries, kind: BoolSeries, alter: IntSeries
) -> IntSeries:
    """Count children from 14 to 24.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    alter : IntSeries
        See :func:`alter`.

    Returns
    -------
    IntSeries with the number of children from 14 to 24 per household.
    """
    kind_14_bis_24 = kind & (14 <= alter) & (alter <= 24)
    return kind_14_bis_24.astype(int).groupby(hh_id).sum()


def anz_kinder_hh(hh_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Count children in households.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------
    IntSeries with the number of children per household.
    """
    return kind.astype(int).groupby(hh_id).sum()


def anz_kinder_tu(tu_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Count children per tax unit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    Returns
    -------
    IntSeries with the number of children per tax unit.
    """
    return (kind.astype(int)).groupby(tu_id).sum()


def anz_erwachsene_hh(hh_id: IntSeries, kind: BoolSeries) -> IntSeries:
    """Count adults in households.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------
    IntSeries with the number of adults per household.
    """
    return (~kind).groupby(hh_id).sum()


def kinder_in_hh(kind: BoolSeries, hh_id: IntSeries) -> BoolSeries:
    """Check if children are in household.

    Parameters
    ----------
    kind
        See basic input variable :ref:`kind <kind>`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------
    BoolSeries indicating children in household.
    """
    return kind.groupby(hh_id).any()


def haushaltsgröße(hh_id: IntSeries) -> IntSeries:
    """Count persons in households.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------
    IntSeries with the number of persons in household.
    """
    return hh_id.groupby(hh_id).transform("size")


def haushaltsgröße_hh(hh_id: IntSeries) -> IntSeries:
    """Count persons in households.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    Returns
    -------
    IntSeries with the number of persons in household per household.
    """
    return hh_id.groupby(hh_id).size()


def rentner_in_hh(hh_id: IntSeries, rentner: BoolSeries) -> BoolSeries:
    """Check if pensioner is in household.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------
    BoolSeries indicating pensioner in household.
    """
    return rentner.groupby(hh_id).any()


def anz_rentner_hh(hh_id: IntSeries, rentner: BoolSeries) -> IntSeries:
    """Count pensioners in household.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------
    IntSeries with the number of pensioners per household.
    """
    return rentner.groupby(hh_id).sum()


def alle_erwachsene_rentner_hh(
    anz_erwachsene_hh: IntSeries, anz_rentner_hh: IntSeries
) -> BoolSeries:
    """Calculate if all adults in the household are pensioners.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------
    IntSeries with the number of pensioners per household.
    """
    return anz_erwachsene_hh == anz_rentner_hh
