#!/usr/bin/python3
from _gettsim.shared import add_rounding_spec, dates_active

aggregation_erziehungsgeld = {
    "bruttolohn_vorj_m_tu": {
        "source_col": "bruttolohn_vorj_m",
        "aggr": "cumsum",
    },
}


@add_rounding_spec(params_key="erziehungsgeld")
@dates_active(end="2006-12-31")
def erziehungsgeld_m(  # noqa: PLR0913
    erziehungsgeld_params: dict,
    erziehungsgeld_anspruch: bool,
    erziehungsgeld_einkommen_relev: float,
    erziehungsgeld_einkommensgrenze: float,
    anz_kinder_ab_6_bis_12m_hh: int,
    anz_kinder_ab_6_bis_24m_hh: int,
    anz_kinder_bis_6m_hh: int,
    budget_erz_geld: bool,
) -> float:
    """Calculate parental leave benefit (erziehungsgeld).

    For the calculation, the relevant wage, the age of the youngest child,
    the income threshold and the eligibility for erziehungsgeld is needed.

    Parameters
    ----------
    erziehungsgeld_anspruch
        See :func:`erziehungsgeld_anspruch`.
    erziehungsgeld_einkommen_relev
        See :func:`erziehungsgeld_einkommen_relev`.
    erziehungsgeld_einkommensgrenze
        See :func:`erziehungsgeld_einkommensgrenze`.
    alter_monate_jüngstes_mitglied_hh
        See :func:`alter_monate_jüngstes_mitglied_hh`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    monthly claim of erziehungsgeld

    Todo: Implement that people can decide whether they want the "regelsatz"
    for up to 24 month or a higher "budgetiertes Erziehungsgeld" for just 12
    month
    """
    # if the income is higher than the threshold within the first 6 month there
    # is no erziehungsgeld claim at all

    abzug = (erziehungsgeld_einkommen_relev / 12) * erziehungsgeld_params[
        "reduzierung_erziehungsgeld"
    ]

    out = 0.0

    if (
        erziehungsgeld_anspruch
        and anz_kinder_bis_6m_hh >= 1
        and erziehungsgeld_einkommen_relev < erziehungsgeld_einkommensgrenze
        and budget_erz_geld
    ):
        out += (
            erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]
            * anz_kinder_bis_6m_hh
        )

    elif (
        erziehungsgeld_anspruch
        and anz_kinder_bis_6m_hh >= 1
        and erziehungsgeld_einkommen_relev < erziehungsgeld_einkommensgrenze
        and (not budget_erz_geld)
    ):
        out += (
            erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]
            * anz_kinder_bis_6m_hh
        )
    # if the income is higher than the threshold and the child is older than
    # 7 month the Erziehungsgeld is reduced
    elif (
        erziehungsgeld_anspruch
        and anz_kinder_ab_6_bis_12m_hh >= 1
        and erziehungsgeld_einkommen_relev > erziehungsgeld_einkommensgrenze
        and budget_erz_geld
    ):
        out += (
            max(erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"] - abzug, 0.0)
            * anz_kinder_ab_6_bis_12m_hh
        )
    elif (
        erziehungsgeld_anspruch
        and anz_kinder_ab_6_bis_24m_hh >= 1
        and erziehungsgeld_einkommen_relev > erziehungsgeld_einkommensgrenze
        and (not budget_erz_geld)
    ):
        out += (
            max(erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"] - abzug, 0.0)
            * anz_kinder_ab_6_bis_24m_hh
        )
    elif (
        erziehungsgeld_anspruch
        and anz_kinder_ab_6_bis_24m_hh >= 1
        and erziehungsgeld_einkommen_relev < erziehungsgeld_einkommensgrenze
        and (not budget_erz_geld)
    ):
        out += (
            erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]
            * anz_kinder_ab_6_bis_24m_hh
        )
    else:
        out += 0.0

    return out


def erziehungsgeld_anspruch(
    arbeitsstunden_w: float,
    hat_kinder: bool,
    anz_kinder_bis_12m_hh: int,
    anz_kinder_bis_24m_hh: int,
    budget_erz_geld: bool,
) -> bool:
    """Determine the eligibility for parental leave benefit (erziehungsgeld).

    Parameters
    ----------
    arbeitsstunden_w
        See :See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    hat_kinder
        See :See basic input variable :ref:`hat_kinder <hat_kinder>`.
    erziehungsgeld_einkommen_relev
        See :func:`erziehungsgeld_einkommen_relev`.
    alter_monate_jüngstes_mitglied_hh
        See :func:`alter_monate_jüngstes_mitglied_hh`.

    Returns
    -------
    eligibility of (erziehungsgeld) as a bool
    TOdo: Erziehungsgeld is paid for every child in hh
    TOdo: If both parents are eligibil they can decide who gets the money
          if not specified the mother gets the money

    """
    if budget_erz_geld:
        out = hat_kinder and (anz_kinder_bis_12m_hh >= 1) and (arbeitsstunden_w <= 30)

    else:
        out = hat_kinder and (anz_kinder_bis_24m_hh >= 1) and (arbeitsstunden_w <= 30)

    return out


def erziehungsgeld_einkommen_relev(  # noqa: PLR0913
    bruttolohn_vorj_m: float,
    bruttolohn_vorj_m_tu: float,
    erziehungsgeld_params: dict,
    alleinerz: bool,
    eink_st_abzuege_params: dict,
    erziehungsgeld_anspruch: bool,
) -> float:
    """Calculate the relevant wage for (erziehungsgeld)

    Parameters
    ----------
    bruttolohn_vorj_m
        See :See basic input variable :ref:`bruttolohn_vorj_m <bruttolohn_vorj_m>`.
    bruttolohn_vorj_m_tu
        See :func:`bruttolohn_vorj_m_tu`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    alleinerz
        See :See basic input variable :ref:`alleinerz <alleinerz>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------
    relevant wage for (erziehungsgeld)


    Todo: There is special rule for "Beamte, Soldaten und Richter" which is not
          implemented yet
    """

    if erziehungsgeld_anspruch and alleinerz:
        out = (
            bruttolohn_vorj_m * 12 - eink_st_abzuege_params["werbungskostenpauschale"]
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    elif erziehungsgeld_anspruch and (not alleinerz):
        out = (
            bruttolohn_vorj_m_tu * 12
            - eink_st_abzuege_params["werbungskostenpauschale"] * 2
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    else:
        out = 0.0
    return out


def erziehungsgeld_einkommensgrenze(  # noqa: PLR0913
    erziehungsgeld_params: dict,
    alleinerz: bool,
    alter_monate_jüngstes_mitglied_hh: float,
    anz_kinder_mit_kindergeld_tu: float,
    budget_erz_geld: bool,
    erziehungsgeld_anspruch: bool,
) -> float:
    """Calculating the income threshold for (erziehungsgeld)

    Parameters
    ----------
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    alleinerz
        See :See basic input variable :ref:`alleinerz <alleinerz>`.
    alter_monate_jüngstes_mitglied_hh
        See :func:`alter_monate_jüngstes_mitglied_hh`.
    anz_kinder_mit_kindergeld_tu
        See :func:`anz_kinder_mit_kindergeld_tu`.

    Returns
    -------
    income threshold for (erziehungsgeld)
    """
    # There are different income threshold depending on the age of the child,
    # the fact if a person is a single parent, and if regelsatz or budgetsatz is applied
    # to-do different income thresholds for different childs

    einkommensgrenze = {
        (True, True, False): erziehungsgeld_params["einkommensgrenze_bis_6m"][
            "alleinerz_regelsatz"
        ],
        (True, False, False): erziehungsgeld_params["einkommensgrenze_bis_6m"][
            "paar_regelsatz"
        ],
        (True, True, True): erziehungsgeld_params["einkommensgrenze_bis_6m"][
            "alleinerz_budgetsatz"
        ],
        (True, False, True): erziehungsgeld_params["einkommensgrenze_bis_6m"][
            "paar_budgetsatz"
        ],
        (False, True, False): erziehungsgeld_params["einkommensgrenze_ab_7m"][
            "alleinerz"
        ],
        (False, False, False): erziehungsgeld_params["einkommensgrenze_ab_7m"]["paar"],
        (False, True, True): erziehungsgeld_params["einkommensgrenze_ab_7m"][
            "alleinerz"
        ],
        (False, False, True): erziehungsgeld_params["einkommensgrenze_ab_7m"]["paar"],
    }
    key = (alter_monate_jüngstes_mitglied_hh < 7, alleinerz, budget_erz_geld)
    out = einkommensgrenze[key]

    # For every additional child the income threshold is increased by a fixed amount
    out += (anz_kinder_mit_kindergeld_tu - 1) * erziehungsgeld_params[
        "aufschlag_einkommen"
    ]
    if not erziehungsgeld_anspruch:
        out = 0.0
    return out
