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
import copy

import pandas as pd


def _zu_verst_eink_kein_kinderfreib(
    _zu_verst_eink_kein_kinderfreib_vorläufig, kind, anz_erwachsene_in_tu, tu_id
):
    """

    Parameters
    ----------
    _zu_verst_eink_kein_kinderfreib_vorläufig
    kind
    anz_erwachsene_in_tu
    tu_id

    Returns
    -------

    """

    zve_tu = (
        (_zu_verst_eink_kein_kinderfreib_vorläufig.loc[~kind])
        .groupby(tu_id)
        .transform(sum)
    )
    out = copy.deepcopy(_zu_verst_eink_kein_kinderfreib_vorläufig)
    out.loc[~kind] = zve_tu / anz_erwachsene_in_tu.loc[~kind]
    return out.rename("_zu_verst_eink_kein_kinderfreib")


def _zu_verst_eink_kein_kinderfreib_vorläufig(
    sum_brutto_eink,
    vorsorge,
    sonderausgaben,
    behinderungsgrad_pauschalbetrag,
    hh_freib,
    altersfreib,
):
    """

    Parameters
    ----------
    sum_brutto_eink
    vorsorge
    sonderausgaben
    behinderungsgrad_pauschalbetrag
    hh_freib
    altersfreib

    Returns
    -------

    """
    out = (
        sum_brutto_eink
        - vorsorge
        - sonderausgaben
        - behinderungsgrad_pauschalbetrag
        - hh_freib
        - altersfreib
    ).clip(lower=0)
    return out.rename("_zu_verst_eink_kein_kinderfreib_vorläufig")


def _zu_verst_eink_kinderfreib(
    _zu_verst_eink_kein_kinderfreib_vorläufig,
    kind,
    anz_erwachsene_in_tu,
    kinderfreib,
    tu_id,
):
    """

    Parameters
    ----------
    _zu_verst_eink_kein_kinderfreib_vorläufig
    kind
    anz_erwachsene_in_tu
    kinderfreib
    tu_id

    Returns
    -------

    """

    zu_vers_eink_kinderfreib = (
        _zu_verst_eink_kein_kinderfreib_vorläufig[~kind] - kinderfreib.loc[~kind]
    )
    zu_verst_eink_tu = (
        (zu_vers_eink_kinderfreib.loc[~kind]).groupby(tu_id).transform(sum)
    )
    out = copy.deepcopy(_zu_verst_eink_kein_kinderfreib_vorläufig)
    out.loc[~kind] = zu_verst_eink_tu / anz_erwachsene_in_tu.loc[~kind]
    return out.rename("_zu_verst_eink_kinderfreib")


def _ertragsanteil(jahr_renteneintr):
    """
    Calculate the share of pensions subject to income taxation.

    Parameters
    ----------
    jahr_renteneintr

    Returns
    -------

    """
    out = pd.Series(index=jahr_renteneintr.index, name="_ertragsanteil", dtype=float)
    out.loc[jahr_renteneintr <= 2004] = 0.27
    out.loc[jahr_renteneintr.between(2005, 2020)] = 0.5 + 0.02 * (
        jahr_renteneintr - 2005
    )
    out.loc[jahr_renteneintr.between(2021, 2040)] = 0.8 + 0.01 * (
        jahr_renteneintr - 2020
    )
    out.loc[jahr_renteneintr >= 2041] = 1
    return out


def anz_erwachsene_in_tu(tu_id, kind):
    out = ((~kind).astype(int)).groupby(tu_id).transform(sum)
    return out.rename("anz_erwachsene_in_tu")


def gemeinsam_veranlagt(anz_erwachsene_in_tu):
    out = anz_erwachsene_in_tu == 2
    return out.rename("gemeinsam_veranlagt")


def gemeinsam_veranlagte_tu(gemeinsam_veranlagt, tu_id):
    out = gemeinsam_veranlagt.groupby(tu_id).apply(any)
    return out.rename("gemeinsam_veranlagte_tu")


def bruttolohn_m_tu(bruttolohn_m, tu_id):
    out = bruttolohn_m.groupby(tu_id).apply(sum)
    return out.rename("bruttolohn_m_tu")
