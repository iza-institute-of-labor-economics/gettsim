from _gettsim.config import numpy_or_jax as np
from _gettsim.shared import policy_info

aggregate_by_p_id_freibeträge = {
    "_eink_st_kinderfreib_anz_anspruch_1": {
        "p_id_to_aggregate_by": "p_id_kinderfreib_empfänger_1",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
    "_eink_st_kinderfreib_anz_anspruch_2": {
        "p_id_to_aggregate_by": "p_id_kinderfreib_empfänger_2",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
    "betreuungskost_elternteil_m": {
        "p_id_to_aggregate_by": "p_id_betreuungsk_träger",
        "source_col": "betreuungskost_m",
        "aggr": "sum",
    },
}


def _eink_st_kinderfreib_anz_ansprüche(
    _eink_st_kinderfreib_anz_anspruch_1: int,
    _eink_st_kinderfreib_anz_anspruch_2: int,
) -> int:
    """Return the number of Kinderfreibeträge a person is entitled to.

    The person could be a parent or legal custodian.

    Parameters
    ----------
    _eink_st_kinderfreib_anz_anspruch_1
        Helper function based on aggregating
        :ref:`p_id_kinderfreibetr_empfänger_1 <p_id_kinderfreibetr_empfänger_1>`.
    _eink_st_kinderfreib_anz_anspruch_2
        Helper function based on aggregating
        :ref:`p_id_kinderfreibetr_empfänger_2 <p_id_kinderfreibetr_empfänger_2>`.

    """
    return _eink_st_kinderfreib_anz_anspruch_1 + _eink_st_kinderfreib_anz_anspruch_2


def _eink_st_behinderungsgrad_pauschbetrag_y(
    behinderungsgrad: int, eink_st_abzuege_params: dict
) -> float:
    """Assign tax deduction allowance for handicaped to different handicap degrees.

    Parameters
    ----------
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    # Get disability degree thresholds
    bins = sorted(eink_st_abzuege_params["behinderten_pauschbetrag"])

    # Select corresponding bin.
    selected_bin_index = (
        np.searchsorted([*bins, np.inf], behinderungsgrad, side="right") - 1
    )
    selected_bin = bins[selected_bin_index]

    # Select appropriate pauschbetrag.
    out = eink_st_abzuege_params["behinderten_pauschbetrag"][selected_bin]

    return float(out)


@policy_info(end_date="2014-12-31", name_in_dag="alleinerz_freib_y_sn")
def eink_st_alleinerz_freib_y_sn_pauschal(
    alleinerz_sn: bool, eink_st_abzuege_params: dict
) -> float:
    """Calculate tax deduction allowance for single parents until 2014.

    This used to be called 'Haushaltsfreibetrag'.

    Parameters
    ----------
    alleinerz_sn
        See :func:`alleinerz_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    if alleinerz_sn:
        out = eink_st_abzuege_params["alleinerz_freibetrag"]
    else:
        out = 0.0

    return out


@policy_info(start_date="2015-01-01", name_in_dag="alleinerz_freib_y_sn")
def eink_st_alleinerz_freib_y_sn_nach_kinderzahl(
    alleinerz_sn: bool,
    kindergeld_anz_ansprüche_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for single parents since 2015.

    Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'

    Parameters
    ----------
    alleinerz_sn
        See :func:`alleinerz_sn`.
    kindergeld_anz_ansprüche_sn
        See :func:`kindergeld_anz_ansprüche_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    alleinerz_freib_y_sn = (
        eink_st_abzuege_params["alleinerz_freibetrag"]
        + (kindergeld_anz_ansprüche_sn - 1)
        * eink_st_abzuege_params["alleinerz_freibetrag_zusatz"]
    )
    if alleinerz_sn:
        out = alleinerz_freib_y_sn
    else:
        out = 0.0

    return out


@policy_info(end_date="2004-12-31", name_in_dag="eink_st_altersfreib_y")
def eink_st_altersfreib_y_bis_2004(  # noqa: PLR0913
    bruttolohn_m: float,
    alter: int,
    kapitaleink_brutto_m: float,
    eink_selbst_m: float,
    eink_vermietung_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for elderly until 2004.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.
    eink_selbst_m
        See :func:`eink_selbst_m`.
    eink_vermietung_m
        See basic input variable :ref:`eink_vermietung_m <eink_vermietung_m>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    altersgrenze = eink_st_abzuege_params["altersentlastungsbetrag_altersgrenze"]
    weiteres_einkommen = max(
        kapitaleink_brutto_m + eink_selbst_m + eink_vermietung_m, 0.0
    )
    if alter > altersgrenze:
        out = min(
            eink_st_abzuege_params["altersentlastung_quote"]
            * 12
            * (bruttolohn_m + weiteres_einkommen),
            eink_st_abzuege_params["altersentlastungsbetrag_max"],
        )
    else:
        out = 0.0

    return out


@policy_info(start_date="2005-01-01", name_in_dag="eink_st_altersfreib_y")
def eink_st_altersfreib_y_ab_2005(  # noqa: PLR0913
    bruttolohn_m: float,
    geringfügig_beschäftigt: bool,
    alter: int,
    geburtsjahr: int,
    kapitaleink_brutto_m: float,
    eink_selbst_m: float,
    eink_vermietung_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for elderly since 2005.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.
    eink_selbst_m
        See :func:`eink_selbst_m`.
    eink_vermietung_m
        See basic input variable :ref:`eink_vermietung_m <eink_vermietung_m>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    Returns
    -------

    """
    # Maximum tax credit by birth year.
    bins = sorted(eink_st_abzuege_params["altersentlastungsbetrag_max"])
    if geburtsjahr <= 1939:
        selected_bin = 1940
    else:
        # Select corresponding bin.
        selected_bin = bins[
            np.searchsorted([*bins, np.inf], geburtsjahr, side="right") - 1
        ]

    # Select appropriate tax credit threshold and quota.
    out_max = eink_st_abzuege_params["altersentlastungsbetrag_max"][selected_bin]

    einkommen_lohn = 0 if geringfügig_beschäftigt else bruttolohn_m
    weiteres_einkommen = max(
        kapitaleink_brutto_m + eink_selbst_m + eink_vermietung_m, 0.0
    )
    out_quote = (
        eink_st_abzuege_params["altersentlastung_quote"][selected_bin]
        * 12
        * (einkommen_lohn + weiteres_einkommen)
    )

    if alter > eink_st_abzuege_params["altersentlastungsbetrag_altersgrenze"]:
        out = min(out_quote, out_max)
    else:
        out = 0.0

    return out


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


def eink_st_kinderfreib_y(
    _eink_st_kinderfreib_anz_ansprüche: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Individual child allowance.

    Parameters
    ----------
    _eink_st_kinderfreib_anz_ansprüche
        See :func:`_eink_st_kinderfreib_anz_ansprüche`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    return float(
        sum(eink_st_abzuege_params["kinderfreib"].values())
        * _eink_st_kinderfreib_anz_ansprüche
    )


def p_id_kinderfreib_empfänger_1(
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


def p_id_kinderfreib_empfänger_2(
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
