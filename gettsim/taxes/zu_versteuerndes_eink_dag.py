import copy

import numpy as np
import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.zu_versteuerndes_eink import zve


def vorsorge(
    p_id,
    hh_id,
    tu_id,
    bruttolohn_m,
    betreuungskost_m,
    eink_selbstst_m,
    kapital_eink_m,
    vermiet_eink_m,
    jahr_renteneintr,
    ges_rente_m,
    arbeitsstunden_w,
    in_ausbildung,
    gem_veranlagt,
    kind,
    behinderungsgrad,
    rentenv_beit_m,
    prv_rente_beit_m,
    arbeitsl_v_beit_m,
    pflegev_beit_m,
    alleinerziehend,
    alter,
    anz_kinder_tu,
    jahr,
    wohnort_ost,
    brutto_eink_1,
    brutto_eink_4,
    brutto_eink_5,
    brutto_eink_6,
    brutto_eink_7,
    sonderausgaben,
    sum_brutto_eink,
    _kindergeld_anspruch,
    hh_freib,
    altersfreib,
    _altervorsorge_aufwend,
    behinderungsgrad_pauschalbetrag,
    ges_krankenv_beit_m,
    eink_st_abzuege_params,
    soz_vers_beitr_params,
    kindergeld_params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            bruttolohn_m,
            betreuungskost_m,
            eink_selbstst_m,
            kapital_eink_m,
            vermiet_eink_m,
            jahr_renteneintr,
            ges_rente_m,
            arbeitsstunden_w,
            in_ausbildung,
            gem_veranlagt,
            kind,
            behinderungsgrad,
            rentenv_beit_m,
            prv_rente_beit_m,
            arbeitsl_v_beit_m,
            pflegev_beit_m,
            alleinerziehend,
            alter,
            anz_kinder_tu,
            jahr,
            brutto_eink_1,
            brutto_eink_4,
            brutto_eink_5,
            brutto_eink_6,
            brutto_eink_7,
            sum_brutto_eink,
            _kindergeld_anspruch,
            altersfreib,
            sonderausgaben,
            _altervorsorge_aufwend,
            behinderungsgrad_pauschalbetrag,
            wohnort_ost,
            ges_krankenv_beit_m,
            hh_freib,
        ],
        axis=1,
    )
    out_cols = [
        "_zu_versteuerndes_eink_kein_kind_freib",
        "_zu_versteuerndes_eink_kind_freib",
        "kind_freib",
        "_ertragsanteil",
        "vorsorge",
    ]

    df = apply_tax_transfer_func(
        df,
        tax_func=zve,
        level=["hh_id", "tu_id"],
        in_cols=df.columns.tolist(),
        out_cols=out_cols,
        func_kwargs={
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "kindergeld_params": kindergeld_params,
        },
    )
    return df["vorsorge"]


def _zu_versteuerndes_eink_kein_kind_freib(
    _zu_versteuerndes_eink_kein_kind_freib_vorläufig, kind, anz_erwachsene_in_tu, tu_id
):

    zve_tu = (
        (_zu_versteuerndes_eink_kein_kind_freib_vorläufig.loc[~kind])
        .groupby(tu_id)
        .transform(sum)
    )
    out = copy.deepcopy(_zu_versteuerndes_eink_kein_kind_freib_vorläufig)
    out.loc[~kind] = zve_tu / anz_erwachsene_in_tu.loc[~kind]
    return out.rename("_zu_versteuerndes_eink_kein_kind_freib")


def _zu_versteuerndes_eink_kein_kind_freib_vorläufig(
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
    import pdb

    pdb.set_trace()
    return out.rename("_zu_versteuerndes_eink_kein_kind_freib_vorläufig")


def _zu_versteuerndes_eink_kind_freib(
    _zu_versteuerndes_eink_kein_kind_freib_vorläufig,
    kind,
    anz_erwachsene_in_tu,
    kinderfreib,
    tu_id,
):
    import pdb

    pdb.set_trace()
    zu_vers_eink_kinderfreib = (
        _zu_versteuerndes_eink_kein_kind_freib_vorläufig[~kind] - kinderfreib.loc[~kind]
    )
    zu_verst_eink_tu = (
        (zu_vers_eink_kinderfreib.loc[~kind]).groupby(tu_id).transform(sum)
    )
    out = copy.deepcopy(_zu_versteuerndes_eink_kein_kind_freib_vorläufig)
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
    _zu_versteuerndes_eink_kein_kind_freib_vorläufig,
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
        _zu_versteuerndes_eink_kein_kind_freib_vorläufig.loc[~kind] - raw_kinderfreib
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
