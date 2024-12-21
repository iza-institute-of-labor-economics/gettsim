"""Income components for income tax calculation."""

from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import policy_info


@policy_info(end_date="2008-12-31", name_in_dag="betrag_y")
def betrag_mit_kapitaleinkommen_y(
    eink_selbst_y: float,
    betrag_aus_abhängiger_beschäftigung_ohne_minijob_y: float,
    eink_vermietung_y: float,
    bruttoeinkommen_renteneinkommen_y: float,
    kapitaleinkommen_y: float,
) -> float:
    """Sum of gross incomes with capital income.

    Parameters
    ----------
    eink_selbst_y
        See :func:`eink_selbst_y`.
    betrag_aus_abhängiger_beschäftigung_ohne_minijob_y
        See :func:`betrag_aus_abhängiger_beschäftigung_ohne_minijob_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    bruttoeinkommen_renteneinkommen_y
        See :func:`bruttoeinkommen_renteneinkommen_y`.
    kapitaleinkommen_y
        See :func:`kapitaleinkommen_y`.

    Returns
    -------

    """
    out = (
        eink_selbst_y
        + betrag_aus_abhängiger_beschäftigung_ohne_minijob_y
        + eink_vermietung_y
        + bruttoeinkommen_renteneinkommen_y
        + kapitaleinkommen_y
    )
    return out


@policy_info(start_date="2009-01-01", name_in_dag="betrag_y")
def betrag_ohne_kapitaleinkommen_y(
    eink_selbst_y: float,
    betrag_aus_abhängiger_beschäftigung_ohne_minijob_y: float,
    eink_vermietung_y: float,
    bruttoeinkommen_renteneinkommen_y: float,
) -> float:
    """Sum of gross incomes without capital income.

    Since 2009 capital income is not subject to normal taxation.
    Parameters
    ----------
    eink_selbst_y
        See :func:`eink_selbst_y`.
    betrag_aus_abhängiger_beschäftigung_ohne_minijob_y
        See :func:`betrag_aus_abhängiger_beschäftigung_ohne_minijob_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    bruttoeinkommen_renteneinkommen_y
        See :func:`bruttoeinkommen_renteneinkommen_y`.

    Returns
    -------

    """
    out = (
        eink_selbst_y
        + betrag_aus_abhängiger_beschäftigung_ohne_minijob_y
        + eink_vermietung_y
        + bruttoeinkommen_renteneinkommen_y
    )
    return out


def kapitaleinkommen_y(
    kapitaleink_brutto_y: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Capital income minus Sparerpauschbetrag.

    Parameters
    ----------
    kapitaleink_brutto_y
        See :func:`kapitaleink_brutto_y`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        kapitaleink_brutto_y
        - eink_st_abzuege_params["sparerpauschbetrag"]
        - eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    )

    return max(out, 0.0)


def rente_ertragsanteil(jahr_renteneintr: int, eink_st_params: dict) -> float:
    """Share of pensions subject to income taxation.

    Parameters
    ----------
    jahr_renteneintr
            See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.
    Returns
    -------

    """
    out = piecewise_polynomial(
        x=jahr_renteneintr,
        thresholds=eink_st_params["rente_ertragsanteil"]["thresholds"],
        rates=eink_st_params["rente_ertragsanteil"]["rates"],
        intercepts_at_lower_thresholds=eink_st_params["rente_ertragsanteil"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out


def betrag_aus_abhängiger_beschäftigung_ohne_minijob_y(
    betrag_aus_abhängiger_beschäftigung_y: float,
    einkommensgrenzen__geringfügig_beschäftigt: bool,
) -> float:
    """Taxable income from dependent employment. In particular, taxable income is set to
    0 for marginally employed persons.

    Parameters
    ----------
    betrag_aus_abhängiger_beschäftigung_y
        See basic input variable :ref:`betrag_aus_abhängiger_beschäftigung_y
        <betrag_aus_abhängiger_beschäftigung_y>`.
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.

    Returns
    -------

    """
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_aus_abhängiger_beschäftigung_y

    return out


def betrag_aus_abhängiger_beschäftigung_y(
    bruttolohn_y: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Aggregate monthly gross wage to yearly income and deduct
    'Werbungskostenpauschale'.

    The wage is reducted by a lump sum payment for 'Werbungskosten'

    Parameters
    ----------
    bruttolohn_y
        See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    abzug = eink_st_abzuege_params["werbungskostenpauschale"]

    out = bruttolohn_y - abzug

    return max(out, 0.0)


def bruttoeinkommen_renteneinkommen_m(
    sum_ges_rente_priv_rente_m: float, rente_ertragsanteil: float
) -> float:
    """Calculate monthly pension payment subject to taxation.

    Parameters
    ----------
    sum_ges_rente_priv_rente_m
        See basic input variable :ref:`sum_ges_rente_priv_rente_m
        <sum_ges_rente_priv_rente_m>`.
    rente_ertragsanteil
        See :func:`rente_ertragsanteil`.

    Returns
    -------

    """
    return rente_ertragsanteil * sum_ges_rente_priv_rente_m
