"""This module computes demographic variables directly on the data.

These information are used throughout modules of gettsim.

"""

import datetime

import numpy

from _gettsim.aggregation import AggregateByGroupSpec, AggregateByPIDSpec
from _gettsim.config import SUPPORTED_GROUPINGS
from _gettsim.functions.policy_function import policy_function
from _gettsim.shared import join_numpy


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
        "anzahl_erwachsene": AggregateByGroupSpec(source_col="erwachsen", aggr="sum"),
        "anzahl_rentner": AggregateByGroupSpec(source_col="rentner", aggr="sum"),
        "anzahl_kinder": AggregateByGroupSpec(source_col="kind", aggr="sum"),
        "anzahl_personen": AggregateByGroupSpec(aggr="count"),
        "anzahl_kinder_bis_2": AggregateByGroupSpec(
            source_col="kind_bis_2", aggr="sum"
        ),
        "anzahl_kinder_bis_5": AggregateByGroupSpec(
            source_col="kind_bis_5", aggr="sum"
        ),
        "anzahl_kinder_bis_6": AggregateByGroupSpec(
            source_col="kind_bis_6", aggr="sum"
        ),
        "anzahl_kinder_bis_15": AggregateByGroupSpec(
            source_col="kind_bis_15", aggr="sum"
        ),
        "anzahl_kinder_bis_17": AggregateByGroupSpec(
            source_col="kind_bis_17", aggr="sum"
        ),
        "alleinerziehend": AggregateByGroupSpec(source_col="alleinerz", aggr="any"),
        "alter_monate_jüngstes_mitglied": AggregateByGroupSpec(
            source_col="alter_monate", aggr="min"
        ),
        "anzahl_mehrlinge_jüngstes_kind": AggregateByGroupSpec(
            source_col="jüngstes_kind_oder_mehrling",
            aggr="sum",
        ),
    }
)


aggregation_specs = {
    "anzahl_kinder_bis_24_elternteil_1": AggregateByPIDSpec(
        p_id_to_aggregate_by=(
            "einkommensteuer__freibetraege__p_id_kinderfreibetragempfänger_1"
        ),
        source_col="kind_bis_24",
        aggr="sum",
    ),
    "anzahl_kinder_bis_24_elternteil_2": AggregateByPIDSpec(
        p_id_to_aggregate_by=(
            "einkommensteuer__freibetraege__p_id_kinderfreibetragempfänger_2"
        ),
        source_col="kind_bis_24",
        aggr="sum",
    ),
    **aggregate_by_group_demographic_vars,
}


@policy_function
def kind_bis_2(alter: int, kind: bool) -> bool:
    """Calculate if child under the age of 3.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = kind and (alter <= 2)
    return out


@policy_function
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


@policy_function
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


@policy_function
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


@policy_function
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


@policy_function
def kind_bis_24(alter: int) -> bool:
    """Child below the age of 25.

    Relevant for the calculation of the long-term care insurance contribution. It does
    not matter whether children have a claim on Kindergeld.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.

    Returns
    -------
    """
    return alter <= 24


@policy_function
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


@policy_function
def erwachsene_alle_rentner_hh(
    anzahl_erwachsene_hh: int, anzahl_rentner_hh: int
) -> bool:
    """Calculate if all adults in the household are pensioners.

    Parameters
    ----------
    anzahl_erwachsene_hh
        See :func:`anzahl_erwachsene_hh`.
    anzahl_rentner_hh
        See :func:`anzahl_rentner_hh`.

    Returns
    -------

    """
    return anzahl_erwachsene_hh == anzahl_rentner_hh


@policy_function
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


@policy_function
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


@policy_function
def jüngstes_kind_oder_mehrling(
    alter_monate: float,
    alter_monate_jüngstes_mitglied_fg: float,
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
    alter_monate_jüngstes_mitglied_fg
        See :func:`alter_monate_jüngstes_mitglied_fg`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    out = (alter_monate - alter_monate_jüngstes_mitglied_fg < 0.1) and kind
    return out


@policy_function
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


@policy_function(skip_vectorization=True)
def elternteil_alleinerziehend(
    p_id_kindergeld_empf: numpy.ndarray[int],
    p_id: numpy.ndarray[int],
    alleinerz: numpy.ndarray[bool],
) -> numpy.ndarray[bool]:
    """Check if parent that receives Unterhaltsvorschuss is a single parent.

    Only single parents receive Unterhaltsvorschuss.

    Parameters
    ----------
    p_id_kindergeld_empf
        See basic input variable :ref:`p_id_kindergeld_empf`.
    p_id
        See basic input variable :ref:`p_id`.
    alleinerz
        See basic input variable :ref:`alleinerz`.

    Returns
    -------

    """
    return join_numpy(
        p_id_kindergeld_empf, p_id, alleinerz, value_if_foreign_key_is_missing=False
    )


def ist_kind_mit_erwerbseinkommen(
    bruttolohn_m: float, kindergeld__grundsätzlich_anspruchsberechtigt: bool
) -> bool:
    """Check if children are working.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    kindergeld__grundsätzlich_anspruchsberechtigt
        See :func:`kindergeld__grundsätzlich_anspruchsberechtigt`.

    Returns
    -------

    """
    out = (bruttolohn_m > 0) and kindergeld__grundsätzlich_anspruchsberechtigt
    return out
