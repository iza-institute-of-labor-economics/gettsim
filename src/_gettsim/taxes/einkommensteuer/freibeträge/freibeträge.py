"""Tax allowances."""

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.function_types import policy_function

aggregation_specs = {
    "anzahl_kinder_bis_24_elternteil_1": AggregateByPIDSpec(
        p_id_to_aggregate_by=("p_id_kinderfreibetragempfänger_1"),
        source_col="kind_bis_24",
        aggr="sum",
    ),
    "anzahl_kinder_bis_24_elternteil_2": AggregateByPIDSpec(
        p_id_to_aggregate_by=("p_id_kinderfreibetragempfänger_2"),
        source_col="kind_bis_24",
        aggr="sum",
    ),
}


@policy_function()
def betrag_y_sn(
    sonderausgaben_y_sn: float,
    einkommensteuer__einkommen__vorsorgeaufwand_y_sn: float,
    betrag_ind_y_sn: float,
) -> float:
    """Calculate total allowances on Steuernummer level.

    Parameters
    ----------

    sonderausgaben_y_sn
        See :func:`sonderausgaben_y_sn`.
    einkommensteuer__einkommen__vorsorgeaufwand_y_sn
        See :func:`einkommensteuer__einkommen__vorsorgeaufwand_y_sn`.
    betrag_ind_y_sn
        See :func:`betrag_ind_y_sn`.

    Returns
    -------

    """
    out = (
        sonderausgaben_y_sn
        + einkommensteuer__einkommen__vorsorgeaufwand_y_sn
        + betrag_ind_y_sn
    )

    return out


@policy_function()
def betrag_ind_y(
    pauschbetrag_behinderung_y: float,
    alleinerziehend_betrag_y: float,
    altersfreibetrag_y: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level.

    Parameters
    ----------

    pauschbetrag_behinderung_y
        See :func:`pauschbetrag_behinderung_y`.
    alleinerziehend_betrag_y
        See :func:`alleinerziehend_betrag_y`.
    altersfreibetrag_y
        See :func:`altersfreibetrag_y`.

    Returns
    -------

    """
    out = pauschbetrag_behinderung_y + alleinerziehend_betrag_y + altersfreibetrag_y
    return out
