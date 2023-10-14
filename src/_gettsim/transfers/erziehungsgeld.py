#!/usr/bin/python3
from _gettsim.shared import add_rounding_spec, dates_active

aggregation_erziehungsgeld = {
    "bruttolohn_vorj_m_tu": {
        "source_col": "bruttolohn_vorj_m",
        "aggr": "sum",
    },
    "erziehungsgeld_kind_m_tu": {
        "source_col": "erziehungsgeld_kind_m",
        "aggr": "sum",
    },
    "erziehungsgeld_anspruch_kind_tu": {
        "source_col": "erziehungsgeld_anspruch_kind",
        "aggr": "any",
    },
}


def erziehungsgeld_m(
    erziehungsgeld_kind_m_tu: int,
    erziehungsgeld_anspruch_eltern: bool,
    inanspruchn_erzgeld: bool,
) -> bool:
    """Calculation of total parental leave benefits (erziehungsgeld).

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6

    Parameters
    ----------
    erziehungsgeld_kind_m_tu
        See :func:`erziehungsgeld_kind_m_tu`.
    erziehungsgeld_anspruch_eltern
        See :func:`erziehungsgeld_anspruch_eltern`.
    inanspruchn_erzgeld
        See :See basic input variable :ref:`inanspruchn_erzgeld <inanspruchn_erzgeld>`.

    Returns
    -------
    Sum of parental leave benefits (erziehungsgeld) on TU level

    """
    if erziehungsgeld_anspruch_eltern and inanspruchn_erzgeld:
        out = erziehungsgeld_kind_m_tu
    else:
        out = 0.0

    return out


@add_rounding_spec(params_key="erziehungsgeld")
@dates_active(end="2006-12-31")
def erziehungsgeld_kind_m(  # noqa: PLR0913
    erziehungsgeld_params: dict,
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_eink_relev_kind: float,
    erziehungsgeld_einkgrenze_kind: float,
    budget_erz_geld: bool,
    kind_bis_7m: bool,
    kind_ab_7m_bis_12m: bool,
) -> float:
    """Calculate parental leave benefit (erziehungsgeld) on child level.

    For the calculation, the relevant wage, the age of the youngest child,
    the income threshold and the eligibility for erziehungsgeld is needed.

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6

    Parameters
    ----------
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.
    erziehungsgeld_eink_relev_kind
        See :func:`erziehungsgeld_eink_relev_kind`.
    erziehungsgeld_einkgrenze_kind
        See :func:`erziehungsgeld_einkgrenze_kind`.
    budget_erz_geld
        See :See basic input variable :ref:`budget_erz_geld <budget_erz_geld>`.
    kind_bis_7m
        See :func:`kind_bis_7m`.
    kind_ab_7m_bis_12m
        See :func:`kind_ab_7m_bis_12m`.


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
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkgrenze_kind
        and budget_erz_geld
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]

    elif (
        erziehungsgeld_anspruch_kind
        and kind_bis_7m
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkgrenze_kind
        and (not budget_erz_geld)
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]
    # if the income is higher than the threshold and the child is older than
    # 7 month the parental leave benefit is reduced
    elif (
        erziehungsgeld_anspruch_kind
        and kind_ab_7m_bis_12m
        and erziehungsgeld_eink_relev_kind > erziehungsgeld_einkgrenze_kind
        and budget_erz_geld
    ):
        out = max(
            erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"] - abzug, 0.0
        )
    elif (
        erziehungsgeld_anspruch_kind
        and kind_ab_7m_bis_12m
        and erziehungsgeld_eink_relev_kind > erziehungsgeld_einkgrenze_kind
        and (not budget_erz_geld)
    ):
        out = max(
            erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"] - abzug, 0.0
        )
    # If the child is older than 7 months and the income is below the income limit,
    # the full rule or budget rate is paid out
    elif (
        erziehungsgeld_anspruch_kind
        and kind_ab_7m_bis_12m
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkgrenze_kind
        and (not budget_erz_geld)
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]
    elif (
        erziehungsgeld_anspruch_kind
        and kind_ab_7m_bis_12m
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkgrenze_kind
        and budget_erz_geld
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]
    # if the income is higher than the threshold within the first 6 month there
    # is no erziehungsgeld claim at all
    else:
        out = 0.0

    return out


def erziehungsgeld_anspruch_kind(
    kind_bis_12m: bool,
    kind_bis_24m: bool,
    budget_erz_geld: bool,
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
    budget_erz_geld
        See :See basic input variable :ref:`budget_erz_geld <budget_erz_geld>`.


    Returns
    -------
    eligibility of (erziehungsgeld) as a bool

    """
    if budget_erz_geld:
        out = kind_bis_12m

    else:
        out = kind_bis_24m

    return out


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


def erziehungsgeld_eink_relev_kind(
    bruttolohn_vorj_m_tu: float,
    erziehungsgeld_params: dict,
    anz_erwachsene_tu: float,
    eink_st_abzuege_params: dict,
    erziehungsgeld_anspruch_kind: bool,
) -> float:
    """Calculate the relevant wage for parental leave benefit (erziehungsgeld) on child
    level

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.209)

    Parameters
    ----------
    bruttolohn_vorj_m_tu
        See :func:`bruttolohn_vorj_m_tu`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.

    Returns
    -------
    relevant wage for calculation parental leave benefit (erziehungsgeld)


    Todo: There is special rule for "Beamte, Soldaten und Richter" which is not
          implemented yet
    """

    if erziehungsgeld_anspruch_kind:
        out = (
            bruttolohn_vorj_m_tu * 12
            - eink_st_abzuege_params["werbungskostenpauschale"] * anz_erwachsene_tu
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    else:
        out = 0.0
    return out


def erziehungsgeld_einkgrenze_kind(
    erziehungsgeld_einkgrenze_kind_vor_aufschl: float,
    anz_kinder_mit_kindergeld_tu: float,
    erziehungsgeld_params: dict,
    erziehungsgeld_anspruch_kind: bool,
) -> float:
    """Calculate the income threshold for parental leave benefit (erziehungsgeld)
    on child level

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    erziehungsgeld_einkgrenze_kind_vor_aufschl
        See :func:`erziehungsgeld_einkgrenze_kind_vor_aufschl`.
    anz_kinder_mit_kindergeld_tu
        See :func:`anz_kinder_mit_kindergeld_tu`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.

    Returns
    -------
    income threshold for parental leave benefit (erziehungsgeld) on child level
    """
    out = (
        erziehungsgeld_einkgrenze_kind_vor_aufschl
        + (anz_kinder_mit_kindergeld_tu - 1)
        * erziehungsgeld_params["aufschlag_einkommen"]
    )
    if not erziehungsgeld_anspruch_kind:
        out = 0.0
    return out


def erziehungsgeld_einkgrenze_kind_vor_aufschl(
    erziehungsgeld_params: dict,
    alleinerz_tu: bool,
    kind_bis_7m: bool,
    budget_erz_geld: bool,
) -> float:
    """Calculating the income threshold for parental leave benefit (erziehungsgeld)
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
    budget_erz_geld
        See :See basic input variable :ref:`budget_erz_geld <budget_erz_geld>`.

    Returns
    -------
    income threshold for parental leave benefit (erziehungsgeld) before child bonus
    """
    # There are different income threshold depending on the age of the child,
    # the fact if a person is a single parent, and if regelsatz or budgetsatz is applied

    if kind_bis_7m:
        alter_kind = "kind_bis_7m"
    else:
        alter_kind = "kind_ab_7m"

    if alleinerz_tu:
        status_eltern = "alleinerz"
    else:
        status_eltern = "paar"

    if budget_erz_geld:
        satz = "budgetsatz"
    else:
        satz = "regelsatz"

    out = erziehungsgeld_params["einkommensgrenze"][alter_kind][status_eltern][satz]

    return out
