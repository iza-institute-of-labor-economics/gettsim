"""Basic child allowance (Kindergeld)."""

import numpy

from _gettsim.functions.policy_function import policy_function
from _gettsim.shared import join_numpy

aggregate_by_group_kindergeld = {
    "anzahl_kinder_fg": {
        "source_col": "anspruchsberechtigt",
        "aggr": "sum",
    },
}

aggregate_by_p_id_kindergeld = {
    "anzahl_ansprüche": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "anspruchsberechtigt",
        "aggr": "sum",
    },
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
    """Sum of Kindergeld for eligible children.

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


@policy_function(end_date="2011-12-31", leaf_name="anspruchsberechtigt")
def anspruchsberechtigt_nach_lohn(
    alter: int,
    in_ausbildung: bool,
    bruttolohn_m: float,
    kindergeld_params: dict,
) -> bool:
    """Determine kindergeld eligibility for an individual child depending on kids wage.

    Until 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    in_ausbildung
        See basic input variable :ref:`in_ausbildung <in_ausbildung>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.

    Returns
    -------

    """
    out = (alter < kindergeld_params["altersgrenze"]["ohne_bedingungen"]) or (
        (alter < kindergeld_params["altersgrenze"]["mit_bedingungen"])
        and in_ausbildung
        and (bruttolohn_m <= kindergeld_params["einkommensgrenze"] / 12)
    )

    return out


@policy_function(start_date="2012-01-01", leaf_name="anspruchsberechtigt")
def anspruchsberechtigt_nach_stunden(
    alter: int,
    in_ausbildung: bool,
    arbeitsstunden_w: float,
    kindergeld_params: dict,
) -> bool:
    """Determine kindergeld eligibility for an individual child depending on working
    hours.

    The current eligibility rule is, that kids must not work more than 20
    hour and are below 25.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    in_ausbildung
        See :func:`in_ausbildung`.
    arbeitsstunden_w
        See :func:`arbeitsstunden_w`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------
    Boolean indiciating kindergeld eligibility.

    """
    out = (alter < kindergeld_params["altersgrenze"]["ohne_bedingungen"]) or (
        (alter < kindergeld_params["altersgrenze"]["mit_bedingungen"])
        and in_ausbildung
        and (arbeitsstunden_w <= kindergeld_params["stundengrenze"])
    )

    return out


@policy_function
def kind_bis_10_mit_kindergeld(
    alter: int,
    anspruchsberechtigt: bool,
) -> bool:
    """Child under the age of 11 and eligible for Kindergeld.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    anspruchsberechtigt
        See :func:`anspruchsberechtigt_nach_stunden`.

    Returns
    -------

    """
    out = anspruchsberechtigt and (alter <= 10)
    return out


@policy_function(skip_vectorization=True)
def gleiche_fg_wie_empfänger(
    p_id: numpy.ndarray[int],
    p_id_kindergeld_empf: numpy.ndarray[int],
    fg_id: numpy.ndarray[int],
) -> numpy.ndarray[bool]:
    """The child's Kindergeldempfänger is in the same Familiengemeinschaft.

    Parameters
    ----------
    p_id
        See basic input variable :ref:`p_id <p_id>`.
    p_id_kindergeld_empf
        See basic input variable :ref:`p_id_kindergeld_empf <p_id_kindergeld_empf>`.
    fg_id
        See basic input variable :ref:`fg_id <fg_id>`.

    Returns
    -------

    """
    fg_id_kindergeldempfänger = join_numpy(
        p_id_kindergeld_empf,
        p_id,
        fg_id,
        value_if_foreign_key_is_missing=-1,
    )

    return fg_id_kindergeldempfänger == fg_id
