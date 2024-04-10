"""
Calculate taxable income (zve = zu versteuerndes Einkommen). The calculation
of the 7 branches of income is according to
https://de.wikipedia.org/wiki/Einkommensteuer_(Deutschland)#Rechenschema

The income types 1 to 3 according to the law are subsumed under the first income typ
(business income). The distinction is important as there are different deduction rules
for each income type. In fact, you need several taxable incomes because of

- child allowance vs. child benefit
- abgeltungssteuer vs. taxing capital income in the tariff ( not implemented yet, #81)

It's always the most favorable for the taxpayer, but you know that only after
applying the tax schedule.
"""

from _gettsim.shared import policy_info


def freibeträge_ind_y(
    _eink_st_behinderungsgrad_pauschbetrag_y: float,
    eink_st_altersfreib_y: float,
    alleinerz_freib_y_sn: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level.

    #ToDo: Check whether these columns are really calculated at the individual level.
    Parameters
    ----------

    _eink_st_behinderungsgrad_pauschbetrag_y
        See :func:`_eink_st_behinderungsgrad_pauschbetrag_y`.
    eink_st_altersfreib_y
        See :func:`eink_st_altersfreib_y`.
    alleinerz_freib_y_sn
        See :func:`alleinerz_freib_y_sn`.

    Returns
    -------

    """
    out = (
        _eink_st_behinderungsgrad_pauschbetrag_y
        + eink_st_altersfreib_y
        + alleinerz_freib_y_sn
    )
    return out


def freibeträge_y_sn(
    eink_st_sonderausgaben_y_sn: float,
    vorsorgeaufw_y_sn: float,
    freibeträge_ind_y_sn: float,
) -> float:
    """Calculate total allowances on Steuernummer level.

    Parameters
    ----------

    eink_st_sonderausgaben_y_sn
        See :func:`eink_st_sonderausgaben_y_sn`.
    vorsorgeaufw_y_sn
        See :func:`vorsorgeaufw_y_sn`.
    freibeträge_ind_y_sn
        See :func:`freibeträge_ind_y_sn`.

    Returns
    -------

    """
    out = eink_st_sonderausgaben_y_sn + vorsorgeaufw_y_sn + freibeträge_ind_y_sn

    return out


def _zu_verst_eink_ohne_kinderfreib_y_sn(
    sum_eink_y_sn: float,
    freibeträge_y_sn: float,
) -> float:
    """Calculate taxable income without child allowance on Steuernummer level.

    Parameters
    ----------
    sum_eink_y_sn
        See :func:`sum_eink_y_sn`.
    freibeträge_y_sn
        See :func:`freibeträge_y_sn`.


    Returns
    -------

    """
    out = sum_eink_y_sn - freibeträge_y_sn

    return max(out, 0.0)


def _zu_verst_eink_mit_kinderfreib_y_sn(
    _zu_verst_eink_ohne_kinderfreib_y_sn: float, eink_st_kinderfreib_y_sn: float
) -> float:
    """Calculate taxable income with child allowance on Steuernummer level.

    Parameters
    ----------
    _zu_verst_eink_ohne_kinderfreib_y_sn
        See :func:`_zu_verst_eink_ohne_kinderfreib_y_sn`.
    eink_st_kinderfreib_y_sn
        See :func:`eink_st_kinderfreib_y_sn`.

    Returns
    -------

    """

    out = _zu_verst_eink_ohne_kinderfreib_y_sn - eink_st_kinderfreib_y_sn
    return max(out, 0.0)


@policy_info(params_key_for_rounding="eink_st")
def zu_verst_eink_y_sn(
    _zu_verst_eink_mit_kinderfreib_y_sn: float,
    _zu_verst_eink_ohne_kinderfreib_y_sn: float,
    kinderfreib_günstiger_sn: bool,
) -> float:
    """Calculate taxable income on Steuernummer level.

    Parameters
    ----------
    _zu_verst_eink_mit_kinderfreib_y_sn
        See :func:`_zu_verst_eink_mit_kinderfreib_y_sn`.
    _zu_verst_eink_ohne_kinderfreib_y_sn
        See :func:`_zu_verst_eink_ohne_kinderfreib_y_sn`.
    kinderfreib_günstiger_sn
        See :func:`kinderfreib_günstiger_sn`.

    Returns
    -------

    """
    if kinderfreib_günstiger_sn:
        out = _zu_verst_eink_mit_kinderfreib_y_sn
    else:
        out = _zu_verst_eink_ohne_kinderfreib_y_sn

    return out
