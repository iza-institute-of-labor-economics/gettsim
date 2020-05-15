import numpy as np
import pandas as pd


def ges_krankenv_beitr_m(
    geringfügig_beschäftigt,
    ges_krankenv_beitr_rente,
    ges_krankenv_beitr_selbst,
    krankenv_beitr_regulär_beschäftigt,
    an_beitr_krankenv_midi_job,
):

    ges_krankenv_beitr_m = pd.Series(
        index=geringfügig_beschäftigt.index, name="ges_krankenv_beitr_m", dtype=float
    )

    ges_krankenv_beitr_m.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    ges_krankenv_beitr_m.loc[
        an_beitr_krankenv_midi_job.index
    ] = an_beitr_krankenv_midi_job
    ges_krankenv_beitr_m.loc[
        krankenv_beitr_regulär_beschäftigt.index
    ] = krankenv_beitr_regulär_beschäftigt
    ges_krankenv_beitr_m.loc[
        ges_krankenv_beitr_selbst.index
    ] = ges_krankenv_beitr_selbst

    # Add the health insurance contribution for pensions
    ges_krankenv_beitr_m += ges_krankenv_beitr_rente
    return ges_krankenv_beitr_m


def pflegev_beitr_m(
    geringfügig_beschäftigt,
    pflegev_beitr_rente,
    pflegev_beitr_selbst,
    pflegev_beitr_regulär_beschäftigt,
    an_beitr_pflegev_midi_job,
):

    pflegev_beitr_m = pd.Series(
        index=geringfügig_beschäftigt.index, name="pflegev_beitr_m", dtype=float
    )

    pflegev_beitr_m.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    pflegev_beitr_m.loc[an_beitr_pflegev_midi_job.index] = an_beitr_pflegev_midi_job
    pflegev_beitr_m.loc[
        pflegev_beitr_regulär_beschäftigt.index
    ] = pflegev_beitr_regulär_beschäftigt
    pflegev_beitr_m.loc[pflegev_beitr_selbst.index] = pflegev_beitr_selbst

    # Add the care insurance contribution for pensions
    pflegev_beitr_m += pflegev_beitr_rente

    return pflegev_beitr_m


def krankenv_beitr_regulär_beschäftigt(
    lohn_krankenv_regulär_beschäftigt, soz_vers_beitr_params
):
    """
    Calculates health insurance contributions for regualr jobs

    Parameters
    ----------
    lohn_krankenv_regulär_beschäftigt : pd.Series
                                      Wage subject to health and care insurance
    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    out = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * lohn_krankenv_regulär_beschäftigt
    )
    return out.rename("krankenv_beitr_regulär_beschäftigt")


def pflegev_beitr_regulär_beschäftigt(
    pflegev_zusatz_kinderlos, lohn_krankenv_regulär_beschäftigt, soz_vers_beitr_params
):
    """
    Calculates care insurance contributions for regular jobs.

    Parameters
    ----------
    pflegev_zusatz_kinderlos : pd.Series
                               Pandas Series indicating addtional care insurance
                               contribution for childless individuals.

    lohn_krankenv_regulär_beschäftigt : pd.Series
                                      Wage subject to health and care insurance
    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly care insurance contributions for self employed
    income.

    """
    out = lohn_krankenv_regulär_beschäftigt.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )
    zusatz_kinderlos = lohn_krankenv_regulär_beschäftigt.loc[
        pflegev_zusatz_kinderlos
    ].multiply(soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"])

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos
    return out.rename("pflegev_beitr_regulär_beschäftigt")


def lohn_krankenv_regulär_beschäftigt(
    bruttolohn_m, krankenv_beitr_bemess_grenze, regulär_beschäftigt
):
    """
    Calculate the wage, which is subject to pension insurance contributions.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    regulär_beschäftigt : pd.Series
                          Boolean Series indicating regular employment.
    krankenv_beitr_bemess_grenze : pd.Series
                                 Threshold for wage subject to health insurance
                                 contributions.


    Returns
    -------

    """
    bruttolohn_m_regulär_beschäftigt = bruttolohn_m.loc[regulär_beschäftigt]
    bemess_grenze = krankenv_beitr_bemess_grenze.loc[regulär_beschäftigt]
    out = bruttolohn_m_regulär_beschäftigt.where(
        bruttolohn_m_regulär_beschäftigt < bemess_grenze, bemess_grenze
    )
    return out.rename("lohn_krankenv_regulär_beschäftigt")


def ges_krankenv_beitr_selbst(krankenv_pflichtig_eink_selbst, soz_vers_beitr_params):
    """
    Calculates health insurance contributions. Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    krankenv_pflichtig_eink_selbst : pd.Series
                                     Income from self employment subject to health
                                     and care insurance
    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    beitr_satz = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )
    out = krankenv_pflichtig_eink_selbst.multiply(beitr_satz)
    return out.rename("ges_krankenv_beitr_selbst")


def pflegev_beitr_selbst(
    pflegev_zusatz_kinderlos, krankenv_pflichtig_eink_selbst, soz_vers_beitr_params
):
    """
    Calculates care insurance contributions. Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------
    pflegev_zusatz_kinderlos : pd.Series
                               Pandas Series indicating addtional care insurance
                               contribution for childless individuals.

    krankenv_pflichtig_eink_selbst : pd.Series
                                     Income from self employment subject to health
                                     and care insurance
    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly care insurance contributions for self employed
    income.
    """
    out = krankenv_pflichtig_eink_selbst.multiply(
        2 * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )
    zusatz_kinderlos = krankenv_pflichtig_eink_selbst.loc[
        pflegev_zusatz_kinderlos
    ].multiply(soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"])

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos
    return out.rename("pflegev_beitr_selbst")


def bezugsgröße(wohnort_ost, soz_vers_beitr_params):
    """
    Selecting by place of living the income threshold for self employed up to which the
    rate of health insurance contributions apply.

    Parameters
    ----------
    wohnort_ost : pd.Series
                  Boolean variable indicating individual living in east germany.
    soz_vers_beitr_params

    Returns
    -------
    """
    out = np.select(
        [wohnort_ost, ~wohnort_ost],
        [
            soz_vers_beitr_params["bezugsgröße"]["ost"],
            soz_vers_beitr_params["bezugsgröße"]["west"],
        ],
    )
    return pd.Series(index=wohnort_ost.index, data=out, name="bezugsgröße")


def krankenv_pflichtig_eink_selbst(
    eink_selbst_m, bezugsgröße, selbsständig_ges_krankenv
):
    """
    Choose the amount selfemployed income which is subject to health insurance
    contribution.

    Parameters
    ----------
    eink_selbst_m : pd.Series
                    Income from selfemployment

    bezugsgröße : pd.Series
                  Threshold for income subcect to health insurance.
    selbsständig_ges_krankenv: pd.Series
                             Boolean Series indicating selfemployed and public health
                             insured.

    Returns
    -------

    """
    bezugsgröße_selbstv = bezugsgröße.loc[selbsständig_ges_krankenv]
    eink_selbst_m_selbstv = eink_selbst_m.loc[selbsständig_ges_krankenv]
    dreiviertel_bezugsgröße = bezugsgröße_selbstv.multiply(0.75)
    out = eink_selbst_m_selbstv.where(
        eink_selbst_m_selbstv < dreiviertel_bezugsgröße, dreiviertel_bezugsgröße
    )
    return out.rename("krankenv_pflichtig_eink_selbst")


def krankenv_pflichtig_rente(ges_rente_m, krankenv_beitr_bemess_grenze):
    """
    Choose the amount pension which is subject to health insurance contribution.

    Parameters
    ----------
    ges_rente_m : pd.Series
                  Pensions an individual recieves.

    krankenv_beitr_bemess_grenze : pd.Series
                                   Threshold for income subcect to health insurance.


    Returns
    -------

    """
    out = ges_rente_m.where(
        ges_rente_m < krankenv_beitr_bemess_grenze, krankenv_beitr_bemess_grenze
    )
    return out.rename("krankenv_pflichtig_rente")


def krankenv_beitr_bemess_grenze(wohnort_ost, soz_vers_beitr_params):
    """
    Calculating the income threshold up to which the rate of health insurance
    contributions apply.

    Parameters
    ----------
    wohnort_ost : pd.Series
                  Boolean variable indicating individual living in east germany.
    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing the income threshold up to which the rate of health
    insurance contributions apply.

    """
    out = np.select(
        [wohnort_ost, ~wohnort_ost],
        [
            soz_vers_beitr_params["beitr_bemess_grenze"]["ges_krankenv"]["ost"],
            soz_vers_beitr_params["beitr_bemess_grenze"]["ges_krankenv"]["west"],
        ],
    )
    return pd.Series(
        data=out, index=wohnort_ost.index, name="krankenv_beitr_bemess_grenze"
    )


def pflegev_beitr_rente(
    pflegev_zusatz_kinderlos, krankenv_pflichtig_rente, soz_vers_beitr_params
):
    """
    Calculating the contribution to health insurance for pension income.

    Parameters
    ----------
    pflegev_zusatz_kinderlos : pd.Series
                               Pandas Series indicating addtional care insurance
                               contribution for childless individuals.

    krankenv_pflichtig_rente : pd.Series
                           Pensions which are subject to social insurance contributions.
    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for pension income.
    """
    out = krankenv_pflichtig_rente.multiply(
        2 * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )
    zusatz_kinderlos = krankenv_pflichtig_rente.loc[pflegev_zusatz_kinderlos].multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
    )

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos
    return out.rename("pflegev_beitr_rente")


def ges_krankenv_beitr_rente(krankenv_pflichtig_rente, soz_vers_beitr_params):
    """
    Calculating the contribution to health insurance for pension income.

    Parameters
    ----------
    krankenv_pflichtig_rente : pd.Series
                           Pensions which are subject to social insurance contributions

    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for pension income.
    """

    out = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * krankenv_pflichtig_rente
    )
    return out.rename("ges_krankenv_beitr_rente")


def ges_beitr_krankenv_midi_job(midi_job_bemessungsentgelt, soz_vers_beitr_params):
    """
    Calculating the sum of employee and employer health insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    ) * midi_job_bemessungsentgelt
    return out.rename("ges_beitr_krankenv_midi_job")


def ag_beitr_krankenv_midi_job(bruttolohn_m, in_gleitzone, soz_vers_beitr_params):
    """
    Calculating the employer health insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params

    Returns
    -------

    """
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    out = bruttolohn_m_in_gleitzone.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )
    return out.rename("ag_beitr_krankenv_midi_job")


def an_beitr_pflegev_midi_job(ges_beitr_pflegev_midi_job, ag_beitr_pflegev_midi_job):
    """
    Calculating the employer care insurance contribution.

    Parameters
    ----------
    ges_beitr_pflegev_midi_job : pd.Series
                                    Sum of employer and employee care
                                    insurance contributions.

    ag_beitr_pflegev_midi_job : pd.Series
                                   Employer care insurance contribution.

    Returns
    -------

    """
    out = ges_beitr_pflegev_midi_job - ag_beitr_pflegev_midi_job
    return out.rename("an_beitr_pflegev_midi_job")


def an_beitr_krankenv_midi_job(ges_beitr_krankenv_midi_job, ag_beitr_krankenv_midi_job):
    """
    Calculating the employer health insurance contribution.

    Parameters
    ----------
    ges_beitr_krankenv_midi_job : pd.Series
                                    Sum of employer and employee health
                                    insurance contributions.

    ag_beitr_krankenv_midi_job : pd.Series
                               Employer health insurance contribution.

    Returns
    -------

    """
    out = ges_beitr_krankenv_midi_job - ag_beitr_krankenv_midi_job
    return out.rename("an_beitr_krankenv_midi_job")


def ag_beitr_pflegev_midi_job(bruttolohn_m, in_gleitzone, soz_vers_beitr_params):
    """
    Calculating the employer care insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params

    Returns
    -------

    """
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    out = bruttolohn_m_in_gleitzone.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )
    return out.rename("ag_beitr_pflegev_midi_job")


def ges_beitr_pflegev_midi_job(
    pflegev_zusatz_kinderlos, midi_job_bemessungsentgelt, soz_vers_beitr_params
):
    """
    Calculating the sum of employee and employer care insurance contribution.

    Parameters
    ----------
    pflegev_zusatz_kinderlos : pd.Series
                               Pandas Series indicating addtional care insurance
                               contribution for childless individuals.

    midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = midi_job_bemessungsentgelt.multiply(
        2 * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )
    zusatz_kinderlos = midi_job_bemessungsentgelt.loc[
        pflegev_zusatz_kinderlos
    ].multiply(soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"])

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos

    return out.rename("ges_beitr_pflegev_midi_job")


def selbsständig_ges_krankenv(selbstständig, prv_krankenv):
    """
    Create boolean Series indicating selfemployed insures via public health insurance.

    Parameters
    ----------
    selbstständig : pd.Series
                    Boolean Series indicating self employment.
    prv_krankenv : pd.Series
                 Boolean Series indicating private health insurance

    Returns
    -------

    """
    return selbstständig & ~prv_krankenv


def pflegev_zusatz_kinderlos(hat_kinder, alter):
    """
    Create boolean Series indicating addtional care insurance contribution for
    childless individuals.

    Parameters
    ----------
    hat_kinder : pd.Series
                 Boolean indicating if individual has kids.
    alter : pd.Series
            Age of individual

    Returns
    -------

    """
    # Todo: No hardcoded 22.
    return ~hat_kinder & alter.gt(22)
