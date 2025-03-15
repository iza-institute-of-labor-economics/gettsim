"""Einkommen.

Einkommen are Einkünfte minus Sonderausgaben, Vorsorgeaufwendungen, außergewöhnliche
Belastungen and sonstige Abzüge."""

from _gettsim.function_types import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial


@policy_function()
def gesamteinkommen_y(
    gesamteinkommen_ohne_abzüge_y_sn: float,
    einkommensteuer__abzüge__betrag_y_sn: float,
) -> float:
    """Calculate taxable income without child allowance on Steuernummer level.

    Parameters
    ----------
    gesamteinkommen_ohne_abzüge_y_sn
        See :func:`gesamteinkommen_ohne_abzüge_y_sn`.
    einkommensteuer__abzüge__betrag_y_sn
        See :func:`einkommensteuer__abzüge__betrag_y_sn`.


    Returns
    -------

    """
    out = gesamteinkommen_ohne_abzüge_y_sn - einkommensteuer__abzüge__betrag_y_sn

    return max(out, 0.0)


@policy_function(end_date="2008-12-31", leaf_name="gesamteinkommen_ohne_abzüge_y")
def gesamteinkommen_ohne_abzüge_mit_kapitaleinkünften_y_sn(
    einkommen__aus_selbstständigkeit_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_y: float,
    einkommen__aus_vermietung_und_verpachtung_y: float,
    renteneinkommen_y: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y: float,
) -> float:
    """Sum of gross incomes with capital income.

    Parameters
    ----------
    einkommen__aus_selbstständigkeit_y
        See :func:`einkommen__aus_selbstständigkeit_y`.
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_y
        See :func:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_y`.
    einkommen__aus_vermietung_und_verpachtung_y
        See :func:`einkommen__aus_vermietung_und_verpachtung_y`.
    renteneinkommen_y
        See :func:`renteneinkommen_y`.
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y
        See :func:`einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y`.

    Returns
    -------

    """
    out = (
        einkommen__aus_selbstständigkeit_y
        + einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_y
        + einkommen__aus_vermietung_und_verpachtung_y
        + renteneinkommen_y
        + einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y
    )
    return out


@policy_function(start_date="2009-01-01", leaf_name="gesamteinkommen_ohne_abzüge_y")
def gesamteinkommen_ohne_abzüge_ohne_kapitaleinkünfte_y_sn(
    einkommen__aus_selbstständigkeit_y: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_y: float,
    einkommen__aus_vermietung_und_verpachtung_y: float,
    renteneinkommen_y: float,
) -> float:
    """Sum of gross incomes without capital income.

    Since 2009 capital income is not subject to normal taxation.
    Parameters
    ----------
    einkommen__aus_selbstständigkeit_y
        See :func:`einkommen__aus_selbstständigkeit_y`.
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_y
        See :func:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_y`.
    einkommen__aus_vermietung_und_verpachtung_y
        See :func:`einkommen__aus_vermietung_und_verpachtung_y`.
    renteneinkommen_y
        See :func:`renteneinkommen_y`.

    Returns
    -------

    """
    out = (
        einkommen__aus_selbstständigkeit_y
        + einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_y
        + einkommen__aus_vermietung_und_verpachtung_y
        + renteneinkommen_y
    )
    return out


@policy_function()
def renteneinkommen_m(
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
