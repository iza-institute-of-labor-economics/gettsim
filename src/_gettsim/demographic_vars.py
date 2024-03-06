"""This module computes demographic variables directly on the data.

These information are used throughout modules of gettsim.

"""

import datetime

import numpy

from _gettsim.config import SUPPORTED_GROUPINGS


def _add_grouping_suffixes_to_keys(group_dict: dict[str, dict]) -> dict[str, dict]:
    """Add grouping suffixes to keys of a dictionary.

    Parameters
    ----------
    group_dict
        Dictionary with keys to be suffixed.

    Returns
    -------
    Dictionary with suffixed keys.
    """
    out = {}

    for key, value in group_dict.items():
        for suffix in SUPPORTED_GROUPINGS:
            new_key = key + "_" + suffix
            out[new_key] = value

    return out


aggregate_by_group_demographic_vars = _add_grouping_suffixes_to_keys(
    {
        "anz_erwachsene": {"source_col": "erwachsen", "aggr": "sum"},
        "anz_rentner": {"source_col": "rentner", "aggr": "sum"},
        "anz_kinder": {"source_col": "kind", "aggr": "sum"},
        "anz_personen": {"aggr": "count"},
        "anz_kinder_bis_5": {"source_col": "kind_bis_5", "aggr": "sum"},
        "anz_kinder_bis_6": {"source_col": "kind_bis_6", "aggr": "sum"},
        "anz_kinder_bis_15": {"source_col": "kind_bis_15", "aggr": "sum"},
        "anz_kinder_bis_17": {"source_col": "kind_bis_17", "aggr": "sum"},
        "anz_kinder_ab_6_bis_13": {"source_col": "kind_ab_6_bis_13", "aggr": "sum"},
        "anz_kinder_ab_14_bis_24": {"source_col": "kind_ab_14_bis_24", "aggr": "sum"},
        "anz_kinder_ab_14_bis_17": {"source_col": "kind_ab_14_bis_17", "aggr": "sum"},
        "anz_kinder_ab_18_bis_24": {"source_col": "kind_ab_18_bis_24", "aggr": "sum"},
        "alleinerz": {"source_col": "alleinerz", "aggr": "any"},
        "haushaltsgröße": {"aggr": "count"},
        "tax_unit_größe": {"aggr": "count"},
        "alter_monate_jüngstes_mitglied": {"source_col": "alter_monate", "aggr": "min"},
        "anz_mehrlinge_jüngstes_kind": {
            "source_col": "jüngstes_kind_oder_mehrling",
            "aggr": "sum",
        },
    }
)


def kind_bis_5(alter: int, kind: bool) -> bool:
    """Calculate if child under the age of 6.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (alter <= 5)
    return out


def kind_bis_6(alter: int, kind: bool) -> bool:
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


def kind_bis_12(alter: int, kind: bool) -> bool:
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


def kind_bis_15(alter: int, kind: bool) -> bool:
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


def kind_bis_17(alter: int, kind: bool) -> bool:
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
    out = kind and (alter <= 17)
    return out


def kind_ab_6_bis_13(alter: int, kind: bool) -> bool:
    """Calculate if child between 6 and 13 years old.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (6 <= alter <= 13)
    return out


def kind_ab_14_bis_24(alter: int, kind: bool) -> bool:
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


def kind_ab_14_bis_17(alter: int, kind: bool) -> bool:
    """Calculate if child between 14 and 17 years old.
    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    Returns
    -------
    """
    out = kind and (14 <= alter <= 17)
    return out


def kind_ab_18_bis_24(alter: int, kind: bool) -> bool:
    """Calculate if child between 18 and 24 years old.
    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    Returns
    -------
    """
    out = kind and (18 <= alter <= 24)
    return out


def erwachsen(kind: bool) -> bool:
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


def geburtsdatum(
    geburtsjahr: int, geburtsmonat: int, geburtstag: int
) -> numpy.datetime64:
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
    out = numpy.datetime64(
        datetime.datetime(geburtsjahr, geburtsmonat, geburtstag)
    ).astype("datetime64[D]")
    return out


def alter_monate(geburtsdatum: numpy.datetime64, elterngeld_params: dict) -> float:
    """Calculate age of youngest child in months.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    geburtsdatum
        See :func:`geburtsdatum`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """

    # TODO(@hmgaudecker): Remove explicit cast when vectorisation is enabled.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/515
    age_in_days = elterngeld_params["datum"] - numpy.datetime64(geburtsdatum)

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
        See basic input variable :ref:`kind <kind>`.

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


def birthdate_decimal(
    geburtsjahr: int,
    geburtsmonat: int,
) -> float:
    """Combines birthyear and birth month to decimal number of
    birthdate with monthly precision, as required for pension
    benefit calculation

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.

    Returns
    -------
    Birthdate with monthly precision as float.

    """
    out = geburtsjahr + (geburtsmonat - 1) / 12

    return out
