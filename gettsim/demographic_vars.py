"""This module computes demographic variables directly on the data. These information
are used throughout modules of gettsim."""
import numpy as np
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import DateTimeSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries

aggregation_demographic_vars = {
    "anz_erwachsene_tu": {"source_col": "erwachsen", "aggr": "sum"},
    "anz_erwachsene_hh": {"source_col": "erwachsen", "aggr": "sum"},
    "anz_rentner_hh": {"source_col": "rentner", "aggr": "sum"},
    "anz_kinder_hh": {"source_col": "kind", "aggr": "sum"},
    "anz_kinder_tu": {"source_col": "kind", "aggr": "sum"},
    "anz_kinder_bis_17_hh": {"source_col": "kind_bis_17", "aggr": "sum"},
    "anz_kinder_bis_6_hh": {"source_col": "kind_bis_6", "aggr": "sum"},
    "anz_kinder_bis_15_hh": {"source_col": "kind_bis_15", "aggr": "sum"},
    "anz_kinder_ab_7_bis_13_hh": {"source_col": "kind_ab_7_bis_13", "aggr": "sum"},
    "anz_kinder_ab_14_bis_24_hh": {"source_col": "kind_ab_14_bis_24", "aggr": "sum"},
    "anz_kinder_bis_10_tu": {"source_col": "kind_bis_10", "aggr": "sum"},
    "alleinerz_tu": {"source_col": "alleinerz", "aggr": "any"},
    "alleinerz_hh": {"source_col": "alleinerz", "aggr": "any"},
    "haushaltsgröße_hh": {"aggr": "count"},
    "geburtstermin_jüngstes_mitglied_hh": {
        "source_col": "geburtstermin",
        "aggr": "max",
    },
}


def kind_bis_17(alter: IntSeries, kind: BoolSeries) -> IntSeries:
    """Calculate if underage person.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (alter < 18)
    return out


def kind_bis_6(alter: IntSeries, kind: BoolSeries) -> IntSeries:
    """Calculate if child under the age of 7.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (alter <= 6)
    return out


def kind_bis_10(alter: IntSeries, kind: BoolSeries) -> IntSeries:
    """Calculate if child under the age of 11.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (alter <= 10)
    return out


def kind_bis_15(alter: IntSeries, kind: BoolSeries) -> IntSeries:
    """Calculate if child under the age of 16.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (alter <= 15)
    return out


def kind_ab_7_bis_13(alter: IntSeries, kind: BoolSeries) -> IntSeries:
    """Calculate if child between 7 and 13 years old.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (7 <= alter <= 13)
    return out


def kind_ab_14_bis_24(alter: IntSeries, kind: BoolSeries) -> IntSeries:
    """Calculate if child between 14 and 24 years old.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (14 <= alter <= 24)
    return out


def erwachsen(kind: BoolSeries) -> IntSeries:
    """Calculate if adult.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = not kind
    return out


def gemeinsam_veranlagt_tu(anz_erwachsene_tu: IntSeries) -> BoolSeries:
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
    return anz_erwachsene_tu == 2


def erwachsene_alle_rentner_hh(
    anz_erwachsene_hh: IntSeries, anz_rentner_hh: IntSeries
) -> BoolSeries:
    """Calculate if all adults in the household are pensioners.

    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.

    Returns
    -------

    """
    return anz_erwachsene_hh == anz_rentner_hh


def geburtstermin(
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


def alter_jüngstes_kind_monate_hh(
    geburtstermin_jüngstes_mitglied_hh: DateTimeSeries, elterngeld_params: dict,
) -> FloatSeries:
    """Calculate age of youngest child in months.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    geburtstermin_jüngstes_mitglied_hh
        See :func:`geburtstermin_jüngstes_mitglied_hh`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """
    date = pd.to_datetime(elterngeld_params["datum"])
    age_in_days = date - geburtstermin_jüngstes_mitglied_hh

    # # Check was formerly implemented in `check_eligibilities` for elterngeld.
    # unborn_children = age_in_days.dt.total_seconds() < 0
    # if unborn_children.any():
    #     hh_ids = hh_id[unborn_children].unique()
    #     raise ValueError(f"Households with ids {hh_ids} have unborn children.")
    return age_in_days / np.timedelta64(1, "M")
