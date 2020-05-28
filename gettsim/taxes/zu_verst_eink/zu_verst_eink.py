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
from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


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
    out = _zu_verst_eink_kein_kinderfreib_vorläufig * 0
    out.loc[~kind] = zve_tu / anz_erwachsene_in_tu.loc[~kind]
    return out


def _zu_verst_eink_kein_kinderfreib_vorläufig(
    sum_brutto_eink,
    vorsorge,
    sonderausgaben,
    behinderungsgrad_pauschbetrag,
    hh_freib,
    altersfreib,
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

    Returns
    -------

    """
    out = (
        sum_brutto_eink
        - vorsorge
        - sonderausgaben
        - behinderungsgrad_pauschbetrag
        - hh_freib
        - altersfreib
    ).clip(lower=0)
    return out


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
    out = _zu_verst_eink_kein_kinderfreib_vorläufig * 0
    out.loc[~kind] = zu_verst_eink_tu / anz_erwachsene_in_tu.loc[~kind]
    return out


def _ertragsanteil(jahr_renteneintr, eink_st_params):
    """Calculate the share of pensions subject to income taxation.

    Parameters
    ----------
    jahr_renteneintr

    Returns
    -------

    """
    out = piecewise_polynomial(
        x=jahr_renteneintr,
        lower_thresholds=eink_st_params["ertragsanteil"]["lower_thresholds"],
        upper_thresholds=eink_st_params["ertragsanteil"]["upper_thresholds"],
        rates=eink_st_params["ertragsanteil"]["rates"],
        intercepts_at_lower_thresholds=eink_st_params["ertragsanteil"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out


def _anz_kinder_in_tu(tu_id, kind):
    return (kind.astype(int)).groupby(tu_id).transform(sum)


def anz_erwachsene_in_tu(tu_id, kind):
    return ((~kind).astype(int)).groupby(tu_id).transform(sum)


def gemeinsam_veranlagt(anz_erwachsene_in_tu):
    return anz_erwachsene_in_tu == 2


def gemeinsam_veranlagte_tu(gemeinsam_veranlagt, tu_id):
    return gemeinsam_veranlagt.groupby(tu_id).any()


def bruttolohn_m_tu(bruttolohn_m, tu_id):
    return bruttolohn_m.groupby(tu_id).sum()
