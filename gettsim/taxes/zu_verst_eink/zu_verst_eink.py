"""
Calculate taxable income (zve = zu versteuerndes Einkommen). The calculation
    of the 6 branches of income is according to
    https://de.wikipedia.org/wiki/Einkommensteuer_(Deutschland)#Rechenschema

        In fact, you need several taxable incomes because of
        - child allowance vs. child benefit
        - abgeltungssteuer vs. taxing capital income in the tariff
        It's always the most favorable for the taxpayer, but you know that only after
         applying the tax schedule
"""
import copy

import numpy as np
import pandas as pd

from gettsim._numpy import numpy_vectorize


def _zu_verst_eink_kein_kinderfreib(
    _zu_verst_eink_kein_kinderfreib_vorläufig, kind, anz_erwachsene_in_tu, tu_id
):

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
    out = (
        sum_brutto_eink
        - vorsorge
        - sonderausgaben
        - behinderungsgrad_pauschalbetrag
        - hh_freib
        - altersfreib
    ).clip(lower=0)
    return out.rename("_zu_verst_eink_kein_kinderfreib_vorläufig")


def _zu_versteuerndes_eink_kind_freib(
    _zu_verst_eink_kein_kinderfreib_vorläufig,
    kind,
    anz_erwachsene_in_tu,
    kinderfreib,
    tu_id,
):

    zu_vers_eink_kinderfreib = (
        _zu_verst_eink_kein_kinderfreib_vorläufig[~kind] - kinderfreib.loc[~kind]
    )
    zu_verst_eink_tu = (
        (zu_vers_eink_kinderfreib.loc[~kind]).groupby(tu_id).transform(sum)
    )
    out = copy.deepcopy(_zu_verst_eink_kein_kinderfreib_vorläufig)
    out.loc[~kind] = zu_verst_eink_tu / anz_erwachsene_in_tu.loc[~kind]
    return out.rename("_zu_versteuerndes_eink_kind_freib")


def brutto_eink_1(eink_selbstst_m):
    """
    Income from Self-Employment

    Parameters
    ----------
    eink_selbstst_m

    Returns
    -------

    """
    out = np.maximum(12 * eink_selbstst_m, 0)
    return out.rename("brutto_eink_1")


def brutto_eink_1_tu(brutto_eink_1, tu_id):
    """


    Parameters
    ----------
    brutto_eink_1
    tu_id

    Returns
    -------

    """
    out = brutto_eink_1.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_1_tu")


def brutto_eink_4(bruttolohn_m, geringfügig_beschäftigt, eink_st_abzuege_params):
    """
    Calculates the gross incomes of non selfemployed work. The wage is reducted by a
    lump sum payment for 'Werbungskosten'
    Parameters
    ----------
    bruttolohn_m

    Returns
    -------

    """
    out = np.maximum(
        bruttolohn_m.multiply(12).subtract(
            eink_st_abzuege_params["werbungskostenpauschale"]
        ),
        0,
    )
    out.loc[geringfügig_beschäftigt] = 0
    return out.rename("brutto_eink_4")


def brutto_eink_4_tu(brutto_eink_4, tu_id):
    """

    Parameters
    ----------
    brutto_eink_4
    tu_id

    Returns
    -------

    """
    out = brutto_eink_4.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_4_tu")


def brutto_eink_5(kapital_eink_m):
    """
    Capital Income

    Parameters
    ----------
    kapital_eink_m

    Returns
    -------

    """
    out = np.maximum(12 * kapital_eink_m, 0)
    return out.rename("brutto_eink_5")


def brutto_eink_5_tu(brutto_eink_5, tu_id):
    """

    Parameters
    ----------
    brutto_eink_5
    tu_id

    Returns
    -------

    """
    out = brutto_eink_5.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_5_tu")


def brutto_eink_6(vermiet_eink_m):
    """
    Income from rents

    Parameters
    ----------
    vermiet_eink_m

    Returns
    -------

    """
    out = np.maximum(12 * vermiet_eink_m, 0)
    return out.rename("brutto_eink_6")


def brutto_eink_6_tu(brutto_eink_6, tu_id):
    """

    Parameters
    ----------
    brutto_eink_6
    tu_id

    Returns
    -------

    """
    out = brutto_eink_6.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_6_tu")


def brutto_eink_7(ges_rente_m, _ertragsanteil):
    """
    Calculates the gross income of 'Sonsitge Einkünfte'. In our case that's only
    pensions.

    Parameters
    ----------
    ges_rente_m
    _ertragsanteil

    Returns
    -------

    """
    out = _ertragsanteil.multiply(12 * ges_rente_m)
    return out.rename("brutto_eink_7")


def brutto_eink_7_tu(brutto_eink_7, tu_id):
    """

    Parameters
    ----------
    brutto_eink_7
    tu_id

    Returns
    -------

    """
    out = brutto_eink_7.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_7_tu")


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


def _sum_brutto_eink_ohne_kapital(
    brutto_eink_1, brutto_eink_4, brutto_eink_6, brutto_eink_7
):
    """
    Since 2009 capital income is not subject to noraml taxation.
    Parameters
    ----------
    brutto_eink_1
    brutto_eink_4
    brutto_eink_6
    brutto_eink_7

    Returns
    -------

    """
    out = brutto_eink_1 + brutto_eink_4 + brutto_eink_6 + brutto_eink_7
    return out.rename("sum_brutto_eink")


def _sum_brutto_eink_mit_kapital(
    _sum_brutto_eink_ohne_kapital, brutto_eink_5, eink_st_abzuege_params
):
    out = _sum_brutto_eink_ohne_kapital + (
        brutto_eink_5
        - eink_st_abzuege_params["sparerpauschbetrag"]
        - eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    ).clip(lower=0)
    return out.rename("sum_brutto_eink")


def behinderungsgrad_pauschalbetrag(behinderungsgrad, eink_st_abzuege_params):
    """
    Calculate the different deductions for different handicap degrees.

    Parameters
    ----------
    behinderungsgrad
    eink_st_abzuege_params

    Returns
    -------

    """
    behinderungsgrad_stufe = [
        behinderungsgrad.between(25, 30),
        behinderungsgrad.between(35, 40),
        behinderungsgrad.between(45, 50),
        behinderungsgrad.between(55, 60),
        behinderungsgrad.between(65, 70),
        behinderungsgrad.between(75, 80),
        behinderungsgrad.between(85, 90),
        behinderungsgrad.between(95, 100),
    ]

    out = np.nan_to_num(
        np.select(
            behinderungsgrad_stufe,
            eink_st_abzuege_params["behinderten_pausch_betrag"].values(),
        )
    )
    return pd.Series(
        data=out, index=behinderungsgrad.index, name="behinderungsgrad_pauschalbetrag"
    )


def hh_freib_bis_2014(alleinerziehend, eink_st_abzuege_params):
    """
    Calculates tax reduction for single parents. Used to be called
    'Haushaltsfreibetrag'

    Parameters
    ----------
    alleinerziehend
    eink_st_abzuege_params

    Returns
    -------

    """
    out = pd.Series(index=alleinerziehend.index, name="hh_freib", data=0, dtype=float)
    out.loc[alleinerziehend] = eink_st_abzuege_params["alleinerziehenden_freibetrag"]
    return out


def hh_freib_seit_2015(alleinerziehend, kind, tu_id, eink_st_abzuege_params):
    """
    Calculates tax reduction for single parents. Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'

    Parameters
    ----------
    alleinerziehend
    kind
    tu_id
    eink_st_abzuege_params

    Returns
    -------

    """
    out = pd.Series(index=alleinerziehend.index, name="hh_freib", data=0, dtype=float)
    anz_kinder = kind.groupby(tu_id).apply(sum)
    out.loc[alleinerziehend] = (
        eink_st_abzuege_params["alleinerziehenden_freibetrag"]
        + tu_id.replace(anz_kinder)
        * eink_st_abzuege_params["alleinerziehenden_freibetrag_zusatz"]
    )
    return out


def altersfreib(
    bruttolohn_m,
    alter,
    kapital_eink_m,
    eink_selbstst_m,
    vermiet_eink_m,
    eink_st_abzuege_params,
):
    """
    Calculates the deductions for elderly. Not tested yet!

    Parameters
    ----------
    bruttolohn_m
    alter
    kapital_eink_m
    eink_selbstst_m
    vermiet_eink_m
    eink_st_abzuege_params

    Returns
    -------

    """
    out = pd.Series(index=bruttolohn_m.index, name="altersfreib", data=0, dtype=float)
    out.loc[alter > 64] = (
        eink_st_abzuege_params["altersentlastung_quote"]
        * 12
        * (
            bruttolohn_m
            + (kapital_eink_m + eink_selbstst_m + vermiet_eink_m).clip(lower=0)
        )
    ).clip(upper=eink_st_abzuege_params["altersentlastungsbetrag_max"])
    return out


def _sonderausgaben_bis_2011(kind, eink_st_abzuege_params):
    """
    Until 2011, we just use the lumpsum payment.
    Parameters
    ----------
    kind
    eink_st_abzuege_params

    Returns
    -------

    """
    out = pd.Series(index=kind.index, data=0, dtype=float, name="sonderausgaben")
    out.loc[~kind] = eink_st_abzuege_params["sonderausgabenpauschbetrag"]
    return out


def _sonderausgaben_ab_2012(
    betreuungskost_m, tu_id, kind, anz_erwachsene_in_tu, eink_st_abzuege_params
):
    """
    Calculating sonderausgaben for childcare. We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg.
    Parameters
    ----------
    betreuungskost_m
    tu_id
    kind
    eink_st_abzuege_params
    anz_erwachsene_in_tu

    Returns
    -------

    """
    abziehbare_betreuungskosten = betreuungskost_m.multiply(12).clip(
        upper=eink_st_abzuege_params["kinderbetreuungskosten_abz_maximum"]
    )

    berechtigte_kinder = (kind.astype(int)).groupby(tu_id).transform(sum)
    out = (
        berechtigte_kinder
        * abziehbare_betreuungskosten
        * eink_st_abzuege_params["kinderbetreuungskosten_abz_anteil"]
    ).divide(anz_erwachsene_in_tu)

    out.loc[kind] = 0
    return out.rename("sonderausgaben")


def _altervorsorge_aufwend(
    kind, rentenv_beit_m, prv_rente_beit_m, eink_st_abzuege_params
):
    """
    Return the amount of contributions to retirement savings that is deductible from
    taxable income. **This function becomes relevant in 2005, do not use it for prior
    year**.

    The share of deductible contributions increases each year from 60% in 2005 to 100%
    in 2025.

    Parameters
    ----------
    kind
    rentenv_beit_m
    prv_rente_beit_m
    eink_st_abzuege_params

    Returns
    -------

    """
    einführungsfaktor = 0.6 + 0.02 * (min(eink_st_abzuege_params["jahr"], 2025) - 2005)
    out = (
        (einführungsfaktor * (2 * rentenv_beit_m + prv_rente_beit_m) - rentenv_beit_m)
        * 12
    ).clip(upper=eink_st_abzuege_params["vorsorge_altersaufw_max"])
    out.loc[kind] = 0
    return out.rename("_altervorsorge_aufwend")


def kinderfreib(
    _kindergeld_anspruch,
    kind,
    _zu_verst_eink_kein_kinderfreib_vorläufig,
    tu_id,
    eink_st_abzuege_params,
):
    # Calculate the possible kinderfreibetrag
    kifreib_total = sum(eink_st_abzuege_params["kinderfreibetrag"].values())
    # Count number of children eligible for Child Benefit.
    # Child allowance is only received for these kids.
    anz_kindergeld_kind = (
        (_kindergeld_anspruch.astype(int)).groupby(tu_id).transform(sum)
    )
    raw_kinderfreib = kifreib_total * anz_kindergeld_kind[~kind]

    # If in a tax unit one adult earns less than the kinderfreib, we transfer the
    # difference
    diff_kinderfreib = (
        _zu_verst_eink_kein_kinderfreib_vorläufig.loc[~kind] - raw_kinderfreib
    )
    # Get the transfers for each concerned tax unit, indexed with the tax unit.
    transfer_tu = diff_kinderfreib.loc[diff_kinderfreib < 0].reindex(
        index=tu_id[~kind].loc[diff_kinderfreib < 0]
    )
    # Assign negative transfers to adults in tax unit
    transfers = tu_id[~kind & (diff_kinderfreib < 0)].replace(transfer_tu)
    out = pd.Series(index=kind.index, data=0, dtype=float, name="kinderfreib")

    # Transfers are saved as negative values and therefore need to be substracted
    out.loc[~kind & (diff_kinderfreib > 0)] = raw_kinderfreib.loc[
        diff_kinderfreib > 0
    ].subtract(transfers.loc[diff_kinderfreib > 0], fill_value=0)
    out.loc[~kind & (diff_kinderfreib < 0)] = raw_kinderfreib.loc[
        diff_kinderfreib < 0
    ].add(transfers.loc[diff_kinderfreib < 0], fill_value=0)

    return out


def anz_erwachsene_in_tu(tu_id, kind):
    out = ((~kind).astype(int)).groupby(tu_id).transform(sum)
    return out.rename("anz_erwachsene_in_tu")


def gemeinsam_veranlagt(tu_id, anz_erwachsene_in_tu):
    out = anz_erwachsene_in_tu == 2
    return out.rename("gemeinsam_veranlagt")


def gemeinsam_veranlagte_tu(gemeinsam_veranlagt, tu_id):
    out = gemeinsam_veranlagt.groupby(tu_id).apply(all)
    return out.rename("gemeinsam_veranlagte_tu")


def _vorsorge_alternative_2005_bis_2009(
    _altervorsorge_aufwend,
    ges_krankenv_beitr_m,
    arbeitsl_v_beit_m,
    pflegev_beit_m,
    kind,
    eink_st_abzuege_params,
):
    """
    Vorsorgeaufwendungen 2005 to 2010
    Pension contributions are accounted for up to €20k.
    From this, a certain share can actually be deducted,
    starting with 60% in 2005.
    Other deductions are simply added up, up to a ceiling of 1500 p.a. for standard employees.

    Parameters
    ----------
    _altervorsorge_aufwend
    ges_krankenv_beitr_m
    arbeitsl_v_beit_m
    pflegev_beit_m
    eink_st_abzuege_params

    Returns
    -------

    """
    out = copy.deepcopy(_altervorsorge_aufwend) * 0
    sum_vorsorge = (
        12 * (ges_krankenv_beitr_m + arbeitsl_v_beit_m + pflegev_beit_m)
    ).clip(upper=eink_st_abzuege_params["vorsorge_sonstige_aufw_max"])
    out.loc[~kind] = (
        sum_vorsorge.loc[~kind] + _altervorsorge_aufwend.loc[~kind]
    ).astype(int)
    return out.rename("_vorsorge_alternative_2005_bis_2010")


def vorsorge_2005_bis_2009(_vorsorge_alternative_2005_bis_2009, vorsorge_bis_2004):
    """
    With the 2005 reform, no taxpayer was supposed to be affected negatively.
    Therefore, one needs to compute amounts
    (2004 and 2005 regime) and take the higher one.

    Parameters
    ----------
    _vorsorge_alternative_2005_bis_2009
    vorsorge_bis_2004

    Returns
    -------

    """
    old_reform = vorsorge_bis_2004 > _vorsorge_alternative_2005_bis_2009
    out = copy.deepcopy(_vorsorge_alternative_2005_bis_2009)
    out.loc[old_reform] = vorsorge_bis_2004.loc[old_reform]
    return out.rename("vorsorge")


def vorsorge_ab_2010(vorsorge_bis_2004, _vorsorge_alternative_ab_2010):
    """
    After a supreme court ruling, the 2005 rule had to be changed in 2010.
        Therefore, one needs to compute amounts
        (2004 and 2010 regime) and take the higher one. (§10 (3a) EStG).
        Sidenote: The 2010 ruling is by construction
        *always* more or equally beneficial than the 2005 one,
        so no need for a separate check there.

    Parameters
    ----------
    vorsorge_bis_2004
    _vorsorge_alternative_ab_2010

    Returns
    -------

    """
    # import pdb
    # pdb.set_trace()
    old_reform = vorsorge_bis_2004 > _vorsorge_alternative_ab_2010
    out = copy.deepcopy(_vorsorge_alternative_ab_2010)
    out.loc[old_reform] = vorsorge_bis_2004.loc[old_reform]
    return out.rename("vorsorge")


def _vorsorge_alternative_ab_2010(
    _altervorsorge_aufwend,
    pflegev_beit_m,
    ges_krankenv_beitr_m,
    arbeitsl_v_beit_m,
    kind,
    eink_st_abzuege_params,
):
    """
    Vorsorgeaufwendungen 2010 regime
    § 10 (3) EStG
    The share of deductable pension contributions increases each year by 2 pp.
    ('nachgelagerte Besteuerung'). In 2018, it's 86%. Add other contributions;
    4% from health contributions are not deductable.
    only deduct pension contributions up to the ceiling. multiply by 2
    because it's both employee and employer contributions.

    Contributions to other security branches can also be deducted.

    This ruling differs to vorsorge2005() only in the treatment of other contributions.

    Parameters
    ----------
    _altervorsorge_aufwend
    pflegev_beit_m
    ges_krankenv_beitr_m
    arbeitsl_v_beit_m
    eink_st_abzuege_params

    Returns
    -------

    """
    out = copy.deepcopy(_altervorsorge_aufwend) * 0
    # 'Basisvorsorge': Health and old-age care contributions are deducted anyway.
    sonstige_vors = 12 * (
        pflegev_beit_m.loc[~kind]
        + (1 - eink_st_abzuege_params["vorsorge_kranken_minderung"])
        * ges_krankenv_beitr_m.loc[~kind]
    )
    # maybe add unemployment insurance, but do not exceed 1900€.
    out.loc[~kind] = sonstige_vors.clip(
        lower=(sonstige_vors + 12 * arbeitsl_v_beit_m.loc[~kind]).clip(
            upper=eink_st_abzuege_params["vorsorge_sonstige_aufw_max"]
        )
    )
    out.loc[~kind] += _altervorsorge_aufwend.loc[~kind]
    return out.rename("_vorsorge_alternative_ab_2010")


def vorsorge_bis_2004(
    _lohn_vorsorgeabzug_single,
    _lohn_vorsorgeabzug_tu,
    ges_krankenv_beitr_m,
    rentenv_beit_m,
    ges_krankenv_beitr_m_tu,
    rentenv_beitr_m_tu,
    tu_id,
    gemeinsam_veranlagte_tu,
    gem_veranlagt,
    kind,
    eink_st_abzuege_params,
):
    out = copy.deepcopy(ges_krankenv_beitr_m) * 0
    out.loc[~gem_veranlagt & ~kind] = berechne_vorsorge_bis_2004(
        _lohn_vorsorgeabzug_single.loc[~kind],
        ges_krankenv_beitr_m.loc[~gem_veranlagt & ~kind],
        rentenv_beit_m.loc[~gem_veranlagt & ~kind],
        1,
        eink_st_abzuege_params,
    )
    vorsorge_tu = berechne_vorsorge_bis_2004(
        _lohn_vorsorgeabzug_tu,
        ges_krankenv_beitr_m_tu.loc[gemeinsam_veranlagte_tu],
        rentenv_beitr_m_tu.loc[gemeinsam_veranlagte_tu],
        2,
        eink_st_abzuege_params,
    )
    out.loc[gem_veranlagt & ~kind] = tu_id[gem_veranlagt].replace(vorsorge_tu)
    return out.rename("vorsorge")


def _lohn_vorsorge_bis_2019_single(
    bruttolohn_m, gemeinsam_veranlagt, eink_st_abzuege_params
):
    out = (
        eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
        * 12
        * bruttolohn_m.loc[~gemeinsam_veranlagt]
    ).clip(lower=0)
    return out.rename("_lohn_vorsorge_bis_2019_single")


def _lohn_vorsorgeabzug_bis_2019_tu(
    bruttolohn_m_tu, gemeinsam_veranlagte_tu, eink_st_abzuege_params
):
    out = 0.5 * (
        2 * eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
        * 12
        * bruttolohn_m_tu.loc[gemeinsam_veranlagte_tu]
    ).clip(lower=0)
    return out.rename("_lohn_vorsorgeabzug_bis_2019_tu")


def _lohn_vorsorge_ab_2020_single(gemeinsam_veranlagt):
    out = gemeinsam_veranlagt.loc[gemeinsam_veranlagt].astype(int) * 0
    return out.rename("_lohn_vorsorge_bis_2019_single")


def _lohn_vorsorge_ab_2020_tu(gemeinsam_veranlagte_tu):
    out = gemeinsam_veranlagte_tu.loc[gemeinsam_veranlagte_tu].astype(int) * 0
    return out.rename("_lohn_vorsorge_bis_2019_tu")


@numpy_vectorize(
    excluded=["anzahl_erwachsene", "eink_st_abzuege_params"], otypes=[float]
)
def berechne_vorsorge_bis_2004(
    lohn_vorsorge,
    krankenv_beitr,
    rentenv_beitr,
    anzahl_erwachsene,
    eink_st_abzuege_params,
):
    item_1 = (1 / anzahl_erwachsene) * max(
        12 * (rentenv_beitr + krankenv_beitr) - lohn_vorsorge, 0
    )
    item_2 = (1 / anzahl_erwachsene) * min(
        item_1, eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]
    )

    item_3 = 0.5 * np.minimum(
        (item_1 - item_2),
        anzahl_erwachsene * eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"],
    )
    out = (lohn_vorsorge + item_2 + item_3).astype(int)
    return out


def bruttolohn_m_tu(bruttolohn_m, tu_id):
    out = bruttolohn_m.groupby(tu_id).apply(sum)
    return out.rename("bruttolohn_m_tu")
