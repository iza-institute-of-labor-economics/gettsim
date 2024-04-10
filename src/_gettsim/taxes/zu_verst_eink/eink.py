from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import policy_info


def eink_selbst_y(eink_selbst_m: float) -> float:
    """Aggregate gross income from self-employment to full year income.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.

    Returns
    -------

    """
    return 12 * eink_selbst_m


def eink_abhängig_beschäftigt_y(
    bruttolohn_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Aggregate monthly gross wage to yearly income and deduct
    'Werbungskostenpauschale'.

    The wage is reducted by a lump sum payment for 'Werbungskosten'

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    abzug = eink_st_abzuege_params["werbungskostenpauschale"]

    out = 12 * bruttolohn_m - abzug

    return out


def _zu_verst_eink_abhängig_beschäftigt_y(
    eink_abhängig_beschäftigt_y: float,
    geringfügig_beschäftigt: bool,
) -> float:
    """Calculate taxable income from dependent employment. In particular, taxable
    income is set to 0 for marginally employed persons.

    Parameters
    ----------
    eink_abhängig_beschäftigt_y
        See basic input variable :ref:`eink_abhängig_beschäftigt_y
        <eink_abhängig_beschäftigt_y>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    Returns
    -------

    """
    if geringfügig_beschäftigt:
        out = 0.0
    else:
        out = eink_abhängig_beschäftigt_y

    return out


def kapitaleink_brutto_y(kapitaleink_brutto_m: float) -> float:
    """Aggregate monthly gross capital income to yearly income.

    Parameters
    ----------
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.

    Returns
    -------

    """
    return 12 * kapitaleink_brutto_m


def eink_vermietung_y(eink_vermietung_m: float) -> float:
    """Aggregate monthly gross rental income to yearly income.

    Parameters
    ----------
    eink_vermietung_m
        See basic input variable :ref:`eink_vermietung_m <eink_vermietung_m>`.

    Returns
    -------

    """
    return 12 * eink_vermietung_m


def eink_rente_zu_verst_m(
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


def eink_rente_zu_verst_y(
    eink_rente_zu_verst_m: float,
) -> float:
    """Aggregate monthly gross pension income subject to taxation to yearly income.

    Parameters
    ----------
    eink_rente_zu_verst_m
        See :func:`eink_rente_zu_verst_m`.

    Returns
    -------

    """
    return eink_rente_zu_verst_m * 12


@policy_info(start_date="2009-01-01", name_in_dag="sum_eink_y")
def sum_eink_ohne_kapital_eink_y(
    eink_selbst_y: float,
    _zu_verst_eink_abhängig_beschäftigt_y: float,
    eink_vermietung_y: float,
    eink_rente_zu_verst_y: float,
) -> float:
    """Sum of gross incomes without capital income.

    Since 2009 capital income is not subject to normal taxation.
    Parameters
    ----------
    eink_selbst_y
        See :func:`eink_selbst_y`.
    _zu_verst_eink_abhängig_beschäftigt_y
        See :func:`_zu_verst_eink_abhängig_beschäftigt_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    eink_rente_zu_verst_y
        See :func:`eink_rente_zu_verst_y`.

    Returns
    -------

    """
    out = (
        eink_selbst_y
        + _zu_verst_eink_abhängig_beschäftigt_y
        + eink_vermietung_y
        + eink_rente_zu_verst_y
    )
    return out


def kapitaleink_y(
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


@policy_info(end_date="2008-12-31", name_in_dag="sum_eink_y")
def sum_eink_mit_kapital_eink_y(
    eink_selbst_y: float,
    _zu_verst_eink_abhängig_beschäftigt_y: float,
    eink_vermietung_y: float,
    eink_rente_zu_verst_y: float,
    kapitaleink_y: float,
) -> float:
    """Sum of gross incomes with capital income.

    Parameters
    ----------
    eink_selbst_y
        See :func:`eink_selbst_y`.
    _zu_verst_eink_abhängig_beschäftigt_y
        See :func:`_zu_verst_eink_abhängig_beschäftigt_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    eink_rente_zu_verst_y
        See :func:`eink_rente_zu_verst_y`.
    kapitaleink_y
        See :func:`kapitaleink_y`.

    Returns
    -------

    """
    out = (
        eink_selbst_y
        + _zu_verst_eink_abhängig_beschäftigt_y
        + eink_vermietung_y
        + eink_rente_zu_verst_y
        + kapitaleink_y
    )
    return out


def rente_ertragsanteil(jahr_renteneintr: int, eink_st_params: dict) -> float:
    """Calculate the share of pensions subject to income taxation.

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
