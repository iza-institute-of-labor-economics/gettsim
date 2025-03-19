"""This module computes demographic variables directly on the data.

These information are used throughout modules of gettsim.

"""

import datetime

import numpy

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.function_types import group_by_function, policy_function

aggregation_specs = {
    "anzahl_erwachsene_hh": AggregateByGroupSpec(
        source_col="erwachsen",
        aggr="sum",
    ),
    "anzahl_rentner_hh": AggregateByGroupSpec(
        source_col="sozialversicherung__rente__bezieht_rente",
        aggr="sum",
    ),
    "anzahl_personen_hh": AggregateByGroupSpec(
        aggr="count",
    ),
    "anzahl_personen_ehe": AggregateByGroupSpec(
        aggr="count",
    ),
}


@policy_function()
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


@policy_function()
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


@policy_function()
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


@policy_function()
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


@policy_function()
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


@policy_function()
def alter_bis_24(alter: int) -> bool:
    """Age is 24 years at most.

    Trivial, but necessary in order to use the target for aggregation.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.

    Returns
    -------
    """
    return alter <= 24


@policy_function()
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


@policy_function()
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


@policy_function()
def geburtsdatum(
    geburtsjahr: int,
    geburtsmonat: int,
    geburtstag: int,
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
        datetime.datetime(
            geburtsjahr,
            geburtsmonat,
            geburtstag,
        )
    ).astype("datetime64[D]")
    return out


@policy_function()
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


@policy_function()
def ist_kind_mit_erwerbseinkommen(
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m: float,
    kindergeld__grundsätzlich_anspruchsberechtigt: bool,
) -> bool:
    """Check if children are working.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m>`.
    kindergeld__grundsätzlich_anspruchsberechtigt
        See :func:`kindergeld__grundsätzlich_anspruchsberechtigt`.

    Returns
    -------

    """
    out = (
        einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m > 0
    ) and kindergeld__grundsätzlich_anspruchsberechtigt
    return out


@group_by_function()
def ehe_id(
    demographics__p_id: numpy.ndarray[int],
    demographics__p_id_ehepartner: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Ehe for each person.
    """
    p_id_to_ehe_id = {}
    next_ehe_id = 0
    result = []

    for index, current_p_id in enumerate(demographics__p_id):
        current_p_id_ehepartner = demographics__p_id_ehepartner[index]

        if current_p_id_ehepartner >= 0 and current_p_id_ehepartner in p_id_to_ehe_id:
            result.append(p_id_to_ehe_id[current_p_id_ehepartner])
            continue

        # New married couple
        result.append(next_ehe_id)
        p_id_to_ehe_id[current_p_id] = next_ehe_id
        next_ehe_id += 1

    return numpy.asarray(result)
