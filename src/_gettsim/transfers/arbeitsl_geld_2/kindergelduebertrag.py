"""Module for the calculation of the Kindergeldübertrag."""

import numpy

from _gettsim.shared import join_numpy, policy_info

aggregate_by_p_id_kindergeldübertrag = {
    "kindergeldübertrag_m": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "_diff_kindergeld_kindbedarf_m",
        "aggr": "sum",
    },
}


@policy_info(end_date="2022-12-31", name_in_dag="_mean_kindergeld_per_child_m")
def _mean_kindergeld_per_child_gestaffelt_m(
    kindergeld_m: float,
    kindergeld_anz_ansprüche: int,
) -> float:
    """Kindergeld per child.

    Returns the average Kindergeld per child. If there are no children, the function
    returns 0. Helper function for `kindergeld_zur_bedarfsdeckung_m`.

    Parameters
    ----------
    kindergeld_m
        See :func:`kindergeld_m`.
    kindergeld_anz_ansprüche
        See :func:`kindergeld_anz_ansprüche`.

    Returns
    -------

    """
    if kindergeld_anz_ansprüche > 0:
        out = kindergeld_m / kindergeld_anz_ansprüche
    else:
        out = 0.0
    return out


@policy_info(start_date="2023-01-01", name_in_dag="_mean_kindergeld_per_child_m")
def _mean_kindergeld_per_child_ohne_staffelung_m(
    kindergeld_params: dict,
    kindergeld_anz_ansprüche: int,
) -> float:
    """Kindergeld per child.

    Returns the (average) Kindergeld per child. Helper function for
    `kindergeld_zur_bedarfsdeckung_m`.

    Parameters
    ----------
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    alter
        See basic input variable :ref:`alter`.

    Returns
    -------

    """
    return kindergeld_params["kindergeld"] if kindergeld_anz_ansprüche > 0 else 0.0


@policy_info(skip_vectorization=True)
def kindergeld_zur_bedarfsdeckung_m(
    _mean_kindergeld_per_child_m: float,
    p_id_kindergeld_empf: numpy.ndarray[int],
    p_id: numpy.ndarray[int],
) -> numpy.ndarray[float]:
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
        _mean_kindergeld_per_child_m,
        value_if_foreign_key_is_missing=0.0,
    )


def _diff_kindergeld_kindbedarf_m(  # noqa: PLR0913
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m: float,
    wohngeld_m_wthh: float,
    anz_personen_wthh: int,
    kindergeld_zur_bedarfsdeckung_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvors_m: float,
    _in_anderer_bedarfsgemeinschaft_als_kindergeldempfänger: bool,
) -> float:
    """Kindergeld that is used to cover the needs (SGB II) of the parent.

    If a child does not need all of the Kindergeld to cover its own needs (SGB II), the
    remaining Kindergeld is used to cover the needs of the parent (§ 11 Abs. 1 Satz 5
    SGB II).

    Kindergeldübertrag (`kindergeldübertrag_m`) is obtained by aggregating this function
    to the parental level.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m
        See :func:`_arbeitsl_geld_2
    wohngeld_m_wthh
        See :func:`wohngeld_m_wthh`.
    anz_personen_wthh
        See :func:`anz_personen_wthh`.
    kindergeld_zur_bedarfsdeckung_m
        See :func:`kindergeld_zur_bedarfsdeckung_m`.
    kind_unterh_erhalt_m
        See :func:`kind_unterh_erhalt_m`.
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    _in_anderer_bedarfsgemeinschaft_als_kindergeldempfänger
        See :func:`_in_anderer_bedarfsgemeinschaft_als_kindergeldempfänger`.

    Returns
    -------

    """
    fehlbetrag = max(
        arbeitsl_geld_2_regelbedarf_m_bg
        - wohngeld_m_wthh / anz_personen_wthh
        - arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m
        - kind_unterh_erhalt_m
        - unterhaltsvors_m,
        0.0,
    )
    # Bedarf not covered or same Bedarfsgemeinschaft as parents
    if (
        not _in_anderer_bedarfsgemeinschaft_als_kindergeldempfänger
        or fehlbetrag > kindergeld_zur_bedarfsdeckung_m
    ):
        out = 0.0
    # Bedarf is covered
    else:
        out = kindergeld_zur_bedarfsdeckung_m - fehlbetrag
    return out


@policy_info(skip_vectorization=True)
def _in_anderer_bedarfsgemeinschaft_als_kindergeldempfänger(
    p_id: numpy.ndarray[int],
    p_id_kindergeld_empf: numpy.ndarray[int],
    bg_id: numpy.ndarray[int],
) -> numpy.ndarray[bool]:
    """True if the person is in a different Bedarfsgemeinschaft than the
    Kindergeldempfänger of that person.
    """
    # Create a dictionary to map p_id to bg_id
    p_id_to_bg_id = dict(zip(p_id, bg_id))

    # Map each p_id_kindergeld_empf to its corresponding bg_id
    empf_bg_id = [
        p_id_to_bg_id[empfänger_id] if empfänger_id >= 0 else -1
        for empfänger_id in p_id_kindergeld_empf
    ]

    # Compare bg_id array with the mapped bg_ids of p_id_kindergeld_empf
    return bg_id != empf_bg_id
