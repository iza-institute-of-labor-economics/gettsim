import numpy as np
import pandas as pd


def behinderungsgrad_pauschbetrag(behinderungsgrad, eink_st_abzuege_params):
    """Calculate the different deductions for different handicap degrees.

    Parameters
    ----------
    behinderungsgrad
    eink_st_abzuege_params

    Returns
    -------

    """
    # Get disability degree thresholds
    bins = sorted(eink_st_abzuege_params["behinderten_pauschbetrag"])
    # Create corresponding bins
    binned = pd.cut(behinderungsgrad, bins=bins + [np.inf], right=False, labels=bins)
    # Replace values in the intervals
    out = (
        binned.replace(eink_st_abzuege_params["behinderten_pauschbetrag"])
        .astype(float)
        .fillna(0)
    )

    return out


def alleinerziehend_freib_tu_bis_2014(alleinerziehend_tu, eink_st_abzuege_params):
    """
    Calculates tax reduction for single parents. Used to be called
    'Haushaltsfreibetrag'

    Parameters
    ----------
    alleinerziehend_tu
    eink_st_abzuege_params

    Returns
    -------

    """
    out = alleinerziehend_tu.astype(float) * 0
    out.loc[alleinerziehend_tu] = eink_st_abzuege_params["alleinerziehenden_freibetrag"]
    return out


def alleinerziehend_freib_tu_seit_2015(
    alleinerziehend_tu, anz_kinder_tu, eink_st_abzuege_params
):
    """
    Calculates tax reduction for single parents. Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'

    Parameters
    ----------
    alleinerziehend_tu
    eink_st_abzuege_params

    Returns
    -------

    """
    out = alleinerziehend_tu.astype(float) * 0
    out.loc[alleinerziehend_tu] = (
        eink_st_abzuege_params["alleinerziehenden_freibetrag"]
        + anz_kinder_tu.loc[alleinerziehend_tu]
        * eink_st_abzuege_params["alleinerziehenden_freibetrag_zusatz"]
    )
    return out


def altersfreib(
    bruttolohn_m,
    alter,
    kapital_eink_m,
    eink_selbst_m,
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
    eink_selbst_m
    vermiet_eink_m
    eink_st_abzuege_params

    Returns
    -------

    """
    out = bruttolohn_m * 0
    out.loc[alter > 64] = (
        eink_st_abzuege_params["altersentlastung_quote"]
        * 12
        * (
            bruttolohn_m
            + (kapital_eink_m + eink_selbst_m + vermiet_eink_m).clip(lower=0)
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
    out = kind.astype(float) * 0
    out.loc[~kind] = eink_st_abzuege_params["sonderausgabenpauschbetrag"]
    return out


def _sonderausgaben_ab_2012(
    betreuungskost_m, tu_id, kind, _anz_erwachsene_tu, eink_st_abzuege_params
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
    _anz_erwachsene_tu

    Returns
    -------

    """
    erwachsene_in_tu = tu_id.replace(_anz_erwachsene_tu)
    abziehbare_betreuungskosten = (12 * betreuungskost_m).clip(
        upper=eink_st_abzuege_params["kinderbetreuungskosten_abz_maximum"]
    )

    berechtigte_kinder = kind.groupby(tu_id).transform(sum)
    out = (
        berechtigte_kinder
        * abziehbare_betreuungskosten
        * eink_st_abzuege_params["kinderbetreuungskosten_abz_anteil"]
    ) / erwachsene_in_tu

    out.loc[kind] = 0
    return out


def _altervorsorge_aufwend(
    kind, rentenv_beitr_m, prv_rente_beitr_m, eink_st_abzuege_params
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
    rentenv_beitr_m
    prv_rente_beitr_m
    eink_st_abzuege_params

    Returns
    -------

    """
    einführungsfaktor = 0.6 + 0.02 * (
        min(eink_st_abzuege_params["datum"].year, 2025) - 2005
    )
    out = (
        (
            einführungsfaktor * (2 * rentenv_beitr_m + prv_rente_beitr_m)
            - rentenv_beitr_m
        )
        * 12
    ).clip(upper=eink_st_abzuege_params["vorsorge_altersaufw_max"])
    out.loc[kind] = 0
    return out


def kinderfreib_tu(
    anz_kindergeld_kinder_tu, _anz_erwachsene_tu, eink_st_abzuege_params
):
    """Sum over all child allowances.

    Parameters
    ----------
    anz_kindergeld_kinder_tu
    eink_st_abzuege_params

    Returns
    -------

    """
    kifreib_total = sum(eink_st_abzuege_params["kinderfreibetrag"].values())
    return kifreib_total * anz_kindergeld_kinder_tu * _anz_erwachsene_tu


def anz_kindergeld_kinder_tu(tu_id, kindergeld_anspruch):
    """Count number of children eligible for Child Benefit.

    Parameters
    ----------
    tu_id
    kindergeld_anspruch

    Returns
    -------

    """
    return kindergeld_anspruch.groupby(tu_id).sum()
