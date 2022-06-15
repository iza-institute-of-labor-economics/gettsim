import numpy as np

from gettsim.shared import add_rounding_spec


def _eink_st_behinderungsgrad_pauschbetrag(
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
        np.searchsorted(bins + [np.inf], behinderungsgrad, side="right") - 1
    )
    selected_bin = bins[selected_bin_index]

    # Select appropriate pauschbetrag.
    out = eink_st_abzuege_params["behinderten_pauschbetrag"][selected_bin]

    return out


def eink_st_alleinerz_freib_tu_bis_2014(
    alleinerz_tu: bool, eink_st_abzuege_params: dict
) -> float:
    """Calculates tax deduction allowance for single parents until 2014.

    This used to be called 'Haushaltsfreibetrag'.

    Parameters
    ----------
    alleinerz_tu
        See :func:`alleinerz_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    if alleinerz_tu:
        out = eink_st_abzuege_params["alleinerz_freibetrag"]
    else:
        out = 0.0

    return out


def eink_st_alleinerz_freib_tu_ab_2015(
    alleinerz: bool,
    anz_kinder_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculates tax deduction allowance for single parents since 2015.

    Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'

    Parameters
    ----------
    alleinerz_tu
        See :func:`alleinerz_tu`.
    anz_kinder_tu
        See :func:`anz_kinder_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    alleinerz_freib_tu = (
        eink_st_abzuege_params["alleinerz_freibetrag"]
        + (anz_kinder_tu - 1) * eink_st_abzuege_params["alleinerz_freibetrag_zusatz"]
    )
    if alleinerz:
        out = alleinerz_freib_tu
    else:
        out = 0.0

    return out


def eink_st_altersfreib_bis_2004(
    bruttolohn_m: float,
    alter: int,
    kapitaleink_brutto_m: float,
    eink_selbst_m: float,
    eink_vermietung_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculates tax deduction allowance for elderly.

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
        out = (
            eink_st_abzuege_params["altersentlastung_quote"]
            * 12
            * (bruttolohn_m + weiteres_einkommen)
        )
        out = min(out, eink_st_abzuege_params["altersentlastungsbetrag_max"])
    else:
        out = 0.0

    return out


def eink_st_altersfreib_ab_2005(
    bruttolohn_m: float,
    alter: int,
    geburtsjahr: int,
    kapitaleink_brutto_m: float,
    eink_selbst_m: float,
    eink_vermietung_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculates tax deduction allowance for elderly.

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

    Returns
    -------

    """
    altersgrenze = eink_st_abzuege_params["altersentlastungsbetrag_altersgrenze"]
    weiteres_einkommen = max(
        kapitaleink_brutto_m + eink_selbst_m + eink_vermietung_m, 0.0
    )
    if alter > altersgrenze:
        if geburtsjahr <= 1939:
            selected_bin = 1940

        else:
            # Get maximum tax credit
            bins = sorted(eink_st_abzuege_params["altersentlastungsbetrag_max"])

            # Select corresponding bin.
            selected_bin_index = (
                np.searchsorted(bins + [np.inf], geburtsjahr, side="right") - 1
            )

            selected_bin = bins[selected_bin_index]

        # Select appropriate tax credit threshold and quota.
        out_max = eink_st_abzuege_params["altersentlastungsbetrag_max"][selected_bin]
        quo = eink_st_abzuege_params["altersentlastung_quote"][selected_bin]

        out_quo = quo * 12 * (bruttolohn_m + weiteres_einkommen)
        out = min(out_quo, out_max)
    else:
        out = 0.0

    return out


def eink_st_sonderausgaben_bis_2011(
    kind: bool,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculating sonderausgaben for childcare until 2011.

    There is only a lumpsum payment implemented.
    Parameters
    ----------
    kind
        See basic input variable :ref:`kind <kind>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    # so far, only the Sonderausgabenpauschale is considered

    if kind:
        out = 0.0
    else:
        out = eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"]

    return out


@add_rounding_spec(params_key="eink_st_abzuege")
def sonderausgaben_betreuung(
    eink_st_abzuege_params: dict,
    anz_kinder_bis_13_tu: int,
    betreuungskost_m: float,
    anz_erwachsene_tu: int,
) -> float:
    """Calculate sonderausgaben for childcare for childen under 14.

    We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg.
    Parameters
    ----------
    betreuungskost_m
        See basic input variable :ref:`betreuungskost_m <betreuungskost_m>`.
    anz_kinder_bis_13_tu
        See :func:`anz_kinder_bis_13_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    """

    abziehbare_betreuungskosten = min(
        12 * betreuungskost_m,
        eink_st_abzuege_params["kinderbetreuungskosten_abz_maximum"],
    )
    out = (
        anz_kinder_bis_13_tu
        * abziehbare_betreuungskosten
        * eink_st_abzuege_params["kinderbetreuungskosten_abz_anteil"]
    ) / anz_erwachsene_tu

    return out


def eink_st_sonderausgaben_ab_2012(
    kind: bool,
    eink_st_abzuege_params: dict,
    sonderausgaben_betreuung: float,
) -> float:
    """Calculate sonderausgaben since 2012.

    We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg.
    Parameters
    ----------
    kind
        See basic input variable :ref:`kind <kind>`.
    sonderausgaben_betreuung
        See :func:`sonderausgaben_betreuung`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    sonderausgaben_gesamt = sonderausgaben_betreuung
    pauschale = eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"]

    if kind:
        out = 0.0
    elif sonderausgaben_gesamt > pauschale:
        out = sonderausgaben_gesamt
    else:
        out = eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"]

    return out


def eink_st_kinderfreib_tu(
    anz_kinder_mit_kindergeld_tu: float,
    anz_erwachsene_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Aggregate child allowances on tax unit level.

    Parameters
    ----------
    anz_kinder_mit_kindergeld_tu
        See :func:`anz_kinder_mit_kindergeld_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    kifreib_total = sum(eink_st_abzuege_params["kinderfreibetrag"].values())
    out = kifreib_total * anz_kinder_mit_kindergeld_tu * anz_erwachsene_tu

    return out
