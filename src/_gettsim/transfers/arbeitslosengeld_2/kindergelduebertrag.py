"""Module for the calculation of the Kindergeldübertrag."""

import numpy

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.functions.policy_function import policy_function
from _gettsim.shared import join_numpy

aggregation_specs = {
    "kindergeldübertrag_m": AggregateByPIDSpec(
        p_id_to_aggregate_by="kindergeld__p_id_empfänger",
        source_col="differenz_kindergeld_kindbedarf_m",
        aggr="sum",
    ),
}


@policy_function(end_date="2022-12-31", leaf_name="kindergeld_pro_kind_m")
def _mean_kindergeld_per_child_gestaffelt_m(
    kindergeld__betrag_m: float,
    kindergeld__anzahl_ansprüche: int,
) -> float:
    """Kindergeld per child.

    Returns the average Kindergeld per child. If there are no children, the function
    returns 0. Helper function for `kindergeld_zur_bedarfsdeckung_m`.

    Parameters
    ----------
    kindergeld__betrag_m
        See :func:`kindergeld__betrag_m`.
    kindergeld__anzahl_ansprüche
        See :func:`kindergeld__anzahl_ansprüche`.

    Returns
    -------

    """
    if kindergeld__anzahl_ansprüche > 0:
        out = kindergeld__betrag_m / kindergeld__anzahl_ansprüche
    else:
        out = 0.0
    return out


@policy_function(start_date="2023-01-01", leaf_name="kindergeld_pro_kind_m")
def _mean_kindergeld_per_child_ohne_staffelung_m(
    kindergeld_params: dict,
    kindergeld__anzahl_ansprüche: int,
) -> float:
    """Kindergeld per child.

    Returns the (average) Kindergeld per child. Helper function for
    `kindergeld_zur_bedarfsdeckung_m`.

    Parameters
    ----------
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    demographics__alter
        See basic input variable :ref:`demographics__alter`.

    Returns
    -------

    """
    return kindergeld_params["kindergeld"] if kindergeld__anzahl_ansprüche > 0 else 0.0


@policy_function(skip_vectorization=True)
def kindergeld_zur_bedarfsdeckung_m(
    kindergeld_pro_kind_m: float,
    kindergeld__p_id_empfänger: numpy.ndarray[int],
    demographics__p_id: numpy.ndarray[int],
) -> numpy.ndarray[float]:
    """Kindergeld that is used to cover the SGB II Regelbedarf of the child.

    Even though the Kindergeld is paid to the parent (see function
    :func:`kindergeld__betrag_m`), the child that gives rise to the Kindergeld claim is
    entitled to it to cover its needs (§ 11 Abs. 1 Satz 5 SGB II). The amount of
    Kindergeld for which the child is entitled to is the sum of the Kindergeld for all
    children divided by the amount of children. Hence, the age of the child (in
    comparison to siblings) does not matter.

    Parameters
    ----------
    kindergeld__betrag_m
        See :func:`kindergeld__betrag_m`.
    kindergeld__p_id_empfänger
        See :func:`kindergeld__p_id_empfänger`.
    demographics__p_id
        See :func:`demographics__p_id`.

    Returns
    -------

    """
    return join_numpy(
        kindergeld__p_id_empfänger,
        demographics__p_id,
        kindergeld_pro_kind_m,
        value_if_foreign_key_is_missing=0.0,
    )


@policy_function
def differenz_kindergeld_kindbedarf_m(  # noqa: PLR0913
    regelbedarf_m_bg: float,
    nettoeinkommen_nach_abzug_freibetrag_m: float,
    wohngeld__anspruchshöhe_m_bg: float,
    kindergeld_zur_bedarfsdeckung_m: float,
    unterhalt__kind_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    in_anderer_bg_als_kindergeldempfänger: bool,
) -> float:
    """Kindergeld that is used to cover the needs (SGB II) of the parent.

    If a child does not need all of the Kindergeld to cover its own needs (SGB II), the
    remaining Kindergeld is used to cover the needs of the parent (§ 11 Abs. 1 Satz 5
    SGB II).

    Kindergeldübertrag (`kindergeldübertrag_m`) is obtained by aggregating this function
    to the parental level.

    Parameters
    ----------
    regelbedarf_m_bg
        See :func:`regelbedarf_m_bg`.
    nettoeinkommen_nach_abzug_freibetrag_m
        See :func:`_arbeitsl_geld_2
    wohngeld__anspruchshöhe_m_bg
        See :func:`wohngeld__anspruchshöhe_m_bg`.
    kindergeld_zur_bedarfsdeckung_m
        See :func:`kindergeld_zur_bedarfsdeckung_m`.
    unterhalt__kind_betrag_m
        See :func:`unterhalt__kind_betrag_m`.
    unterhaltsvorschuss__betrag_m
        See :func:`unterhaltsvorschuss__betrag_m`.
    in_anderer_bg_als_kindergeldempfänger
        See :func:`in_anderer_bg_als_kindergeldempfänger`.

    Returns
    -------

    """
    fehlbetrag = max(
        regelbedarf_m_bg
        - wohngeld__anspruchshöhe_m_bg
        - nettoeinkommen_nach_abzug_freibetrag_m
        - unterhalt__kind_betrag_m
        - unterhaltsvorschuss__betrag_m,
        0.0,
    )
    # Bedarf not covered or same Bedarfsgemeinschaft as parents
    if (
        not in_anderer_bg_als_kindergeldempfänger
        or fehlbetrag > kindergeld_zur_bedarfsdeckung_m
    ):
        out = 0.0
    # Bedarf is covered
    else:
        out = kindergeld_zur_bedarfsdeckung_m - fehlbetrag
    return out


@policy_function(skip_vectorization=True)
def in_anderer_bg_als_kindergeldempfänger(
    demographics__p_id: numpy.ndarray[int],
    kindergeld__p_id_empfänger: numpy.ndarray[int],
    bg_id: numpy.ndarray[int],
) -> numpy.ndarray[bool]:
    """True if the person is in a different Bedarfsgemeinschaft than the
    Kindergeldempfänger of that person.

    Parameters
    ----------
    demographics__p_id
        See basic input variable :ref:`demographics__p_id <demographics__p_id>`
    kindergeld__p_id_empfänger
        See basic input variable :ref:`kindergeld__p_id_empfänger <kindergeld__p_id_empfänger>`
    bg_id
        See :func:`bg_id`.

    Returns
    -------

    """  # noqa: E501
    # Create a dictionary to map demographics__p_id to bg_id
    p_id_to_bg_id = dict(zip(demographics__p_id, bg_id))

    # Map each kindergeld__p_id_empfänger to its corresponding bg_id
    empf_bg_id = [
        p_id_to_bg_id[empfänger_id] if empfänger_id >= 0 else -1
        for empfänger_id in kindergeld__p_id_empfänger
    ]

    # Compare bg_id array with the mapped bg_ids of kindergeld__p_id_empfänger
    return bg_id != empf_bg_id
