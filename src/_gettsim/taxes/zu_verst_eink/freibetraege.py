from _gettsim.config import numpy_or_jax as np
from _gettsim.shared import add_rounding_spec, dates_active


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


@dates_active(end="2014-12-31", change_name="alleinerz_freib_y_tu")
def eink_st_alleinerz_freib_y_tu_pauschal(
    alleinerz_tu: bool, eink_st_abzuege_params: dict
) -> float:
    """Calculate tax deduction allowance for single parents until 2014.

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


@dates_active(start="2015-01-01", change_name="alleinerz_freib_y_tu")
def eink_st_alleinerz_freib_y_tu_nach_kinderzahl(
    alleinerz: bool,
    anz_kinder_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for single parents since 2015.

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
    alleinerz_freib_y_tu = (
        eink_st_abzuege_params["alleinerz_freibetrag"]
        + (anz_kinder_tu - 1) * eink_st_abzuege_params["alleinerz_freibetrag_zusatz"]
    )
    if alleinerz:
        out = alleinerz_freib_y_tu
    else:
        out = 0.0

    return out


@dates_active(end="2004-12-31", change_name="eink_st_altersfreib_y")
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


@dates_active(start="2005-01-01", change_name="eink_st_altersfreib_y")
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


@dates_active(end="2011-12-31", change_name="eink_st_sonderausgaben_y_tu")
def eink_st_sonderausgaben_y_tu_nur_pauschale(
    eink_st_abzuege_params: dict,
    anz_erwachsene_tu: int,
) -> float:
    """Individual Sonderausgaben on tax unit level until 2011.

    Only a lump sum payment is implemented.

    Parameters
    ----------
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    anz_erwachsene_tu
        See func `anz_erwachsene_tu <anz_erwachsene_tu>`.

    Returns
    -------

    """
    # so far, only the Sonderausgabenpauschale is considered

    out = (
        eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"]
        * anz_erwachsene_tu
    )

    return float(out)


@dates_active(start="2012-01-01", change_name="eink_st_sonderausgaben_y_tu")
def eink_st_sonderausgaben_y_tu_mit_betreuung(
    eink_st_abzuege_params: dict,
    sonderausgaben_betreuung_y_tu: float,
    anz_erwachsene_tu: int,
) -> float:
    """Individual sonderausgaben on tax unit level since 2012.

    We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg.

    Parameters
    ----------
    kind
        See basic input variable :ref:`kind <kind>`.
    sonderausgaben_betreuung_y_tu
        See :func:`sonderausgaben_betreuung_y_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.

    Returns
    -------

    """
    sonderausgaben_gesamt = sonderausgaben_betreuung_y_tu
    pauschale = (
        eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"]
        * anz_erwachsene_tu
    )

    out = max(sonderausgaben_gesamt, pauschale)

    return float(out)


def eink_st_abz_betreuungskost_y(
    eink_st_abzuege_params: dict,
    betreuungskost_m: float,
) -> float:
    """Individual deductable childcare cost for each individual child under 14.

    Parameters
    ----------
    betreuungskost_m
        See basic input variable :ref:`betreuungskost_m <betreuungskost_m>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = min(
        12 * betreuungskost_m,
        eink_st_abzuege_params["kinderbetreuungskosten_abz_maximum"],
    )
    return out


@add_rounding_spec(params_key="eink_st_abzuege")
def sonderausgaben_betreuung_y_tu(
    eink_st_abzuege_params: dict,
    eink_st_abz_betreuungskost_y_tu: float,
) -> float:
    """Sonderausgaben for childcare on tax unit level.

    We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg.

    Parameters
    ----------
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    eink_st_abz_betreuungskost_y_tu
        See :func:`eink_st_abz_betreuungskost_y_tu`.

    Returns
    -------

    """

    out = (
        eink_st_abz_betreuungskost_y_tu
        * eink_st_abzuege_params["kinderbetreuungskosten_abz_anteil"]
    )

    return float(out)


def eink_st_kinderfreib_y_tu(
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
    kinderfreib_total = sum(eink_st_abzuege_params["kinderfreib"].values())
    out = kinderfreib_total * anz_kinder_mit_kindergeld_tu * anz_erwachsene_tu

    return float(out)
