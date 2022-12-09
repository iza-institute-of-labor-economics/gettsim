"""This module computes demographic variables directly on the data.

These information are used throughout modules of gettsim.

"""
import datetime

import numpy as np


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
    "tax_unit_größe_tu": {"aggr": "count"},
    "alter_monate_jüngstes_mitglied_hh": {"source_col": "alter_monate", "aggr": "min"},
    "anz_mehrlinge_jüngstes_kind_hh": {
        "source_col": "jüngstes_kind_oder_mehrling",
        "aggr": "sum",
    },
}


def kind_bis_17(alter: int, kind: bool) -> bool:
    """Calculate if underage person.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <input_variable_table>`.
    kind
        See basic input variable :ref:`kind <input_variable_table>`.

    Returns
    -------

    """
    out = kind and (alter < 18)
    return out


def kind_bis_6(alter: int, kind: bool) -> bool:
    """Calculate if child under the age of 7.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <input_variable_table>`.
    kind
        See basic input variable :ref:`kind <input_variable_table>`.

    Returns
    -------

    """
    out = kind and (alter <= 6)
    return out


def kind_bis_10(alter: int, kind: bool) -> bool:
    """Calculate if child under the age of 11.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <input_variable_table>`.
    kind
        See basic input variable :ref:`kind <input_variable_table>`.

    Returns
    -------

    """
    out = kind and (alter <= 10)
    return out


def kind_bis_15(alter: int, kind: bool) -> bool:
    """Calculate if child under the age of 16.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <input_variable_table>`.
    kind
        See basic input variable :ref:`kind <input_variable_table>`.

    Returns
    -------

    """
    out = kind and (alter <= 15)
    return out


def kind_ab_7_bis_13(alter: int, kind: bool) -> bool:
    """Calculate if child between 7 and 13 years old.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <input_variable_table>`.
    kind
        See basic input variable :ref:`kind <input_variable_table>`.

    Returns
    -------

    """
    out = kind and (7 <= alter <= 13)
    return out


def kind_ab_14_bis_24(alter: int, kind: bool) -> bool:
    """Calculate if child between 14 and 24 years old.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <input_variable_table>`.
    kind
        See basic input variable :ref:`kind <input_variable_table>`.

    Returns
    -------

    """
    out = kind and (14 <= alter <= 24)
    return out


def erwachsen(kind: bool) -> bool:
    """Calculate if adult.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <input_variable_table>`.
    kind
        See basic input variable :ref:`kind <input_variable_table>`.

    Returns
    -------

    """
    out = not kind
    return out


def gemeinsam_veranlagt_tu(anz_erwachsene_tu: int) -> bool:
    """Check if the tax unit consists of two wage earners.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <input_variable_table>`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    Returns
    -------
    Boolean indicating two wage earners in tax unit.

    """
    return anz_erwachsene_tu == 2


def erwachsene_alle_rentner_hh(anz_erwachsene_hh: int, anz_rentner_hh: int) -> bool:
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


def geburtsdatum(geburtsjahr: int, geburtsmonat: int, geburtstag: int) -> np.datetime64:
    """Create date of birth datetime variable.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <input_variable_table>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <input_variable_table>`.
    geburtstag
        See basic input variable :ref:`geburtstag <input_variable_table>`.

    Returns
    -------

    """
    out = np.datetime64(
        datetime.datetime(geburtsjahr, geburtsmonat, geburtstag)
    ).astype("datetime64[D]")
    return out


def alter_monate(geburtsdatum: np.datetime64, elterngeld_params: dict) -> float:
    """Calculate age of youngest child in months.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <input_variable_table>`.
    geburtsdatum
        See :func:`geburtsdatum`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <input_variable_table>`.
    Returns
    -------

    """
    # ToDo: Find out why geburtsdatum need to be cast to datetime64 again. It
    # ToDo: should already have this type based on the function above
    age_in_days = elterngeld_params["datum"] - np.datetime64(geburtsdatum)

    out = age_in_days / 30.436875
    return out.astype(float)


def jüngstes_kind_oder_mehrling(
    alter_monate: float,
    alter_monate_jüngstes_mitglied_hh: float,
    kind: bool,
) -> bool:
    """Check if person is the youngest child in the household or a twin, triplet, etc.
    of the youngest child.

    # ToDo: replace kind by some age restriction
    # ToDo: Check definition as relevant for Elterngeld. Currently, it is calculated as
    # ToDo: age not being larger than 0.1 of a month

    Parameters
    ----------
    alter_monate
        See :func:`alter_monate`.
    alter_monate_jüngstes_mitglied_hh
        See :func:`alter_monate_jüngstes_mitglied_hh`.
    kind
        See basic input variable :ref:`kind <input_variable_table>`.

    Returns
    -------

    """
    out = (alter_monate - alter_monate_jüngstes_mitglied_hh < 0.1) and kind
    return out


def eltern(
    erwachsen: bool,
    kindergeld_anspruch: bool,
) -> bool:
    """Check if person in the tax unit is considered a parent or the parent's spouse.

    Parameters
    ----------
    erwachsen
        See :func:`erwachsen`.
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.

    Returns
    -------

    """

    out = (erwachsen) and (not kindergeld_anspruch)
    return out
