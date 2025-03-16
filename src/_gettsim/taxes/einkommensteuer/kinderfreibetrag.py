"""Tax allowances for individuals or couples with children."""

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.function_types import policy_function

aggregation_specs = {
    "anzahl_kinderfreibeträge_1": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_kinderfreibetragempfänger_1",
        source_col="kindergeld__grundsätzlich_anspruchsberechtigt",
        aggr="sum",
    ),
    "anzahl_kinderfreibeträge_2": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_kinderfreibetragempfänger_2",
        source_col="kindergeld__grundsätzlich_anspruchsberechtigt",
        aggr="sum",
    ),
}


@policy_function()
def kinderfreibetrag_y(
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


@policy_function()
def anzahl_kinderfreibeträge(
    anzahl_kinderfreibeträge_1: int,
    anzahl_kinderfreibeträge_2: int,
) -> int:
    """Return the number of Kinderfreibeträge a person is entitled to.

    The person could be a parent or legal custodian.

    Parameters
    ----------
    anzahl_kinderfreibeträge_1
        Helper function based on aggregating
        :ref:`p_id_kinderfreibetr_empfänger_1 <p_id_kinderfreibetr_empfänger_1>`.
    anzahl_kinderfreibeträge_2
        Helper function based on aggregating
        :ref:`p_id_kinderfreibetr_empfänger_2 <p_id_kinderfreibetr_empfänger_2>`.

    """
    return anzahl_kinderfreibeträge_1 + anzahl_kinderfreibeträge_2


@policy_function()
def p_id_kinderfreibetragempfänger_1(
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
def p_id_kinderfreibetragempfänger_2(
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
