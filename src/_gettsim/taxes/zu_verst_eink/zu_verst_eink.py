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

from _gettsim.shared import add_rounding_spec


def freibeträge_ind_y(
    _eink_st_behinderungsgrad_pauschbetrag_y: float,
    eink_st_altersfreib_y: float,
    alleinerz_freib_y_tu: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level.

    #ToDo: Check whether these columns are really calculated at the individual level.
    Parameters
    ----------

    _eink_st_behinderungsgrad_pauschbetrag_y
        See :func:`_eink_st_behinderungsgrad_pauschbetrag_y`.
    eink_st_altersfreib_y
        See :func:`eink_st_altersfreib_y`.
    alleinerz_freib_y_tu
        See :func:`alleinerz_freib_y_tu`.

    Returns
    -------

    """
    out = (
        _eink_st_behinderungsgrad_pauschbetrag_y
        + eink_st_altersfreib_y
        + alleinerz_freib_y_tu
    )
    return out


def freibeträge_y_tu(
    eink_st_sonderausgaben_y_tu: float,
    vorsorgeaufw_y_tu: float,
    freibeträge_ind_y_tu: float,
) -> float:
    """Calculate total allowances on tax unit level.

    Parameters
    ----------

    eink_st_sonderausgaben_y_tu
        See :func:`eink_st_sonderausgaben_y_tu`.
    vorsorgeaufw_y_tu
        See :func:`vorsorgeaufw_y_tu`.
    freibeträge_ind_y_tu
        See :func:`freibeträge_ind_y_tu`.

    Returns
    -------

    """
    out = eink_st_sonderausgaben_y_tu + vorsorgeaufw_y_tu + freibeträge_ind_y_tu

    return out


def _zu_verst_eink_ohne_kinderfreib_y_tu(
    sum_eink_y_tu: float,
    freibeträge_y_tu: float,
) -> float:
    """Calculate taxable income without child allowance on tax unit level.

    Parameters
    ----------
    sum_eink_y_tu
        See :func:`sum_eink_y_tu`.
    freibeträge_y_tu
        See :func:`freibeträge_y_tu`.


    Returns
    -------

    """
    out = sum_eink_y_tu - freibeträge_y_tu

    return max(out, 0.0)


def _zu_verst_eink_mit_kinderfreib_y_tu(
    _zu_verst_eink_ohne_kinderfreib_y_tu: float, eink_st_kinderfreib_y_tu: float
) -> float:
    """Calculate taxable income with child allowance on tax unit level.

    Parameters
    ----------
    _zu_verst_eink_ohne_kinderfreib_y_tu
        See :func:`_zu_verst_eink_ohne_kinderfreib_y_tu`.
    eink_st_kinderfreib_y_tu
        See :func:`eink_st_kinderfreib_y_tu`.

    Returns
    -------

    """

    out = _zu_verst_eink_ohne_kinderfreib_y_tu - eink_st_kinderfreib_y_tu
    return max(out, 0.0)


@add_rounding_spec(params_key="eink_st")
def zu_verst_eink_y_tu(
    _zu_verst_eink_mit_kinderfreib_y_tu: float,
    _zu_verst_eink_ohne_kinderfreib_y_tu: float,
    kinderfreib_günstiger_tu: bool,
) -> float:
    """Calculate taxable income on tax unit level.

    Parameters
    ----------
    _zu_verst_eink_mit_kinderfreib_y_tu
        See :func:`_zu_verst_eink_mit_kinderfreib_y_tu`.
    _zu_verst_eink_ohne_kinderfreib_y_tu
        See :func:`_zu_verst_eink_ohne_kinderfreib_y_tu`.
    kinderfreib_günstiger_tu
        See :func:`kinderfreib_günstiger_tu`.

    Returns
    -------

    """
    if kinderfreib_günstiger_tu:
        out = _zu_verst_eink_mit_kinderfreib_y_tu
    else:
        out = _zu_verst_eink_ohne_kinderfreib_y_tu

    return out
