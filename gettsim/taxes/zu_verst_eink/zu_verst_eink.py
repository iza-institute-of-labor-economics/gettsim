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


def _zu_verst_eink_kein_kinderfreib_tu(
    sum_brutto_eink,
    vorsorge,
    sonderausgaben,
    behinderungsgrad_pauschbetrag,
    hh_freib,
    altersfreib,
    tu_id,
):
    """

    Parameters
    ----------
    sum_brutto_eink
    vorsorge
    sonderausgaben
    behinderungsgrad_pauschbetrag
    hh_freib
    altersfreib
    tu_id

    Returns
    -------

    """

    out = (
        sum_brutto_eink
        - vorsorge
        - sonderausgaben
        - behinderungsgrad_pauschbetrag
        - tu_id.replace(hh_freib)
        - altersfreib
    ).clip(lower=0)
    return out.groupby(tu_id).sum()


def _zu_verst_eink_kinderfreib_tu(
    _zu_verst_eink_kein_kinderfreib_tu, kinderfreib_tu,
):
    """

    Parameters
    ----------
    _zu_verst_eink_kein_kinderfreib_tu
    kinderfreib_tu

    Returns
    -------

    """
    return _zu_verst_eink_kein_kinderfreib_tu - kinderfreib_tu
