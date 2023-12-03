#!/usr/bin/python3
from _gettsim.shared import add_rounding_spec, dates_active


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_m(
    erziehungsgeld_kind_m_tu: int,
    erziehungsgeld_anspruch_eltern: bool,
    inanspruchn_erziehungsgeld: bool,
) -> bool:
    """Total parental leave benefits (Erziehungsgeld).

    Legal reference: BErzGG (BGBl. I 1985 S. 2154; BGBl. I 2004 S. 206)

    Parameters
    ----------
    erziehungsgeld_kind_m_tu
        See :func:`erziehungsgeld_kind_m_tu`.
    erziehungsgeld_anspruch_eltern
        See :func:`erziehungsgeld_anspruch_eltern`.
    inanspruchn_erziehungsgeld
        See :See basic input variable :ref:`inanspruchn_erziehungsgeld
        <inanspruchn_erziehungsgeld>`.

    Returns
    -------
    Sum of parental leave benefits (erziehungsgeld) on TU level

    """
    if erziehungsgeld_anspruch_eltern and inanspruchn_erziehungsgeld:
        out = erziehungsgeld_kind_m_tu
    else:
        out = 0.0

    return out


@add_rounding_spec(params_key="erziehungsgeld")
@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_kind_m(  # noqa: PLR0913
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_eink_relev_kind: float,
    erziehungsgeld_einkommensgrenze_kind: float,
    budget_erziehungsgeld: bool,
    kind_bis_7m: bool,
    kind_ab_7m_bis_12m: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Parental leave benefit (erziehungsgeld) on child level.

    For the calculation, the relevant wage, the age of the youngest child,
    the income threshold and the eligibility for erziehungsgeld is needed.

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6

    Parameters
    ----------
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.
    erziehungsgeld_eink_relev_kind
        See :func:`erziehungsgeld_eink_relev_kind`.
    erziehungsgeld_einkommensgrenze_kind
        See :func:`erziehungsgeld_einkommensgrenze_kind`.
    budget_erziehungsgeld
        See :See basic input variable :ref:`budget_erziehungsgeld
        <budget_erziehungsgeld>`.
    kind_bis_7m
        See :func:`kind_bis_7m`.
    kind_ab_7m_bis_12m
        See :func:`kind_ab_7m_bis_12m`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.


    Returns
    -------
    monthly claim of parental leave benefit (erziehungsgeld) on child level

    """

    abzug = (erziehungsgeld_eink_relev_kind / 12) * erziehungsgeld_params[
        "abschlag_faktor"
    ]
    # If the child is younger than 7 months and the income is below the income limit,
    # the full normal rate or budget rate is paid out
    if (
        erziehungsgeld_anspruch_kind
        and kind_bis_7m
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkommensgrenze_kind
        and budget_erziehungsgeld
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]

    elif (
        erziehungsgeld_anspruch_kind
        and kind_bis_7m
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkommensgrenze_kind
        and (not budget_erziehungsgeld)
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]
    # if the income is higher than the threshold and the child is older than
    # 7 month the parental leave benefit is reduced
    elif (
        erziehungsgeld_anspruch_kind
        and kind_ab_7m_bis_12m
        and erziehungsgeld_eink_relev_kind > erziehungsgeld_einkommensgrenze_kind
        and budget_erziehungsgeld
    ):
        out = max(
            erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"] - abzug, 0.0
        )
    elif (
        erziehungsgeld_anspruch_kind
        and kind_ab_7m_bis_12m
        and erziehungsgeld_eink_relev_kind > erziehungsgeld_einkommensgrenze_kind
        and (not budget_erziehungsgeld)
    ):
        out = max(
            erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"] - abzug, 0.0
        )
    # If the child is older than 7 months and the income is below the income limit,
    # the full normal or budget rate is paid out
    elif (
        erziehungsgeld_anspruch_kind
        and kind_ab_7m_bis_12m
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkommensgrenze_kind
        and (not budget_erziehungsgeld)
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]
    elif (
        erziehungsgeld_anspruch_kind
        and kind_ab_7m_bis_12m
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkommensgrenze_kind
        and budget_erziehungsgeld
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]
    # if the income is higher than the threshold within the first 6 month there
    # is no erziehungsgeld claim at all
    else:
        out = 0.0

    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_anspruch_kind(
    kind_bis_12m: bool,
    kind_bis_24m: bool,
    budget_erziehungsgeld: bool,
) -> bool:
    """Determine the eligibility for parental leave benefit (erziehungsgeld) on child
    level.

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.207)

    Parameters
    ----------
    kind_bis_12m
        See :func:`kind_bis_12m`.
    kind_bis_24m
        See :func:`kind_bis_24m`.
    budget_erziehungsgeld
        See :See basic input variable :ref:`budget_erziehungsgeld
        <budget_erziehungsgeld>`.


    Returns
    -------
    eligibility of (erziehungsgeld) as a bool

    """
    if budget_erziehungsgeld:
        out = kind_bis_12m

    else:
        out = kind_bis_24m

    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_anspruch_eltern(
    arbeitsstunden_w: float,
    hat_kinder: bool,
    erziehungsgeld_anspruch_kind_tu: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Determine the eligibility for parental leave benefit (erziehungsgeld) on
    parental level.

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.207)

    Parameters
    ----------
    arbeitsstunden_w
        See :See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    hat_kinder
        See :See basic input variable :ref:`hat_kinder <hat_kinder>`.
    erziehungsgeld_anspruch_kind_tu
        See :func:`erziehungsgeld_anspruch_kind_tu`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of parental leave benefit (erziehungsgeld) as a bool

    """
    out = (
        erziehungsgeld_anspruch_kind_tu
        and (arbeitsstunden_w <= erziehungsgeld_params["arbeitsstunden_w_grenze"])
        and hat_kinder
    )

    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_eink_relev_kind(
    bruttolohn_vorj_m_tu: float,
    anz_erwachsene_tu: int,
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_params: dict,
    eink_st_abzuege_params: dict,
) -> float:
    """Relevant wage for parental leave benefit (erziehungsgeld) on child
    level

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.209)

    There is special rule for "Beamte, Soldaten und Richter" which is not
    implemented yet

    Parameters
    ----------
    bruttolohn_vorj_m_tu
        See :func:`bruttolohn_vorj_m_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------
    relevant wage for calculation parental leave benefit (erziehungsgeld)
    """

    if erziehungsgeld_anspruch_kind:
        out = (
            bruttolohn_vorj_m_tu * 12
            - eink_st_abzuege_params["werbungskostenpauschale"] * anz_erwachsene_tu
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    else:
        out = 0.0
    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_einkommensgrenze_kind(
    erziehungsgeld_einkommensgrenze_vor_aufschl: float,
    anz_kinder_mit_kindergeld_tu: float,
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (erziehungsgeld)
    on child level

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    erziehungsgeld_einkommensgrenze_vor_aufschl
        See :func:`erziehungsgeld_einkommensgrenze_vor_aufschl`.
    anz_kinder_mit_kindergeld_tu
        See :func:`anz_kinder_mit_kindergeld_tu`.
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    income threshold for parental leave benefit (erziehungsgeld) on child level
    """
    out = (
        erziehungsgeld_einkommensgrenze_vor_aufschl
        + (anz_kinder_mit_kindergeld_tu - 1)
        * erziehungsgeld_params["aufschlag_einkommen"]
    )
    if not erziehungsgeld_anspruch_kind:
        out = 0.0
    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_einkommensgrenze_vor_aufschl(
    alleinerz_tu: bool,
    kind_bis_7m: bool,
    budget_erziehungsgeld: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (erziehungsgeld)
    on child level before adding the bonus for additional children

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    alleinerz_tu
        See :func:`alleinerz_tu`.
    kind_bis_7m
        See :func:`kind_bis_7m`.
    budget_erziehungsgeld
        See :See basic input variable :ref:`budget_erziehungsgeld
        <budget_erziehungsgeld>`.

    Returns
    -------
    income threshold for parental leave benefit (erziehungsgeld) before child bonus
    """
    # There are different income thresholds depending on the age of the child,
    # the fact if a person is a single parent, and if regelsatz or budgetsatz is applied

    if kind_bis_7m:
        alter_kind = "kind_bis_7m"
    else:
        alter_kind = "kind_ab_7m"

    if alleinerz_tu:
        status_eltern = "alleinerz"
    else:
        status_eltern = "paar"

    if budget_erziehungsgeld:
        satz = "budgetsatz"
    else:
        satz = "regelsatz"

    out = erziehungsgeld_params["einkommensgrenze"][alter_kind][status_eltern][satz]

    return out
