"""Tax allowances for individuals or couples with children."""

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.function_types import policy_function

aggregation_specs = {
    "anzahl_kinderfreibeträge_1": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_kinderfreibetragsempfänger_1",
        source_col="kindergeld__grundsätzlich_anspruchsberechtigt",
        aggr="sum",
    ),
    "anzahl_kinderfreibeträge_2": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_kinderfreibetragsempfänger_2",
        source_col="kindergeld__grundsätzlich_anspruchsberechtigt",
        aggr="sum",
    ),
}


@policy_function()
def kinderfreibetrag_y(
    anzahl_kinderfreibeträge: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Individual child allowance.

    Parameters
    ----------
    anzahl_kinderfreibeträge
        See :func:`anzahl_kinderfreibeträge`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    return float(
        sum(eink_st_abzuege_params["kinderfreib"].values()) * anzahl_kinderfreibeträge
    )


@policy_function()
def anzahl_kinderfreibeträge(
    anzahl_kinderfreibeträge_1: int,
    anzahl_kinderfreibeträge_2: int,
) -> int:
    """Return the number of Kinderfreibeträge a person is entitled to.

    The person could be a parent or legal custodian.

    Note: Users should overwrite this function if there are single parents in the data
    who should receive two instead of one Kinderfreibeträge. GETTSIM does not
    automatically do this, even if the p_id of the other parent is set to missing (-1).

    Parameters
    ----------
    anzahl_kinderfreibeträge_1
        See :func:`p_id_kinderfreibetr_empfänger_1 <p_id_kinderfreibetr_empfänger_1>`.
    anzahl_kinderfreibeträge_2
        See :func:`p_id_kinderfreibetr_empfänger_2 <p_id_kinderfreibetr_empfänger_2>`.

    """
    return anzahl_kinderfreibeträge_1 + anzahl_kinderfreibeträge_2


@policy_function()
def p_id_kinderfreibetragsempfänger_1(
    demographics__p_id_elternteil_1: int,
) -> int:
    """Assigns child allowance to parent 1.

    Parameters
    ----------
    demographics__p_id_elternteil_1
        See :func:`demographics__p_id_elternteil_1`.

    Returns
    -------

    """
    return demographics__p_id_elternteil_1


@policy_function()
def p_id_kinderfreibetragsempfänger_2(
    demographics__p_id_elternteil_2: int,
) -> int:
    """Assigns child allowance to parent 2.

    Parameters
    ----------
    demographics__p_id_elternteil_2
        See :func:`demographics__p_id_elternteil_2`.

    Returns
    -------

    """
    return demographics__p_id_elternteil_2
