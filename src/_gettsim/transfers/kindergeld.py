import numpy as np

from _gettsim.shared import join_numpy, policy_info

aggregate_by_group_kindergeld = {
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
    "kindergeld_übertrag_m": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "_kindergeld_kindbedarf_differenz_m",
        "aggr": "sum",
    },
}


@policy_info(start_date="2023-01-01", name_in_dag="kindergeld_m")
def kindergeld_ohne_staffelung_m(
    kindergeld_anz_ansprüche: int,
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


@policy_info(end_date="2022-12-31", name_in_dag="kindergeld_m")
def kindergeld_gestaffelt_m(
    kindergeld_anz_ansprüche: int,
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


@policy_info(end_date="2011-12-31", name_in_dag="kindergeld_anspruch")
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


@policy_info(start_date="2012-01-01", name_in_dag="kindergeld_anspruch")
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


def kind_bis_10_mit_kindergeld(
    alter: int,
    kindergeld_anspruch: bool,
) -> bool:
    """Child under the age of 11 and eligible for Kindergeld.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    kindergeld_anspruch
        See :func:`kindergeld_anspruch_nach_stunden`.

    Returns
    -------

    """
    out = kindergeld_anspruch and (alter <= 10)
    return out


def _kindergeld_per_child_m(
    kindergeld_m: float,
    kindergeld_anz_ansprüche: int,
) -> float:
    """Kindergeld per child.

    Helper function for `kindergeld_zur_bedarfdeckung_m`. Returns the average Kindergeld
    per child. If there are no children, the function returns 0.

    Parameters
    ----------
    kindergeld_m
        See :func:`kindergeld_m`.
    kindergeld_anz_ansprüche
        See :func:`kindergeld_anz_ansprüche`.

    Returns
    -------

    """
    if kindergeld_anz_ansprüche == 0:
        out = 0.0
    else:
        out = kindergeld_m / kindergeld_anz_ansprüche
    return out


@policy_info(skip_vectorization=True)
def kindergeld_zur_bedarfdeckung_m(
    _kindergeld_per_child_m: float,
    p_id_kindergeld_empf: np.ndarray[int],
    p_id: np.ndarray[int],
) -> float:
    """Kindergeld that is used to cover the SGB II Regelbedarf of the child.

    Even though the Kindergeld is paid to the parent (see function
    :func:`kindergeld_m`), the child that gives rise to the Kindergeld claim is entitled
    to it to cover its needs (§ 11 Abs. 1 Satz 5 SGB II). The amount of Kindergeld for
    which the child is entitled to is the sum of the Kindergeld for all children divided
    by the amount of children. Hence, the age of the child (in comparison to siblings)
    does not matter.

    Parameters
    ----------
    kindergeld_m
        See :func:`kindergeld_m`.
    kindergeld_anz_ansprüche
        See :func:`kindergeld_anz_ansprüche`.
    p_id_kindergeld_empf
        See :func:`p_id_kindergeld_empf`.
    p_id
        See :func:`p_id`.

    Returns
    -------

    """
    return join_numpy(
        p_id_kindergeld_empf,
        p_id,
        _kindergeld_per_child_m,
        value_if_foreign_key_is_missing=0.0,
    )


def _kindergeld_kindbedarf_differenz_m(
    _arbeitsl_geld_2_eink_ohne_kindergeldübertrag_m_bg: float,
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    kindergeld_zur_bedarfdeckung_m: float,
) -> float:
    """Kindergeld that is used to cover the needs (SGB II) of the parent.

    If a child does not need all of the Kindergeld to cover its own needs (SGB II), the
    remaining Kindergeld is used to cover the needs of the parent (§ 11 Abs. 1 Satz 5
    SGB II).


    """
    fehlbetrag = max(
        arbeitsl_geld_2_regelbedarf_m_bg
        - _arbeitsl_geld_2_eink_ohne_kindergeldübertrag_m_bg,
        0.0,
    )
    if fehlbetrag > kindergeld_zur_bedarfdeckung_m:
        out = 0.0
    else:
        out = kindergeld_zur_bedarfdeckung_m - fehlbetrag
    return out
