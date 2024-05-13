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


def _diff_kindergeld_kindbedarf_m(
    _arbeitsl_geld_2_eink_ohne_kindergeldübertrag_m_bg: float,
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    kindergeld_zur_bedarfsdeckung_m: float,
    eigenbedarf_gedeckt: bool,
) -> numpy.ndarray[float]:
    """Kindergeld that is used to cover the needs (SGB II) of the parent.

    If a child does not need all of the Kindergeld to cover its own needs (SGB II), the
    remaining Kindergeld is used to cover the needs of the parent (§ 11 Abs. 1 Satz 5
    SGB II).

    Kindergeldübertrag (`kindergeldübertrag_m`) is obtained by aggregating this function
    to the parental level.

    Parameters
    ----------
    _arbeitsl_geld_2_eink_ohne_kindergeldübertrag_m_bg
        See :func:`_arbeitsl_geld_2_eink_ohne_kindergeldübertrag_m_bg`.
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    kindergeld_zur_bedarfsdeckung_m
        See :func:`kindergeld_zur_bedarfsdeckung_m`.
    eigenbedarf_gedeckt
        See :func:`eigenbedarf_gedeckt`.

    Returns
    -------

    """
    # TODO (@MImmesberger): Remove `eigenbedarf_gedeckt` conditions once
    # Bedarfsgemeinschaft is fully endogenous. This is a temporary fix. Without it,
    # Kindergeld would be counted twice as income of the Bedarfsgemeinschaft (one time
    # the full amount for the child and one time the Kindergeldübertrag for the parent -
    # because the child doesn't drop out of Bedarfsgemeinschaft endogenously).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/622
    # TODO (@MImmesberger): Consider Kinderwohngeld in the Fehlbetrag calculation.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/750
    fehlbetrag = max(
        arbeitsl_geld_2_regelbedarf_m_bg
        - _arbeitsl_geld_2_eink_ohne_kindergeldübertrag_m_bg,
        0.0,
    )
    # Bedarf not covered or same Bedarfsgemeinschaft as parents
    if not eigenbedarf_gedeckt or fehlbetrag > kindergeld_zur_bedarfsdeckung_m:
        out = 0.0
    # Bedarf is covered
    else:
        out = kindergeld_zur_bedarfsdeckung_m - fehlbetrag
    return out
