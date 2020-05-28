import numpy as np


def ges_krankenv_beitr_m(
    _geringfügig_beschäftigt,
    ges_krankenv_beitr_rente,
    ges_krankenv_beitr_selbst,
    krankenv_beitr_regulär_beschäftigt,
    an_beitr_krankenv_midi_job,
):
    """ Contribution for each individual to the public health insurance.

    Parameters
    ----------
    _geringfügig_beschäftigt
    ges_krankenv_beitr_rente
    ges_krankenv_beitr_selbst
    krankenv_beitr_regulär_beschäftigt
    an_beitr_krankenv_midi_job

    Returns
    -------

    """

    out = _geringfügig_beschäftigt.astype(float) * np.nan

    out.loc[_geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_krankenv_midi_job.index] = an_beitr_krankenv_midi_job
    out.loc[
        krankenv_beitr_regulär_beschäftigt.index
    ] = krankenv_beitr_regulär_beschäftigt
    out.loc[ges_krankenv_beitr_selbst.index] = ges_krankenv_beitr_selbst

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente


def ges_krankenv_beitr_m_tu(ges_krankenv_beitr_m, tu_id):
    """Contribution for each tax unit to the public health insurance.

    Parameters
    ----------
    ges_krankenv_beitr_m
    tu_id

    Returns
    -------

    """
    return ges_krankenv_beitr_m.groupby(tu_id).sum()


def pflegev_beitr_m(
    _geringfügig_beschäftigt,
    pflegev_beitr_rente,
    pflegev_beitr_selbst,
    pflegev_beitr__regulär_beschäftigt,
    an_beitr_pflegev_midi_job,
):
    """Contribution for each individual to the public care insurance.

    Parameters
    ----------
    _geringfügig_beschäftigt
    pflegev_beitr_rente
    pflegev_beitr_selbst
    pflegev_beitr__regulär_beschäftigt
    an_beitr_pflegev_midi_job

    Returns
    -------

    """
    out = _geringfügig_beschäftigt.astype(float) * np.nan

    out.loc[_geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_pflegev_midi_job.index] = an_beitr_pflegev_midi_job
    out.loc[
        pflegev_beitr__regulär_beschäftigt.index
    ] = pflegev_beitr__regulär_beschäftigt
    out.loc[pflegev_beitr_selbst.index] = pflegev_beitr_selbst

    # Add the care insurance contribution for pensions
    return out + pflegev_beitr_rente


def krankenv_beitr_regulär_beschäftigt(
    lohn_krankenv__regulär_beschäftigt, soz_vers_beitr_params
):
    """Calculates health insurance contributions for regualr jobs


    Parameters
    ----------
    lohn_krankenv__regulär_beschäftigt : pd.Series
                                      Wage subject to health and care insurance
    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * lohn_krankenv__regulär_beschäftigt
    )


def pflegev_beitr__regulär_beschäftigt(
    pflegev_zusatz_kinderlos, lohn_krankenv__regulär_beschäftigt, soz_vers_beitr_params
):
    """Calculates care insurance contributions for regular jobs.


    Parameters
    ----------
    pflegev_zusatz_kinderlos : pd.Series
                               Pandas Series indicating addtional care insurance
                               contribution for childless individuals.

    lohn_krankenv__regulär_beschäftigt : pd.Series
                                      Wage subject to health and care insurance
    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly care insurance contributions for self employed
    income.

    """
    out = (
        lohn_krankenv__regulär_beschäftigt
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )

    zusatz_kinderlos = (
        lohn_krankenv__regulär_beschäftigt.loc[pflegev_zusatz_kinderlos]
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
    )

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos
    return out


def lohn_krankenv__regulär_beschäftigt(
    bruttolohn_m, krankenv_beitr_bemess_grenze, _regulär_beschäftigt
):
    """Calculate the wage, which is subject to pension insurance contributions.


    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    _regulär_beschäftigt : pd.Series
                          Boolean Series indicating regular employment.
    krankenv_beitr_bemess_grenze : pd.Series
                                 Threshold for wage subject to health insurance
                                 contributions.


    Returns
    -------

    """
    bruttolohn_m__regulär_beschäftigt = bruttolohn_m.loc[_regulär_beschäftigt]
    bemess_grenze = krankenv_beitr_bemess_grenze.loc[_regulär_beschäftigt]
    return bruttolohn_m__regulär_beschäftigt.clip(upper=bemess_grenze)


def ges_krankenv_beitr_selbst(krankenv_pflichtig_eink_selbst, soz_vers_beitr_params):
    """Calculates health insurance contributions.
    Self-employed pay the full
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
    return krankenv_pflichtig_eink_selbst * beitr_satz


def pflegev_beitr_selbst(
    pflegev_zusatz_kinderlos, krankenv_pflichtig_eink_selbst, soz_vers_beitr_params
):
    """Calculates care insurance contributions.

    Self-employed pay the full
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
    out = (
        krankenv_pflichtig_eink_selbst
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )

    zusatz_kinderlos = (
        krankenv_pflichtig_eink_selbst.loc[pflegev_zusatz_kinderlos]
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
    )

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos
    return out


def bezugsgröße(wohnort_ost, soz_vers_beitr_params):
    """Threshold for self employment income subject to health insurance.

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
    return wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["bezugsgröße"]["ost"],
            False: soz_vers_beitr_params["bezugsgröße"]["west"],
        }
    ).astype(float)


def krankenv_pflichtig_eink_selbst(
    eink_selbst_m, bezugsgröße, selbsständig_ges_krankenv
):
    """Choose the amount selfemployed income which is subject to health insurance
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
    dreiviertel_bezugsgröße = bezugsgröße_selbstv * 0.75
    return eink_selbst_m_selbstv.clip(upper=dreiviertel_bezugsgröße)


def krankenv_pflichtig_rente(ges_rente_m, krankenv_beitr_bemess_grenze):
    """Choose the amount pension which is subject to health insurance contribution.

    Parameters
    ----------
    ges_rente_m : pd.Series
                  Pensions an individual recieves.

    krankenv_beitr_bemess_grenze : pd.Series
                                   Threshold for income subcect to health insurance.


    Returns
    -------

    """
    return ges_rente_m.clip(upper=krankenv_beitr_bemess_grenze)


def krankenv_beitr_bemess_grenze(wohnort_ost, soz_vers_beitr_params):
    """Calculating the income threshold up to which the rate of health insurance
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
    return wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["beitr_bemess_grenze"]["ges_krankenv"]["ost"],
            False: soz_vers_beitr_params["beitr_bemess_grenze"]["ges_krankenv"]["west"],
        }
    )


def pflegev_beitr_rente(
    pflegev_zusatz_kinderlos, krankenv_pflichtig_rente, soz_vers_beitr_params
):
    """Calculating the contribution to health insurance for pension income.


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
    out = (
        krankenv_pflichtig_rente
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )
    zusatz_kinderlos = (
        krankenv_pflichtig_rente.loc[pflegev_zusatz_kinderlos]
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
    )

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos
    return out


def ges_krankenv_beitr_rente(krankenv_pflichtig_rente, soz_vers_beitr_params):
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    krankenv_pflichtig_rente : pd.Series
                           Pensions which are subject to social insurance contributions

    soz_vers_beitr_params

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for pension income.
    """

    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * krankenv_pflichtig_rente
    )


def ges_beitr_krankenv_midi_job(_midi_job_bemessungsentgelt, soz_vers_beitr_params):
    """Calculating the sum of employee and employer health insurance contribution.


    Parameters
    ----------
    _midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    ) * _midi_job_bemessungsentgelt


def ag_beitr_krankenv_midi_job(bruttolohn_m, _in_gleitzone, soz_vers_beitr_params):
    """Calculating the employer health insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    _in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[_in_gleitzone]
    return (
        bruttolohn_m__in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )


def an_beitr_pflegev_midi_job(ges_beitr_pflegev_midi_job, ag_beitr_pflegev_midi_job):
    """Calculating the employer care insurance contribution.


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
    return ges_beitr_pflegev_midi_job - ag_beitr_pflegev_midi_job


def an_beitr_krankenv_midi_job(ges_beitr_krankenv_midi_job, ag_beitr_krankenv_midi_job):
    """Calculating the employer health insurance contribution.


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
    return ges_beitr_krankenv_midi_job - ag_beitr_krankenv_midi_job


def ag_beitr_pflegev_midi_job(bruttolohn_m, _in_gleitzone, soz_vers_beitr_params):
    """
    Calculating the employer care insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    _in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[_in_gleitzone]
    return (
        bruttolohn_m__in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )


def ges_beitr_pflegev_midi_job(
    pflegev_zusatz_kinderlos, _midi_job_bemessungsentgelt, soz_vers_beitr_params
):
    """Calculating the sum of employee and employer care insurance contribution.


    Parameters
    ----------
    pflegev_zusatz_kinderlos : pd.Series
                               Pandas Series indicating addtional care insurance
                               contribution for childless individuals.

    _midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = (
        _midi_job_bemessungsentgelt
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )

    zusatz_kinderlos = (
        _midi_job_bemessungsentgelt.loc[pflegev_zusatz_kinderlos]
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
    )

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos

    return out


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
