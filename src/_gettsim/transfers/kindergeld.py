from _gettsim.shared import dates_active

aggregate_by_group_kindergeld = {
    "anz_kinder_mit_kindergeld_tu": {
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
    "anz_kinder_mit_kindergeld_fg": {
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}

aggregate_by_p_id_kindergeld = {
    "kindergeld_anz_ansprüche": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}


@dates_active(start="2023-01-01", change_name="kindergeld_m")
def kindergeld_ohne_staffelung_m(
    kindergeld_anz_ansprüche: bool,
    kindergeld_params: dict,
) -> float:
    """Sum of Kindergeld for eligible children.

    Kindergeld claim is the same for each child, i.e. increases linearly with the number
    of children.

    Parameters
    ----------
    kindergeld_anz_ansprüche
        See :func:`kindergeld_anz_ansprüche`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """

    return kindergeld_params["kindergeld"] * kindergeld_anz_ansprüche


@dates_active(end="2022-12-31", change_name="kindergeld_m")
def kindergeld_gestaffelt_m(
    kindergeld_anz_ansprüche: bool,
    kindergeld_params: dict,
) -> float:
    """Sum of Kindergeld for eligible children.

    Kindergeld claim for each child depends on the number of children Kindergeld is
    being claimed for.

    Parameters
    ----------
    kindergeld_anz_ansprüche
        See :func:`kindergeld_anz_ansprüche`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """

    if kindergeld_anz_ansprüche == 0:
        sum_kindergeld = 0.0
    else:
        sum_kindergeld = sum(
            kindergeld_params["kindergeld"][
                (
                    i
                    if i <= max(kindergeld_params["kindergeld"])
                    else max(kindergeld_params["kindergeld"])
                )
            ]
            for i in range(1, kindergeld_anz_ansprüche + 1)
        )

    return sum_kindergeld


@dates_active(end="2011-12-31", change_name="kindergeld_anspruch")
def kindergeld_anspruch_nach_lohn(
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


@dates_active(start="2012-01-01", change_name="kindergeld_anspruch")
def kindergeld_anspruch_nach_stunden(
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


def kind_bis_12_mit_kindergeld(
    alter: int,
    kindergeld_anspruch: bool,
) -> bool:
    """Child under the age of 13 and eligible for Kindergeld.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kindergeld_anspruch
        See :func:`kindergeld_anspruch_nach_stunden`.

    Returns
    -------

    """
    out = kindergeld_anspruch and (alter <= 12)
    return out
