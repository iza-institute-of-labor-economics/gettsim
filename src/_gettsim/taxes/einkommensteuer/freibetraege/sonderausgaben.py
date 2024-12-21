"""Tax allowances for special expenses."""

from _gettsim.shared import policy_info

aggregate_by_p_id_sonderausgaben = {
    "betreuungskosten_elternteil_m": {
        "p_id_to_aggregate_by": "p_id_betreuungsk_träger",
        "source_col": "betreuungskosten_m",
        "aggr": "sum",
    },
}


@policy_info(end_date="2011-12-31", name_in_dag="betrag_y_sn")
def betrag_y_sn_nur_pauschale(
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
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


@policy_info(start_date="2012-01-01", name_in_dag="betrag_y_sn")
def betrag_y_sn_mit_betreuung(
    absetzbare_betreuungskosten: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Sonderausgaben on Steuernummer level since 2012.

    We follow 10 Abs.1 Nr. 5 EStG. You can find
    details here https://www.buzer.de/s1.htm?a=10&g=estg.

    Parameters
    ----------
    absetzbare_betreuungskosten
        See :func:`absetzbare_betreuungskosten`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    anz_personen_sn
        See :func:`anz_personen_sn`.

    Returns
    -------

    """
    sonderausgaben_gesamt = absetzbare_betreuungskosten
    pauschale = (
        eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"] * anz_personen_sn
    )

    out = max(sonderausgaben_gesamt, pauschale)

    return float(out)


def ausgaben_für_betreuung_y(
    betreuungskosten_elternteil_y: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Individual deductable childcare cost for each individual child under 14.

    Parameters
    ----------
    betreuungskosten_elternteil_y
        See :func:`betreuungskosten_elternteil_y`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = min(
        betreuungskosten_elternteil_y,
        eink_st_abzuege_params["kinderbetreuungskosten_abz_maximum"],
    )
    return out


@policy_info(params_key_for_rounding="eink_st_abzuege")
def absetzbare_betreuungskosten_y_sn(
    ausgaben_für_betreuung_y_sn: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Sonderausgaben for childcare on Steuernummer level.

    We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg.

    Parameters
    ----------
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    ausgaben_für_betreuung_y_sn
        See :func:`ausgaben_für_betreuung_y_sn`.

    Returns
    -------

    """

    out = (
        ausgaben_für_betreuung_y_sn
        * eink_st_abzuege_params["kinderbetreuungskosten_abz_anteil"]
    )

    return float(out)
