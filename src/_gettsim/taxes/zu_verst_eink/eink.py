from _gettsim.piecewise_functions import piecewise_polynomial


def eink_selbst(eink_selbst_m: float) -> float:
    """Aggregate gross income from self-employment to full year income.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.

    Returns
    -------

    """
    return 12 * eink_selbst_m


def eink_abhängig_beschäftigt(
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


def _zu_verst_eink_abhängig_beschäftigt(
    eink_abhängig_beschäftigt: float,
    geringfügig_beschäftigt: bool,
) -> float:
    """Calculate taxable income from dependent employment. In particular, taxable
    income is set to 0 for marginally employed persons.

    Parameters
    ----------
    eink_abhängig_beschäftigt
        See basic input variable :ref:`eink_abhängig_beschäftigt
        <eink_abhängig_beschäftigt>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    Returns
    -------

    """
    if geringfügig_beschäftigt:
        out = 0.0
    else:
        out = eink_abhängig_beschäftigt

    return out


def kapitaleink_brutto(kapitaleink_brutto_m: float) -> float:
    """Aggregate monthly gross capital income to yearly income.

    Parameters
    ----------
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.

    Returns
    -------

    """
    return 12 * kapitaleink_brutto_m


def eink_vermietung(eink_vermietung_m: float) -> float:
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


def eink_rente_zu_verst(
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


def sum_eink_ohne_kapital(
    eink_selbst: float,
    _zu_verst_eink_abhängig_beschäftigt: float,
    eink_vermietung: float,
    eink_rente_zu_verst: float,
) -> float:
    """Sum of gross incomes without capital income.

    Since 2009 capital income is not subject to normal taxation.
    Parameters
    ----------
    eink_selbst
        See :func:`eink_selbst`.
    _zu_verst_eink_abhängig_beschäftigt
        See :func:`_zu_verst_eink_abhängig_beschäftigt`.
    eink_vermietung
        See :func:`eink_vermietung`.
    eink_rente_zu_verst
        See :func:`eink_rente_zu_verst`.

    Returns
    -------

    """
    out = (
        eink_selbst
        + _zu_verst_eink_abhängig_beschäftigt
        + eink_vermietung
        + eink_rente_zu_verst
    )
    return out


def kapitaleink(
    kapitaleink_brutto: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Capital income minus Sparerpauschbetrag.

    Parameters
    ----------
    kapitaleink_brutto
        See :func:`kapitaleink_brutto`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        kapitaleink_brutto
        - eink_st_abzuege_params["sparerpauschbetrag"]
        - eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    )

    return max(out, 0.0)


def sum_eink_mit_kapital(
    sum_eink_ohne_kapital: float,
    kapitaleink: float,
) -> float:
    """Sum of gross incomes with capital income.

    Parameters
    ----------
    sum_eink_ohne_kapital
        See :func:`sum_eink_ohne_kapital`.
    kapitaleink
        See :func:`kapitaleink`.

    Returns
    -------

    """
    return sum_eink_ohne_kapital + kapitaleink


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
