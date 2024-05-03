"""Module for the calculation of the Kindergeldübertrag."""

import numpy as np

from _gettsim.shared import join_numpy, policy_info

aggregate_by_p_id_kindergeldübertrag = {
    "kindergeld_übertrag_m": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "_kindergeld_kindbedarf_differenz_m",
        "aggr": "sum",
    },
}


def _kindergeld_per_child_m(
    kindergeld_m: float,
    kindergeld_anz_ansprüche: int,
) -> float:
    """Kindergeld per child.

    Returns the average Kindergeld per child. If there are no children, the function
    returns 0. Helper function for `kindergeld_zur_bedarfdeckung_m`.

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
    arbeitsl_geld_2_eink_m_bg: float,
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    kindergeld_zur_bedarfdeckung_m: float,
    eigenbedarf_gedeckt: bool,
) -> float:
    """Kindergeld that is used to cover the needs (SGB II) of the parent.

    If a child does not need all of the Kindergeld to cover its own needs (SGB II), the
    remaining Kindergeld is used to cover the needs of the parent (§ 11 Abs. 1 Satz 5
    SGB II).


    """
    # TODO (@MImmesberger): Remove `eigenbedarf_gedeckt` conditions once
    # Bedarfsgemeinschaft is fully endogenous. This is a temporary fix. Without it,
    # Kindergeld would be counted twice as income of the Bedarfsgemeinschaft (one time
    # the full amount for the child and one time the Kindergeldübertrag for the parent -
    # because the child doesn't drop out of Bedarfsgemeinschaft endogenously).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/622
    fehlbetrag = max(
        arbeitsl_geld_2_regelbedarf_m_bg - arbeitsl_geld_2_eink_m_bg,
        0.0,
    )
    # Bedarf not covered or same Bedarfsgemeinschaft as parents
    if not eigenbedarf_gedeckt or fehlbetrag > kindergeld_zur_bedarfdeckung_m:
        out = 0.0
    # Bedarf is covered
    else:
        out = kindergeld_zur_bedarfdeckung_m - fehlbetrag
    return out
