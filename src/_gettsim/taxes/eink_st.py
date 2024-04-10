from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import policy_info

aggregate_by_p_id_eink_st = {
    "eink_st_rel_kindergeld_anz_ansprüche_1": {
        "p_id_to_aggregate_by": "p_id_elternteil_1",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
    "eink_st_rel_kindergeld_anz_ansprüche_2": {
        "p_id_to_aggregate_by": "p_id_elternteil_2",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}


def eink_st_ohne_kinderfreib_y_sn(
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
    out = anz_personen_sn * _eink_st_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


@policy_info(end_date="2001-12-31", name_in_dag="eink_st_mit_kinderfreib_y_sn")
def eink_st_mit_kinderfreib_y_sn_bis_2001() -> float:
    raise NotImplementedError("Tax system before 2002 is not implemented yet.")


@policy_info(start_date="2002-01-01", name_in_dag="eink_st_mit_kinderfreib_y_sn")
def eink_st_mit_kinderfreib_y_sn_ab_2002(
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
    out = anz_personen_sn * _eink_st_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


def _eink_st_tarif(x: float, params: dict) -> float:
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


@policy_info(
    end_date="1996-12-31", name_in_dag="eink_st_y_sn", params_key_for_rounding="eink_st"
)
def eink_st_y_sn_kindergeld_kinderfreib_parallel(
    eink_st_mit_kinderfreib_y_sn: float,
) -> float:
    """Income tax calculation on Steuernummer level allowing for claiming
    Kinderfreibetrag and receiving Kindergeld at the same time.

    Parameters
    ----------
    eink_st_mit_kinderfreib_y_sn
        See :func:`eink_st_mit_kinderfreib_y_sn`.

    Returns
    -------

    """
    return eink_st_mit_kinderfreib_y_sn


@policy_info(
    start_date="1997-01-01",
    name_in_dag="eink_st_y_sn",
    params_key_for_rounding="eink_st",
)
def eink_st_y_sn_kindergeld_oder_kinderfreib(
    eink_st_ohne_kinderfreib_y_sn: float,
    eink_st_mit_kinderfreib_y_sn: float,
    kinderfreib_günstiger_sn: bool,
    eink_st_rel_kindergeld_y_sn: float,
) -> float:
    """Income tax calculation on Steuernummer level since 1997.

    Parameters
    ----------
    eink_st_ohne_kinderfreib_y_sn
        See :func:`eink_st_ohne_kinderfreib_y_sn`.
    eink_st_mit_kinderfreib_y_sn
        See :func:`eink_st_mit_kinderfreib_y_sn`.
    kinderfreib_günstiger_sn
        See :func:`kinderfreib_günstiger_sn`.
    eink_st_rel_kindergeld_y_sn
        See :func:`eink_st_rel_kindergeld_y_sn`.

    Returns
    -------

    """
    if kinderfreib_günstiger_sn:
        out = eink_st_mit_kinderfreib_y_sn + eink_st_rel_kindergeld_y_sn
    else:
        out = eink_st_ohne_kinderfreib_y_sn

    return out


def kinderfreib_günstiger_sn(
    eink_st_ohne_kinderfreib_y_sn: float,
    eink_st_mit_kinderfreib_y_sn: float,
    eink_st_rel_kindergeld_y_sn: float,
) -> bool:
    """Kinderfreibetrag more favorable than Kindergeld.

    Parameters
    ----------
    eink_st_ohne_kinderfreib_y_sn
        See :func:`eink_st_ohne_kinderfreib_y_sn`.
    eink_st_mit_kinderfreib_y_sn
        See :func:`eink_st_mit_kinderfreib_y_sn`.
    eink_st_rel_kindergeld_y_sn
        See :func:`eink_st_rel_kindergeld_y_sn`.
    Returns
    -------

    """
    unterschiedsbeitrag = eink_st_ohne_kinderfreib_y_sn - eink_st_mit_kinderfreib_y_sn

    out = unterschiedsbeitrag > eink_st_rel_kindergeld_y_sn
    return out


@policy_info(start_date="2023-01-01", name_in_dag="eink_st_rel_kindergeld_m")
def eink_st_rel_kindergeld_ohne_staffelung_m(
    eink_st_rel_kindergeld_anz_ansprüche_1: int,
    eink_st_rel_kindergeld_anz_ansprüche_2: int,
    kindergeld_params: dict,
) -> float:
    """Kindergeld relevant for income tax. For each parent, half of the actual
    Kindergeld claim is considered.

    Source: § 31 Satz 4 EStG: "Bei nicht zusammenveranlagten Eltern wird der
    Kindergeldanspruch im Umfang des Kinderfreibetrags angesetzt."

    Parameters
    ----------
    eink_st_rel_kindergeld_anz_ansprüche_1
        See :func:`eink_st_rel_kindergeld_anz_ansprüche_1`.
    eink_st_rel_kindergeld_anz_ansprüche_2
        See :func:`eink_st_rel_kindergeld_anz_ansprüche_2`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    Returns
    -------

    """
    eink_st_rel_kindergeld_anz_ansprüche = (
        eink_st_rel_kindergeld_anz_ansprüche_1 + eink_st_rel_kindergeld_anz_ansprüche_2
    )
    return kindergeld_params["kindergeld"] * eink_st_rel_kindergeld_anz_ansprüche / 2


@policy_info(end_date="2022-12-31", name_in_dag="eink_st_rel_kindergeld_m")
def eink_st_rel_kindergeld_mit_staffelung_m(
    eink_st_rel_kindergeld_anz_ansprüche_1: int,
    eink_st_rel_kindergeld_anz_ansprüche_2: int,
    kindergeld_params: dict,
) -> float:
    """Kindergeld relevant for income tax. For each parent, half of the actual
    Kindergeld claim is considered.

    Source: § 31 Satz 4 EStG: "Bei nicht zusammenveranlagten Eltern wird der
    Kindergeldanspruch im Umfang des Kinderfreibetrags angesetzt."

    Parameters
    ----------
    eink_st_rel_kindergeld_anz_ansprüche_1
        See :func:`eink_st_rel_kindergeld_anz_ansprüche_1`.
    eink_st_rel_kindergeld_anz_ansprüche_2
        See :func:`eink_st_rel_kindergeld_anz_ansprüche_2`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.
    Returns
    -------
    """
    eink_st_rel_kindergeld_anz_ansprüche = (
        eink_st_rel_kindergeld_anz_ansprüche_1 + eink_st_rel_kindergeld_anz_ansprüche_2
    )

    if eink_st_rel_kindergeld_anz_ansprüche == 0:
        sum_eink_st_rel_kindergeld = 0.0
    else:
        sum_eink_st_rel_kindergeld = sum(
            kindergeld_params["kindergeld"][
                (
                    i
                    if i <= max(kindergeld_params["kindergeld"])
                    else max(kindergeld_params["kindergeld"])
                )
            ]
            for i in range(1, eink_st_rel_kindergeld_anz_ansprüche + 1)
        )

    return sum_eink_st_rel_kindergeld / 2
