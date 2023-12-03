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
    Sum of parental leave benefits (Erziehungsgeld) on TU level

    """
    if erziehungsgeld_anspruch_eltern and inanspruchn_erziehungsgeld:
        out = erziehungsgeld_kind_m_tu
    else:
        out = 0.0

    return out


@add_rounding_spec(params_key="erziehungsgeld")
@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_kind_m(
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_abzug_transfer: float,
    erziehungsgeld_ohne_abzug_m: float,
) -> float:
    """Parental leave benefit (Erziehungsgeld) on child level.

    For the calculation, the relevant income, the age of the youngest child,
    the income threshold and the eligibility for erziehungsgeld is needed.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6

    Parameters
    ----------
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.
    erziehungsgeld_abzug_transfer
        See :func:`erziehungsgeld_abzug_transfer`.
    erziehungsgeld_ohne_abzug_m
        See :func:`erziehungsgeld_ohne_abzug`.


    Returns
    -------
    Monthly claim of parental leave benefit (Erziehungsgeld) on child level
    """
    if erziehungsgeld_anspruch_kind:
        out = max(
            erziehungsgeld_ohne_abzug_m - erziehungsgeld_abzug_transfer,
            0.0,
        )
    else:
        out = 0.0

    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_ohne_abzug_m(
    budget_erziehungsgeld: bool,
    erziehungsgeld_eink_relev_kind_y: float,
    erziehungsgeld_einkommensgrenze_kind_y: float,
    alter_monate: int,
    erziehungsgeld_params: dict,
) -> float:
    """Parental leave benefit (Erziehungsgeld) without means-test.

    Parameters
    ----------
    budget_erziehungsgeld
        See :See basic input variable :ref:`budget_erziehungsgeld
        <budget_erziehungsgeld>`.
    erziehungsgeld_eink_relev_kind_y
        See :func:`erziehungsgeld_eink_relev_kind_y`.
    erziehungsgeld_einkommensgrenze_kind_y
        See :func:`erziehungsgeld_einkommensgrenze_kind_y`.
    alter_monate
        See :func:`alter_monate`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    Parental leave benefit (Erziehungsgeld) without means-test
    """
    if (
        erziehungsgeld_eink_relev_kind_y > erziehungsgeld_einkommensgrenze_kind_y
        and alter_monate
        < erziehungsgeld_params["einkommensgrenze"][
            "start_age_m_teilw_anrechnung_einkommen"
        ]
    ):
        out = 0.0
    elif budget_erziehungsgeld:
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]
    else:
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]

    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_abzug_transfer(
    erziehungsgeld_eink_relev_kind_m: float,
    erziehungsgeld_einkommensgrenze_kind_m: float,
    alter_monate: int,
    erziehungsgeld_params: dict,
) -> float:
    """Determine the income reduction for parental leave benefit (Erziehungsgeld).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.209)

    Parameters
    ----------
    erziehungsgeld_eink_relev_kind_m
        See :func:`erziehungsgeld_eink_relev_kind_y`.
    erziehungsgeld_einkommensgrenze_kind_m
        See :func:`erziehungsgeld_einkommensgrenze_kind_y`.
    alter_monate
        See :func:`alter_monate`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    Income reduction for parental leave benefit (Erziehungsgeld)
    """
    if (
        erziehungsgeld_eink_relev_kind_m > erziehungsgeld_einkommensgrenze_kind_m
        and alter_monate
        >= erziehungsgeld_params["einkommensgrenze"][
            "start_age_m_teilw_anrechnung_einkommen"
        ]
    ):
        out = (
            erziehungsgeld_eink_relev_kind_m * erziehungsgeld_params["abschlag_faktor"]
        )
    else:
        out = 0.0
    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_anspruch_kind(
    kind: bool,
    alter_monate: int,
    budget_erziehungsgeld: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Determine the eligibility for parental leave benefit (Erziehungsgeld) on child
    level.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.207)

    Parameters
    ----------
    kind
        See :See basic input variable :ref:`kind <kind>`.
    alter_monate
        See :func:`alter_monate`.
    budget_erziehungsgeld
        See :See basic input variable :ref:`budget_erziehungsgeld
        <budget_erziehungsgeld>`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of (Erziehungsgeld) as a bool

    """
    if budget_erziehungsgeld:
        out = kind and alter_monate <= erziehungsgeld_params["end_age_budgetsatz"]

    else:
        out = kind and alter_monate <= erziehungsgeld_params["end_age_regelsatz"]

    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_anspruch_eltern(
    arbeitsstunden_w: float,
    hat_kinder: bool,
    erziehungsgeld_anspruch_kind_tu: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Determine the eligibility for parental leave benefit (Erziehungsgeld) on
    parental level.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.207)

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
    eligibility of parental leave benefit (Erziehungsgeld) as a bool

    """
    out = (
        erziehungsgeld_anspruch_kind_tu
        and (arbeitsstunden_w <= erziehungsgeld_params["arbeitsstunden_w_grenze"])
        and hat_kinder
    )

    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_eink_relev_kind_y(
    bruttolohn_vorj_y_tu: float,
    anz_erwachsene_tu: int,
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_params: dict,
    eink_st_abzuege_params: dict,
) -> float:
    """Income relevant for means testing for parental leave benefit (Erziehungsgeld).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.209)

    There is special rule for "Beamte, Soldaten und Richter" which is not
    implemented yet.

    Parameters
    ----------
    bruttolohn_vorj_y_tu
        See :func:`bruttolohn_vorj_y_tu`.
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
    Relevant income
    """

    if erziehungsgeld_anspruch_kind:
        out = (
            bruttolohn_vorj_y_tu
            - eink_st_abzuege_params["werbungskostenpauschale"] * anz_erwachsene_tu
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    else:
        out = 0.0
    return out


@dates_active(start="1985-01-01", end="2008-12-31")
def erziehungsgeld_einkommensgrenze_kind_y(
    erziehungsgeld_einkommensgrenze_vor_aufschl: float,
    anz_kinder_mit_kindergeld_tu: float,
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

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
    income threshold for parental leave benefit (Erziehungsgeld) on child level
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
    alter_monate: int,
    budget_erziehungsgeld: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld)
    on child level before adding the bonus for additional children

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    alleinerz_tu
        See :func:`alleinerz_tu`.
    alter_monate
        See :func:`alter_monate`.
    budget_erziehungsgeld
        See :See basic input variable :ref:`budget_erziehungsgeld
        <budget_erziehungsgeld>`.

    Returns
    -------
    Income threshold for parental leave benefit (Erziehungsgeld) before child bonus
    """
    # There are different income thresholds depending on the age of the child,
    # the fact if a person is a single parent, and if regelsatz or budgetsatz is applied

    if (
        alter_monate
        < erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        limit = "limit"
    else:
        limit = "reduced_limit"

    if alleinerz_tu:
        status_eltern = "alleinerz"
    else:
        status_eltern = "paar"

    if budget_erziehungsgeld:
        satz = "budgetsatz"
    else:
        satz = "regelsatz"

    out = erziehungsgeld_params["einkommensgrenze"][limit][status_eltern][satz]

    return out
