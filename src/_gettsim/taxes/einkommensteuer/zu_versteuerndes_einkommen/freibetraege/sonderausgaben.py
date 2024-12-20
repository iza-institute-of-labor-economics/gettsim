"""Tax allowances for special expenses."""

from _gettsim.shared import policy_info

aggregate_by_p_id_sonderausgaben = {
    "betreuungskost_elternteil_m": {
        "p_id_to_aggregate_by": "p_id_betreuungsk_träger",
        "source_col": "betreuungskost_m",
        "aggr": "sum",
    },
}


@policy_info(end_date="2011-12-31", name_in_dag="eink_st_sonderausgaben_y_sn")
def eink_st_sonderausgaben_y_sn_nur_pauschale(
    eink_st_abzuege_params: dict,
    anz_personen_sn: int,
) -> float:
    """Sonderausgaben on Steuernummer level until 2011.

    Only a lump sum payment is implemented.

    Parameters
    ----------
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    anz_personen_sn
        See func `anz_personen_sn <anz_personen_sn>`.

    Returns
    -------

    """
    # so far, only the Sonderausgabenpauschale is considered

    out = (
        eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"] * anz_personen_sn
    )

    return float(out)


@policy_info(start_date="2012-01-01", name_in_dag="eink_st_sonderausgaben_y_sn")
def eink_st_sonderausgaben_y_sn_mit_betreuung(
    eink_st_abzuege_params: dict,
    sonderausgaben_betreuung_y_sn: float,
    anz_personen_sn: int,
) -> float:
    """Sonderausgaben on Steuernummer level since 2012.

    We follow 10 Abs.1 Nr. 5 EStG. You can find
    details here https://www.buzer.de/s1.htm?a=10&g=estg.

    Parameters
    ----------
    sonderausgaben_betreuung_y_sn
        See :func:`sonderausgaben_betreuung_y_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    anz_personen_sn
        See :func:`anz_personen_sn`.

    Returns
    -------

    """
    sonderausgaben_gesamt = sonderausgaben_betreuung_y_sn
    pauschale = (
        eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"] * anz_personen_sn
    )

    out = max(sonderausgaben_gesamt, pauschale)

    return float(out)


def eink_st_abz_betreuungskost_y(
    eink_st_abzuege_params: dict,
    betreuungskost_elternteil_y: float,
) -> float:
    """Individual deductable childcare cost for each individual child under 14.

    Parameters
    ----------
    betreuungskost_elternteil_y
        See :func:`betreuungskost_elternteil_y`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = min(
        betreuungskost_elternteil_y,
        eink_st_abzuege_params["kinderbetreuungskosten_abz_maximum"],
    )
    return out


@policy_info(params_key_for_rounding="eink_st_abzuege")
def sonderausgaben_betreuung_y_sn(
    eink_st_abzuege_params: dict,
    eink_st_abz_betreuungskost_y_sn: float,
) -> float:
    """Sonderausgaben for childcare on Steuernummer level.

    We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg.

    Parameters
    ----------
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    eink_st_abz_betreuungskost_y_sn
        See :func:`eink_st_abz_betreuungskost_y_sn`.

    Returns
    -------

    """

    out = (
        eink_st_abz_betreuungskost_y_sn
        * eink_st_abzuege_params["kinderbetreuungskosten_abz_anteil"]
    )

    return float(out)
