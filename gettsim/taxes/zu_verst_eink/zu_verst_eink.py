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
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def sum_brutto_eink_tu(sum_brutto_eink: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Sum of gross incomes on tax unit level.

    Parameters
    ----------
    sum_brutto_eink
        See :func:`sum_brutto_eink`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return sum_brutto_eink.groupby(tu_id).sum()


def freibetraege(
    vorsorge: FloatSeries,
    sonderausgaben: FloatSeries,
    behinderungsgrad_pauschbetrag: FloatSeries,
    alleinerziehend_freib_tu: FloatSeries,
    altersfreib: FloatSeries,
    tu_id: IntSeries,
) -> FloatSeries:
    """Calculate taxable income without child allowance.

    Parameters
    ----------

    vorsorge
        See :func:`vorsorge`.
    sonderausgaben
        See :func:`sonderausgaben`.
    behinderungsgrad_pauschbetrag
        See :func:`behinderungsgrad_pauschbetrag`.
    alleinerziehend_freib_tu
        See :func:`alleinerziehend_freib_tu`.
    altersfreib
        See :func:`altersfreib`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """

    out = (
        vorsorge
        + sonderausgaben
        + behinderungsgrad_pauschbetrag
        + tu_id.replace(alleinerziehend_freib_tu)
        + altersfreib
    )
    return out


def freibetraege_tu(freibetraege: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Sum of gross incomes on tax unit level.

    Parameters
    ----------
    freibetraege
        See :func:`freibetraege`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return freibetraege.groupby(tu_id).sum()


def zu_verst_eink_kein_kinderfreib_tu(
    sum_brutto_eink_tu: FloatSeries, freibetraege_tu: FloatSeries,
) -> FloatSeries:
    """Calculate taxable income without child allowance.

    Parameters
    ----------
    sum_brutto_eink_tu
        See :func:`sum_brutto_eink_tu`.
    freibetraege_tu
        See :func:`freibetraege_tu`.


    Returns
    -------

    """

    return (sum_brutto_eink_tu - freibetraege_tu).clip(lower=0)


def zu_verst_eink_kinderfreib_tu(
    zu_verst_eink_kein_kinderfreib_tu: FloatSeries, kinderfreib_tu: FloatSeries
) -> FloatSeries:
    """Calculate taxable income with child allowance.

    Parameters
    ----------
    zu_verst_eink_kein_kinderfreib_tu
        See :func:`zu_verst_eink_kein_kinderfreib_tu`.
    kinderfreib_tu
        See :func:`kinderfreib_tu`.

    Returns
    -------

    """
    return zu_verst_eink_kein_kinderfreib_tu - kinderfreib_tu
