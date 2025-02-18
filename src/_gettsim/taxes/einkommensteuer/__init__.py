"""Income taxes."""

from _gettsim.piecewise_functions import piecewise_polynomial

aggregate_by_p_id_eink_st = {
    "anzahl_kindergeld_ansprüche_1": {
        "p_id_to_aggregate_by": "p_id_elternteil_1",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
    "anzahl_kindergeld_ansprüche_2": {
        "p_id_to_aggregate_by": "p_id_elternteil_2",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}


@policy_info(
    end_date="1996-12-31", name_in_dag="betrag_y_sn", params_key_for_rounding="eink_st"
)
def betrag_y_sn_kindergeld_kinderfreib_parallel(
    betrag_mit_kinderfreib_y_sn: float,
) -> float:
    """Income tax calculation on Steuernummer level allowing for claiming
    Kinderfreibetrag and receiving Kindergeld at the same time.

    Parameters
    ----------
    betrag_mit_kinderfreib_y_sn
        See :func:`betrag_mit_kinderfreib_y_sn`.

    Returns
    -------

    """
    return betrag_mit_kinderfreib_y_sn


@policy_info(
    start_date="1997-01-01",
    name_in_dag="betrag_y_sn",
    params_key_for_rounding="eink_st",
)
def betrag_y_sn_kindergeld_oder_kinderfreib(
    betrag_ohne_kinderfreib_y_sn: float,
    betrag_mit_kinderfreib_y_sn: float,
    kinderfreib_günstiger_sn: bool,
    relevantes_kindergeld_y_sn: float,
) -> float:
    """Income tax calculation on Steuernummer level since 1997.

    Parameters
    ----------
    betrag_ohne_kinderfreib_y_sn
        See :func:`betrag_ohne_kinderfreib_y_sn`.
    betrag_mit_kinderfreib_y_sn
        See :func:`betrag_mit_kinderfreib_y_sn`.
    kinderfreib_günstiger_sn
        See :func:`kinderfreib_günstiger_sn`.
    relevantes_kindergeld_y_sn
        See :func:`relevantes_kindergeld_y_sn`.

    Returns
    -------

    """
    if kinderfreib_günstiger_sn:
        out = betrag_mit_kinderfreib_y_sn + relevantes_kindergeld_y_sn
    else:
        out = betrag_ohne_kinderfreib_y_sn

    return out


def kinderfreib_günstiger_sn(
    betrag_ohne_kinderfreib_y_sn: float,
    betrag_mit_kinderfreib_y_sn: float,
    relevantes_kindergeld_y_sn: float,
) -> bool:
    """Kinderfreibetrag more favorable than Kindergeld.

    Parameters
    ----------
    betrag_ohne_kinderfreib_y_sn
        See :func:`betrag_ohne_kinderfreib_y_sn`.
    betrag_mit_kinderfreib_y_sn
        See :func:`betrag_mit_kinderfreib_y_sn`.
    relevantes_kindergeld_y_sn
        See :func:`relevantes_kindergeld_y_sn`.
    Returns
    -------

    """
    unterschiedsbeitrag = betrag_ohne_kinderfreib_y_sn - betrag_mit_kinderfreib_y_sn

    out = unterschiedsbeitrag > relevantes_kindergeld_y_sn
    return out


@policy_info(end_date="2001-12-31", name_in_dag="betrag_mit_kinderfreib_y_sn")
def betrag_mit_kinderfreib_y_sn_bis_2001() -> float:
    raise NotImplementedError("Tax system before 2002 is not implemented yet.")


@policy_info(start_date="2002-01-01", name_in_dag="betrag_mit_kinderfreib_y_sn")
def betrag_mit_kinderfreib_y_sn_ab_2002(
    _zu_verst_eink_mit_kinderfreib_y_sn: float,
    anz_personen_sn: int,
    eink_st_params: dict,
) -> float:
    """Taxes with child allowance on Steuernummer level. Also referred to as "tarifliche
    ESt I".

    Parameters
    ----------
    _zu_verst_eink_mit_kinderfreib_y_sn
        See :func:`_zu_verst_eink_mit_kinderfreib_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_mit_kinderfreib_y_sn / anz_personen_sn
    out = anz_personen_sn * einkommensteuer_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


def betrag_ohne_kinderfreib_y_sn(
    _zu_verst_eink_ohne_kinderfreib_y_sn: float,
    anz_personen_sn: int,
    eink_st_params: dict,
) -> float:
    """Taxes without child allowance on Steuernummer level. Also referred to as
    "tarifliche ESt II".

    Parameters
    ----------
    _zu_verst_eink_ohne_kinderfreib_y_sn
        See :func:`_zu_verst_eink_ohne_kinderfreib_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_ohne_kinderfreib_y_sn / anz_personen_sn
    out = anz_personen_sn * einkommensteuer_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


@policy_info(end_date="2022-12-31", name_in_dag="relevantes_kindergeld_m")
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


@policy_info(start_date="2023-01-01", name_in_dag="relevantes_kindergeld_m")
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
