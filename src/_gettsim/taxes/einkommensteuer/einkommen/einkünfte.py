"""Income components for income tax calculation."""

from _gettsim.function_types import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial


@policy_function(end_date="2008-12-31", leaf_name="gesamteinkünfte_y")
def gesamteinkünfte_mit_kapitaleinkommen_y_sn(
    einkommen__aus_selbstständigkeit_y: float,
    einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y: float,
    eink_vermietung_y: float,
    renteneinkünfte_y: float,
    zu_versteuerndes_kapitaleinkommen_y_sn: float,
) -> float:
    """Sum of gross incomes with capital income.

    Parameters
    ----------
    einkommen__aus_selbstständigkeit_y
        See :func:`einkommen__aus_selbstständigkeit_y`.
    einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y
        See :func:`einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    renteneinkünfte_y
        See :func:`renteneinkünfte_y`.
    zu_versteuerndes_kapitaleinkommen_y_sn
        See :func:`zu_versteuerndes_kapitaleinkommen_y_sn`.

    Returns
    -------

    """
    out = (
        einkommen__aus_selbstständigkeit_y
        + einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y
        + eink_vermietung_y
        + renteneinkünfte_y
        + zu_versteuerndes_kapitaleinkommen_y_sn
    )
    return out


@policy_function(start_date="2009-01-01", leaf_name="gesamteinkünfte_y")
def gesamteinkünfte_ohne_kapitaleinkommen_y_sn(
    einkommen__aus_selbstständigkeit_y: float,
    einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y: float,
    eink_vermietung_y: float,
    renteneinkünfte_y: float,
) -> float:
    """Sum of gross incomes without capital income.

    Since 2009 capital income is not subject to normal taxation.
    Parameters
    ----------
    einkommen__aus_selbstständigkeit_y
        See :func:`einkommen__aus_selbstständigkeit_y`.
    einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y
        See :func:`einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    renteneinkünfte_y
        See :func:`renteneinkünfte_y`.

    Returns
    -------

    """
    out = (
        einkommen__aus_selbstständigkeit_y
        + einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y
        + eink_vermietung_y
        + renteneinkünfte_y
    )
    return out


@policy_function()
def zu_versteuerndes_kapitaleinkommen_y(
    kapitaleink_brutto_y: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate taxable capital income on Steuernummer level.

    Parameters
    ----------
    kapitaleink_brutto_y
        See :func:`kapitaleink_brutto_y`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = kapitaleink_brutto_y - (
        eink_st_abzuege_params["sparerpauschbetrag"]
        + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    )

    return max(out, 0.0)


@policy_function()
def rente_ertragsanteil(
    sozialversicherung__rente__jahr_renteneintritt: int, eink_st_params: dict
) -> float:
    """Share of pensions subject to income taxation.

    Parameters
    ----------
    sozialversicherung__rente__jahr_renteneintritt
            See basic input variable :ref:`sozialversicherung__rente__jahr_renteneintritt <sozialversicherung__rente__jahr_renteneintritt>`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.
    Returns
    -------

    """
    out = piecewise_polynomial(
        x=sozialversicherung__rente__jahr_renteneintritt,
        thresholds=eink_st_params["rente_ertragsanteil"]["thresholds"],
        rates=eink_st_params["rente_ertragsanteil"]["rates"],
        intercepts_at_lower_thresholds=eink_st_params["rente_ertragsanteil"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out


@policy_function()
def einkünfte_aus_abhängiger_beschäftigung_ohne_minijob_y(
    einkünfte_aus_abhängiger_beschäftigung_y: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
) -> float:
    """Taxable income from dependent employment. In particular, taxable income is set to
    0 for marginally employed persons.

    Parameters
    ----------
    einkünfte_aus_abhängiger_beschäftigung_y
        See :func:`einkünfte_aus_abhängiger_beschäftigung_y`.
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.

    Returns
    -------

    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = einkünfte_aus_abhängiger_beschäftigung_y

    return out


@policy_function()
def einkünfte_aus_abhängiger_beschäftigung_y(
    einkommen__bruttolohn_y: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Aggregate monthly gross wage to yearly income and deduct
    'Werbungskostenpauschale'.

    The wage is reducted by a lump sum payment for 'Werbungskosten'

    Parameters
    ----------
    einkommen__bruttolohn_y
        See basic input variable :ref:`einkommen__bruttolohn_y <einkommen__bruttolohn_y>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    abzug = eink_st_abzuege_params["werbungskostenpauschale"]

    out = einkommen__bruttolohn_y - abzug

    return max(out, 0.0)


@policy_function()
def renteneinkünfte_m(
    sozialversicherung__rente__summe_private_gesetzliche_rente_m: float,
    rente_ertragsanteil: float,
) -> float:
    """Calculate monthly pension payment subject to taxation.

    Parameters
    ----------
    sozialversicherung__rente__summe_private_gesetzliche_rente_m
        See :func:`sozialversicherung__rente__summe_private_gesetzliche_rente_m`.
    rente_ertragsanteil
        See :func:`rente_ertragsanteil`.

    Returns
    -------

    """
    return (
        rente_ertragsanteil
        * sozialversicherung__rente__summe_private_gesetzliche_rente_m
    )
