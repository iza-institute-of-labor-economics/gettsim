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
    alter_monate: float,
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
    alter_monate
        See :func:`alter_monate`.


    Returns
    -------
    monthly claim of parental leave benefit (erziehungsgeld) on child level

    """
    # if the income is higher than the threshold within the first 6 month there
    # is no erziehungsgeld claim at all

    abzug = (erziehungsgeld_eink_relev_kind / 12) * erziehungsgeld_params[
        "reduzierung_erziehungsgeld"
    ]

    if (
        erziehungsgeld_anspruch_kind
        and alter_monate < 7
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkgrenze_kind
        and budget_erz_geld
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]

    elif (
        erziehungsgeld_anspruch_kind
        and alter_monate < 7
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkgrenze_kind
        and (not budget_erz_geld)
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]
    # if the income is higher than the threshold and the child is older than
    # 7 month the Erziehungsgeld is reduced
    elif (
        erziehungsgeld_anspruch_kind
        and (7 <= alter_monate <= 12)
        and erziehungsgeld_eink_relev_kind > erziehungsgeld_einkgrenze_kind
        and budget_erz_geld
    ):
        out = max(
            erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"] - abzug, 0.0
        )
    elif (
        erziehungsgeld_anspruch_kind
        and (7 <= alter_monate <= 12)
        and erziehungsgeld_eink_relev_kind > erziehungsgeld_einkgrenze_kind
        and (not budget_erz_geld)
    ):
        out = max(
            erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"] - abzug, 0.0
        )
    elif (
        erziehungsgeld_anspruch_kind
        and (7 <= alter_monate <= 12)
        and erziehungsgeld_eink_relev_kind < erziehungsgeld_einkgrenze_kind
        and (not budget_erz_geld)
    ):
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]
    else:
        out = 0.0

    return out


def erziehungsgeld_anspruch_kind(
    alter_monate: float,
    budget_erz_geld: bool,
) -> bool:
    """Determine the eligibility for parental leave benefit (erziehungsgeld) on child
    level.

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.207)

    Parameters
    ----------
    alter_monate
        See :func:`alter_monate`.
    budget_erz_geld
        See :See basic input variable :ref:`budget_erz_geld <budget_erz_geld>`.


    Returns
    -------
    eligibility of (erziehungsgeld) as a bool

    """
    if budget_erz_geld:
        out = alter_monate <= 12

    else:
        out = alter_monate <= 24

    return out


def erziehungsgeld_anspruch_eltern(
    arbeitsstunden_w: float,
    hat_kinder: bool,
    erziehungsgeld_anspruch_kind_tu: bool,
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

    Returns
    -------
    eligibility of parental leave benefit (erziehungsgeld) as a bool

    """
    out = erziehungsgeld_anspruch_kind_tu and (arbeitsstunden_w <= 30) and hat_kinder

    return out


def erziehungsgeld_eink_relev_kind(
    bruttolohn_vorj_m_tu: float,
    erziehungsgeld_params: dict,
    alleinerz_tu: bool,
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
    alleinerz_tu
        See :func:`alleinerz_tu`.
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

    if erziehungsgeld_anspruch_kind and alleinerz_tu:
        out = (
            bruttolohn_vorj_m_tu * 12
            - eink_st_abzuege_params["werbungskostenpauschale"]
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    elif erziehungsgeld_anspruch_kind and (not alleinerz_tu):
        out = (
            bruttolohn_vorj_m_tu * 12
            - eink_st_abzuege_params["werbungskostenpauschale"]
            * 2  # is that already hard coded?
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    else:
        out = 0.0
    return out


def erziehungsgeld_einkgrenze_kind(  # noqa: PLR0913
    erziehungsgeld_params: dict,
    alleinerz_tu: bool,
    alter_monate: float,
    anz_kinder_mit_kindergeld_tu: float,
    budget_erz_geld: bool,
    erziehungsgeld_anspruch_kind: bool,
) -> float:
    """Calculating the income threshold for parental leave benefit (erziehungsgeld)
    on child level

    legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    alleinerz_tu
        See :func:`alleinerz_tu`.
    alter_monate
        See :func:`alter_monate`.
    anz_kinder_mit_kindergeld_tu
        See :func:`anz_kinder_mit_kindergeld_tu`.
    budget_erz_geld
        See :See basic input variable :ref:`budget_erz_geld <budget_erz_geld>`.
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.

    Returns
    -------
    income threshold for parental leave benefit (erziehungsgeld)
    """
    # There are different income threshold depending on the age of the child,
    # the fact if a person is a single parent, and if regelsatz or budgetsatz is applied

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
    key = (alter_monate < 7, alleinerz_tu, budget_erz_geld)
    out = einkommensgrenze[key]

    # For every additional child the income threshold is increased by a fixed amount
    out += (anz_kinder_mit_kindergeld_tu - 1) * erziehungsgeld_params[
        "aufschlag_einkommen"
    ]
    if not erziehungsgeld_anspruch_kind:
        out = 0.0
    return out
