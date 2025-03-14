"""Income taxes."""

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.function_types import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial

aggregation_specs = {
    "anzahl_kindergeld_ansprüche_1": AggregateByPIDSpec(
        p_id_to_aggregate_by="demographics__p_id_elternteil_1",
        source_col="kindergeld__grundsätzlich_anspruchsberechtigt",
        aggr="sum",
    ),
    "anzahl_kindergeld_ansprüche_2": AggregateByPIDSpec(
        p_id_to_aggregate_by="demographics__p_id_elternteil_2",
        source_col="kindergeld__grundsätzlich_anspruchsberechtigt",
        aggr="sum",
    ),
}


@policy_function(
    end_date="1996-12-31", leaf_name="betrag_y_sn", params_key_for_rounding="eink_st"
)
def betrag_y_sn_kindergeld_kinderfreibetrag_parallel(
    betrag_mit_kinderfreibetrag_y_sn: float,
) -> float:
    """Income tax calculation on Steuernummer level allowing for claiming
    Kinderfreibetrag and receiving Kindergeld at the same time.

    Parameters
    ----------
    betrag_mit_kinderfreibetrag_y_sn
        See :func:`betrag_mit_kinderfreibetrag_y_sn`.

    Returns
    -------

    """
    return betrag_mit_kinderfreibetrag_y_sn


@policy_function(
    start_date="1997-01-01",
    leaf_name="betrag_y_sn",
    params_key_for_rounding="eink_st",
)
def betrag_y_sn_kindergeld_oder_kinderfreibetrag(
    betrag_ohne_kinderfreibetrag_y_sn: float,
    betrag_mit_kinderfreibetrag_y_sn: float,
    kinderfreibetrag_günstiger_sn: bool,
    relevantes_kindergeld_y_sn: float,
) -> float:
    """Income tax calculation on Steuernummer level since 1997.

    Parameters
    ----------
    betrag_ohne_kinderfreibetrag_y_sn
        See :func:`betrag_ohne_kinderfreibetrag_y_sn`.
    betrag_mit_kinderfreibetrag_y_sn
        See :func:`betrag_mit_kinderfreibetrag_y_sn`.
    kinderfreibetrag_günstiger_sn
        See :func:`kinderfreibetrag_günstiger_sn`.
    relevantes_kindergeld_y_sn
        See :func:`relevantes_kindergeld_y_sn`.

    Returns
    -------

    """
    if kinderfreibetrag_günstiger_sn:
        out = betrag_mit_kinderfreibetrag_y_sn + relevantes_kindergeld_y_sn
    else:
        out = betrag_ohne_kinderfreibetrag_y_sn

    return out


@policy_function()
def kinderfreibetrag_günstiger_sn(
    betrag_ohne_kinderfreibetrag_y_sn: float,
    betrag_mit_kinderfreibetrag_y_sn: float,
    relevantes_kindergeld_y_sn: float,
) -> bool:
    """Kinderfreibetrag more favorable than Kindergeld.

    Parameters
    ----------
    betrag_ohne_kinderfreibetrag_y_sn
        See :func:`betrag_ohne_kinderfreibetrag_y_sn`.
    betrag_mit_kinderfreibetrag_y_sn
        See :func:`betrag_mit_kinderfreibetrag_y_sn`.
    relevantes_kindergeld_y_sn
        See :func:`relevantes_kindergeld_y_sn`.
    Returns
    -------

    """
    unterschiedsbeitrag = (
        betrag_ohne_kinderfreibetrag_y_sn - betrag_mit_kinderfreibetrag_y_sn
    )

    out = unterschiedsbeitrag > relevantes_kindergeld_y_sn
    return out


@policy_function(end_date="2001-12-31", leaf_name="betrag_mit_kinderfreibetrag_y_sn")
def betrag_mit_kinderfreibetrag_y_sn_bis_2001() -> float:
    raise NotImplementedError("Tax system before 2002 is not implemented yet.")


@policy_function(start_date="2002-01-01", leaf_name="betrag_mit_kinderfreibetrag_y_sn")
def betrag_mit_kinderfreibetrag_y_sn_ab_2002(
    einkommensteuer__einkommen__zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    demographics__anzahl_personen_sn: int,
    eink_st_params: dict,
) -> float:
    """Taxes with child allowance on Steuernummer level. Also referred to as "tarifliche
    ESt I".

    Parameters
    ----------
    einkommensteuer__einkommen__zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
        See :func:`einkommensteuer__einkommen__zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn`.
    demographics__anzahl_personen_sn
        See :func:`demographics__anzahl_personen_sn`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = (
        einkommensteuer__einkommen__zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
        / demographics__anzahl_personen_sn
    )
    out = demographics__anzahl_personen_sn * einkommensteuer_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


@policy_function(params_key_for_rounding="eink_st")
def betrag_ohne_kinderfreibetrag_y_sn(
    einkommensteuer__einkommen__zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn: float,
    demographics__anzahl_personen_sn: int,
    eink_st_params: dict,
) -> float:
    """Taxes without child allowance on Steuernummer level. Also referred to as
    "tarifliche ESt II".

    Parameters
    ----------
    einkommensteuer__einkommen__zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn
        See :func:`einkommensteuer__einkommen__zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn`.
    demographics__anzahl_personen_sn
        See :func:`demographics__anzahl_personen_sn`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = (
        einkommensteuer__einkommen__zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn
        / demographics__anzahl_personen_sn
    )
    out = demographics__anzahl_personen_sn * einkommensteuer_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


@policy_function(end_date="2022-12-31", leaf_name="relevantes_kindergeld_m")
def relevantes_kindergeld_mit_staffelung_m(
    anzahl_kindergeld_ansprüche_1: int,
    anzahl_kindergeld_ansprüche_2: int,
    kindergeld_params: dict,
) -> float:
    """Kindergeld relevant for income tax. For each parent, half of the actual
    Kindergeld claim is considered.

    Source: § 31 Satz 4 EStG: "Bei nicht zusammenveranlagten Eltern wird der
    Kindergeldanspruch im Umfang des Kinderfreibetrags angesetzt."

    Parameters
    ----------
    anzahl_kindergeld_ansprüche_1
        See :func:`anzahl_kindergeld_ansprüche_1`.
    anzahl_kindergeld_ansprüche_2
        See :func:`anzahl_kindergeld_ansprüche_2`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    Returns
    -------
    """
    kindergeld_ansprüche = anzahl_kindergeld_ansprüche_1 + anzahl_kindergeld_ansprüche_2

    if kindergeld_ansprüche == 0:
        relevantes_kindergeld = 0.0
    else:
        relevantes_kindergeld = sum(
            kindergeld_params["kindergeld"][
                (min(i, max(kindergeld_params["kindergeld"])))
            ]
            for i in range(1, kindergeld_ansprüche + 1)
        )

    return relevantes_kindergeld / 2


@policy_function(start_date="2023-01-01", leaf_name="relevantes_kindergeld_m")
def relevantes_kindergeld_ohne_staffelung_m(
    anzahl_kindergeld_ansprüche_1: int,
    anzahl_kindergeld_ansprüche_2: int,
    kindergeld_params: dict,
) -> float:
    """Kindergeld relevant for income tax. For each parent, half of the actual
    Kindergeld claim is considered.

    Source: § 31 Satz 4 EStG: "Bei nicht zusammenveranlagten Eltern wird der
    Kindergeldanspruch im Umfang des Kinderfreibetrags angesetzt."

    Parameters
    ----------
    anzahl_kindergeld_ansprüche_1
        See :func:`anzahl_kindergeld_ansprüche_1`.
    anzahl_kindergeld_ansprüche_2
        See :func:`anzahl_kindergeld_ansprüche_2`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    Returns
    -------

    """
    kindergeld_ansprüche = anzahl_kindergeld_ansprüche_1 + anzahl_kindergeld_ansprüche_2
    return kindergeld_params["kindergeld"] * kindergeld_ansprüche / 2


def einkommensteuer_tarif(x: float, params: dict) -> float:
    """The German income tax tariff.

    Parameters
    ----------
    x : float
        The series of floats which the income tax schedule is applied to.
    params : dict
        Dictionary created in respy.piecewise_functions.

    Returns
    -------

    """
    out = piecewise_polynomial(
        x=x,
        thresholds=params["eink_st_tarif"]["thresholds"],
        rates=params["eink_st_tarif"]["rates"],
        intercepts_at_lower_thresholds=params["eink_st_tarif"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out
