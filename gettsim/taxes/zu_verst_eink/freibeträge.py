import numpy as np
import pandas as pd


def behinderungsgrad_pauschalbetrag(behinderungsgrad, eink_st_abzuege_params):
    """Calculate the different deductions for different handicap degrees.

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

    return pd.Series(data=out, index=behinderungsgrad.index)


def _hh_freib_bis_2014(alleinerziehend, eink_st_abzuege_params):
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
    out = alleinerziehend.astype(float) * 0
    out.loc[alleinerziehend] = eink_st_abzuege_params["alleinerziehenden_freibetrag"]
    return out


def _hh_freib_seit_2015(alleinerziehend, _anz_kinder_in_tu, eink_st_abzuege_params):
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
    out = alleinerziehend.astype(float) * 0
    out.loc[alleinerziehend] = (
        eink_st_abzuege_params["alleinerziehenden_freibetrag"]
        + _anz_kinder_in_tu.loc[alleinerziehend]
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
    out = bruttolohn_m * 0
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
    out = kind.astype(float) * 0
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
    abziehbare_betreuungskosten = (12 * betreuungskost_m).clip(
        upper=eink_st_abzuege_params["kinderbetreuungskosten_abz_maximum"]
    )

    berechtigte_kinder = kind.groupby(tu_id).transform(sum)
    out = (
        berechtigte_kinder
        * abziehbare_betreuungskosten
        * eink_st_abzuege_params["kinderbetreuungskosten_abz_anteil"]
    ) / anz_erwachsene_in_tu

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
    einführungsfaktor = 0.6 + 0.02 * (min(eink_st_abzuege_params["jahr"], 2025) - 2005)
    out = (
        (
            einführungsfaktor * (2 * rentenv_beitr_m + prv_rente_beitr_m)
            - rentenv_beitr_m
        )
        * 12
    ).clip(upper=eink_st_abzuege_params["vorsorge_altersaufw_max"])
    out.loc[kind] = 0
    return out


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
