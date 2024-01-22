from _gettsim.shared import dates_active

aggregation_kindergeld = {
    "kumulativer_kindergeld_anspruch_tu": {
        "source_col": "kindergeld_anspruch",
        "aggr": "cumsum",
    },
    "anz_kinder_mit_kindergeld_tu": {
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}


def kindergeld_m(
    kindergeld_eltern_m: float,
):
    return kindergeld_eltern_m


def kindergeld_kind_m(
    kindergeld_anspruch: bool,
    kumulativer_kindergeld_anspruch_tu: int,
    kindergeld_params: dict,
) -> float:
    """Calculate kindergeld for an individual child.

    Parameters
    ----------
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.
    kumulativer_kindergeld_anspruch_tu
        See :func:`kumulativer_kindergeld_anspruch_tu`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """

    # Make sure that only eligible children get assigned kindergeld
    if not kindergeld_anspruch:
        out = 0.0
    else:
        # Kindergeld_Anspruch is the cumulative sum of eligible children.
        out = kindergeld_params["kindergeld"][
            min(
                kumulativer_kindergeld_anspruch_tu, max(kindergeld_params["kindergeld"])
            )
        ]
    return out


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
