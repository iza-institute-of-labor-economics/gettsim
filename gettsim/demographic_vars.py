"""This module computes demographic variables directly on the data. These information
are used throughout modules of gettsim."""
import numpy as np
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import DateTimeSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def anz_minderj_hh(hh_id: IntSeries, alter: IntSeries, kind: BoolSeries) -> IntSeries:
    """Calculate the number of underage persons in household.

    Parameters
    ----------
    hh_id : IntSeries
        See basic input variable :ref:`hh_id <hh_id>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    minderj = (alter < 18) & (alter > 0)
    return (minderj & kind).groupby(hh_id).sum()


def alleinerz_tu(tu_id: IntSeries, alleinerz: BoolSeries) -> BoolSeries:
    """Check if single parent is in tax unit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    Returns
    -------
    BoolSeries indicating single parent in tax unit.
    """
    return alleinerz.groupby(tu_id).any()


def alleinerz_hh(hh_id: IntSeries, alleinerz: BoolSeries) -> BoolSeries:
    """Check if single parent is in household.

    Parameters
    ----------
    hh_id : IntSeries
        See basic input variable :ref:`hh_id <hh_id>`.
    alleinerz : BoolSeries
        See basic input variable :ref:`alleinerz <alleinerz>`.

    Returns
    -------
    BoolSeries indicating single parent in household.
    """
    return alleinerz.groupby(hh_id).any()


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
    alter
        See basic input variable :ref:`alter <alter>`.

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
    alter
        See basic input variable :ref:`alter <alter>`.

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
    alter
        See basic input variable :ref:`alter <alter>`.

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
    alter
        See basic input variable :ref:`alter <alter>`.

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


def alle_erwachsene_sind_rentner_hh(
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


def hhsize_tu(tu_id: IntSeries) -> IntSeries:
    """Count persons in taxunit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    Returns
    -------
    IntSeries with the number of persons in taxunit per taxunit.
    """
    return tu_id.groupby(tu_id).size()


def date_of_birth(
    geburtsjahr: IntSeries, geburtsmonat: IntSeries, geburtstag: IntSeries
) -> DateTimeSeries:
    """Create date of birth datetime variable.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    geburtstag
        See basic input variable :ref:`geburtstag <geburtstag>`.

    Returns
    -------

    """
    out = pd.to_datetime(
        pd.concat(
            [
                geburtsjahr.rename("year"),
                geburtsmonat.rename("month"),
                geburtstag.rename("day"),
            ],
            axis=1,
        )
    )
    return out


def alter_jüngstes_kind(
    hh_id: IntSeries, date_of_birth: DateTimeSeries, kind: BoolSeries
) -> DateTimeSeries:
    """Calculate the age of the youngest child.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    date_of_birth
        See :func:`geburtstag`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    alter_jüngstes_kind = date_of_birth.loc[kind].groupby(hh_id).max()
    # Re-index to get NaT for households without children.
    alter_jüngstes_kind = alter_jüngstes_kind.reindex(index=hh_id.unique())
    # Replace hh_ids with timestamps and re-cast to `datetime64[ns]` if there was no kid
    # which yields object dtype.
    return hh_id.replace(alter_jüngstes_kind).astype("datetime64[ns]")


def jüngstes_kind(
    date_of_birth: DateTimeSeries, alter_jüngstes_kind: DateTimeSeries
) -> BoolSeries:
    """Determine the youngest child in each household.

    Parameters
    ----------
    date_of_birth
        See :func:`date_of_birth`.
    alter_jüngstes_kind
        See :func:`alter_jüngstes_kind`.

    Returns
    -------

    """
    return date_of_birth == alter_jüngstes_kind


def alter_jüngstes_kind_monate(
    hh_id: IntSeries, alter_jüngstes_kind: DateTimeSeries, elterngeld_params: dict
) -> FloatSeries:
    """Calculate in age of youngest child in months.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    alter_jüngstes_kind
        See :func:`alter_jüngstes_kind`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """
    date = pd.to_datetime(elterngeld_params["datum"])
    age_in_days = date - alter_jüngstes_kind

    # Check was formerly implemented in `check_eligibilities` for elterngeld.
    unborn_children = age_in_days.dt.total_seconds() < 0
    if unborn_children.any():
        hh_ids = hh_id[unborn_children].unique()
        raise ValueError(f"Households with ids {hh_ids} have unborn children.")
    return age_in_days / np.timedelta64(1, "M")
