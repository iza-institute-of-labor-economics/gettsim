"""Basic child allowance (Kindergeld)."""

import numpy

from _gettsim.aggregation import AggregateByGroupSpec, AggregateByPIDSpec
from _gettsim.function_types import policy_function
from _gettsim.shared import join_numpy

aggregation_specs = {
    "anzahl_kinder_fg": AggregateByGroupSpec(
        source_col="grundsätzlich_anspruchsberechtigt",
        aggr="sum",
    ),
    "anzahl_ansprüche": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_empfänger",
        source_col="grundsätzlich_anspruchsberechtigt",
        aggr="sum",
    ),
}


@policy_function(start_date="2023-01-01", leaf_name="betrag_m")
def betrag_ohne_staffelung_m(
    anzahl_ansprüche: int,
    kindergeld_params: dict,
) -> float:
    """Sum of Kindergeld for eligible children.

    Kindergeld claim is the same for each child, i.e. increases linearly with the number
    of children.

    Parameters
    ----------
    anzahl_ansprüche
        See :func:`anzahl_ansprüche`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """

    return kindergeld_params["kindergeld"] * anzahl_ansprüche


@policy_function(end_date="2022-12-31", leaf_name="betrag_m")
def betrag_gestaffelt_m(
    anzahl_ansprüche: int,
    kindergeld_params: dict,
) -> float:
    """Sum of Kindergeld that parents receive for their children.

    Kindergeld claim for each child depends on the number of children Kindergeld is
    being claimed for.

    Parameters
    ----------
    anzahl_ansprüche
        See :func:`anzahl_ansprüche`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """

    if anzahl_ansprüche == 0:
        sum_kindergeld = 0.0
    else:
        sum_kindergeld = sum(
            kindergeld_params["kindergeld"][
                (min(i, max(kindergeld_params["kindergeld"])))
            ]
            for i in range(1, anzahl_ansprüche + 1)
        )

    return sum_kindergeld


@policy_function(end_date="2011-12-31", leaf_name="grundsätzlich_anspruchsberechtigt")
def grundsätzlich_anspruchsberechtigt_nach_lohn(
    demographics__alter: int,
    in_ausbildung: bool,
    einkommen__bruttolohn_m: float,
    kindergeld_params: dict,
) -> bool:
    """Determine kindergeld eligibility for an individual child depending on kids wage.

    Until 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    in_ausbildung
        See basic input variable :ref:`in_ausbildung <in_ausbildung>`.
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.

    Returns
    -------

    """
    out = (
        demographics__alter < kindergeld_params["altersgrenze"]["ohne_bedingungen"]
    ) or (
        (demographics__alter < kindergeld_params["altersgrenze"]["mit_bedingungen"])
        and in_ausbildung
        and (einkommen__bruttolohn_m <= kindergeld_params["einkommensgrenze"] / 12)
    )

    return out


@policy_function(start_date="2012-01-01", leaf_name="grundsätzlich_anspruchsberechtigt")
def grundsätzlich_anspruchsberechtigt_nach_stunden(
    demographics__alter: int,
    in_ausbildung: bool,
    demographics__arbeitsstunden_w: float,
    kindergeld_params: dict,
) -> bool:
    """Determine kindergeld eligibility for an individual child depending on working
    hours.

    The current eligibility rule is, that kids must not work more than 20
    hour and are below 25.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    in_ausbildung
        See :func:`in_ausbildung`.
    demographics__arbeitsstunden_w
        See :func:`demographics__arbeitsstunden_w`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------
    Boolean indiciating kindergeld eligibility.

    """
    out = (
        demographics__alter < kindergeld_params["altersgrenze"]["ohne_bedingungen"]
    ) or (
        (demographics__alter < kindergeld_params["altersgrenze"]["mit_bedingungen"])
        and in_ausbildung
        and (demographics__arbeitsstunden_w <= kindergeld_params["stundengrenze"])
    )

    return out


@policy_function()
def kind_bis_10_mit_kindergeld(
    demographics__alter: int,
    grundsätzlich_anspruchsberechtigt: bool,
) -> bool:
    """Child under the age of 11 and eligible for Kindergeld.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    grundsätzlich_anspruchsberechtigt
        See :func:`grundsätzlich_anspruchsberechtigt_nach_stunden`.

    Returns
    -------

    """
    out = grundsätzlich_anspruchsberechtigt and (demographics__alter <= 10)
    return out


@policy_function(skip_vectorization=True)
def gleiche_fg_wie_empfänger(
    demographics__p_id: numpy.ndarray[int],
    p_id_empfänger: numpy.ndarray[int],
    arbeitslosengeld_2__fg_id: numpy.ndarray[int],
) -> numpy.ndarray[bool]:
    """The child's Kindergeldempfänger is in the same Familiengemeinschaft.

    Parameters
    ----------
    demographics__p_id
        See basic input variable :ref:`demographics__p_id <demographics__p_id>`.
    p_id_empfänger
        See basic input variable :ref:`p_id_empfänger <p_id_empfänger>`.
    arbeitslosengeld_2__fg_id
        See basic input variable :ref:`arbeitslosengeld_2__fg_id <arbeitslosengeld_2__fg_id>`.

    Returns
    -------

    """
    fg_id_kindergeldempfänger = join_numpy(
        p_id_empfänger,
        demographics__p_id,
        arbeitslosengeld_2__fg_id,
        value_if_foreign_key_is_missing=-1,
    )

    return fg_id_kindergeldempfänger == arbeitslosengeld_2__fg_id
