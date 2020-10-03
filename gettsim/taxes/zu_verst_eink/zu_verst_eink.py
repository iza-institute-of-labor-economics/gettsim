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
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries

def zu_verst_eink_kein_kinderfreib_tu(
    sum_brutto_eink,
    vorsorge,
    sonderausgaben,
    behinderungsgrad_pauschbetrag,
    alleinerziehend_freib_tu,
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
        - tu_id.replace(alleinerziehend_freib_tu)
        - altersfreib
    ).clip(lower=0)
    return out.groupby(tu_id).sum()


def zu_verst_eink_kinderfreib_tu(
    zu_verst_eink_kein_kinderfreib_tu, kinderfreib_tu,
):
    """

    Parameters
    ----------
    zu_verst_eink_kein_kinderfreib_tu
    kinderfreib_tu

    Returns
    -------

    """
    return zu_verst_eink_kein_kinderfreib_tu - kinderfreib_tu
