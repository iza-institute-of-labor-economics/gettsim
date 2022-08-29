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


def individual_freibeträge(
    vorsorgeaufw: float,
    _eink_st_behinderungsgrad_pauschbetrag: float,
    eink_st_altersfreib: float,
    alleinerz_freib_tu: float,
) -> float:
    """Calculate individual allowances.

    Parameters
    ----------

    vorsorgeaufw
        See :func:`vorsorgeaufw`.
    _eink_st_behinderungsgrad_pauschbetrag
        See :func:`_eink_st_behinderungsgrad_pauschbetrag`.
    eink_st_altersfreib
        See :func:`eink_st_altersfreib`.
    alleinerz_freib_tu
        See :func:`alleinerz_freib_tu`.

    Returns
    -------

    """
    out = (
        vorsorgeaufw
        + _eink_st_behinderungsgrad_pauschbetrag
        + eink_st_altersfreib
        + alleinerz_freib_tu
    )
    return out


def freibeträge_tu(
    eink_st_sonderausgaben_tu: float,
    individual_freibeträge_tu: float,
) -> float:
    """Calculate total allowances.

    Parameters
    ----------

    eink_st_sonderausgaben_tu
        See :func:`eink_st_sonderausgaben_tu`.
    individual_freibeträge_tu
        See :func:`individual_freibeträge_tu`.

    Returns
    -------

    """
    out = individual_freibeträge_tu + eink_st_sonderausgaben_tu

    return out


def _zu_verst_eink_ohne_kinderfreib_tu(
    sum_eink_tu: float,
    freibeträge_tu: float,
) -> float:
    """Calculate taxable income without child allowance per tax unit.

    Parameters
    ----------
    sum_eink_tu
        See :func:`sum_eink_tu`.
    freibeträge_tu
        See :func:`freibeträge_tu`.


    Returns
    -------

    """
    out = sum_eink_tu - freibeträge_tu

    return max(out, 0.0)


def zu_verst_eink_mit_kinderfreib_tu(
    _zu_verst_eink_ohne_kinderfreib_tu: float, eink_st_kinderfreib_tu: float
) -> float:
    """Calculate taxable income with child allowance per tax unit.

    Parameters
    ----------
    _zu_verst_eink_ohne_kinderfreib_tu
        See :func:`_zu_verst_eink_ohne_kinderfreib_tu`.
    eink_st_kinderfreib_tu
        See :func:`eink_st_kinderfreib_tu`.

    Returns
    -------

    """

    out = _zu_verst_eink_ohne_kinderfreib_tu - eink_st_kinderfreib_tu
    return max(out, 0.0)
