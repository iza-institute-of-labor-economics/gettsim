"""Tax allowances for individuals or couples with children."""

aggregate_by_p_id_freibeträge = {
    "anzahl_anspruch_1": {
        "p_id_to_aggregate_by": "p_id_empfänger_1",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
    "anzahl_anspruch_2": {
        "p_id_to_aggregate_by": "p_id_empfänger_2",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}


def betrag_y(
    anzahl_ansprüche: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Individual child allowance.

    Parameters
    ----------
    anzahl_ansprüche
        See :func:`anzahl_ansprüche`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    return float(sum(eink_st_abzuege_params["kinderfreib"].values()) * anzahl_ansprüche)


def anzahl_ansprüche(
    anzahl_anspruch_1: int,
    anzahl_anspruch_2: int,
) -> int:
    """Return the number of Kinderfreibeträge a person is entitled to.

    The person could be a parent or legal custodian.

    Parameters
    ----------
    anzahl_anspruch_1
        Helper function based on aggregating
        :ref:`p_id_kinderfreibetr_empfänger_1 <p_id_kinderfreibetr_empfänger_1>`.
    anzahl_anspruch_2
        Helper function based on aggregating
        :ref:`p_id_kinderfreibetr_empfänger_2 <p_id_kinderfreibetr_empfänger_2>`.

    """
    return anzahl_anspruch_1 + anzahl_anspruch_2


def p_id_empfänger_1(
    p_id_elternteil_1: int,
) -> int:
    """Assigns child allowance to parent 1.

    Parameters
    ----------
    p_id_elternteil_1
        See :func:`p_id_elternteil_1`.

    Returns
    -------

    """
    return p_id_elternteil_1


def p_id_empfänger_2(
    p_id_elternteil_2: int,
) -> int:
    """Assigns child allowance to parent 2.

    Parameters
    ----------
    p_id_elternteil_2
        See :func:`p_id_elternteil_2`.

    Returns
    -------

    """
    return p_id_elternteil_2
