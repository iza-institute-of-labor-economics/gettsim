import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def ges_krankenv_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    ges_krankenv_beitr_rente: FloatSeries,
    ges_krankenv_beitr_selbst: FloatSeries,
    krankenv_beitr_regulär_beschäftigt: FloatSeries,
    an_beitr_krankenv_midi_job: FloatSeries,
) -> FloatSeries:
    """ Contribution for each individual to the public health insurance.

    Parameters
    ----------
    geringfügig_beschäftigt 
        See :func:`geringfügig_beschäftigt`.
    ges_krankenv_beitr_rente 
        See :func:`ges_krankenv_beitr_rente`.
    ges_krankenv_beitr_selbst 
        See :func:`ges_krankenv_beitr_selbst`.
    krankenv_beitr_regulär_beschäftigt 
        See :func:`krankenv_beitr_regulär_beschäftigt`.
    an_beitr_krankenv_midi_job 
        See :func:`an_beitr_krankenv_midi_job`.

    Returns
    -------

    """

    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_krankenv_midi_job.index] = an_beitr_krankenv_midi_job
    out.loc[
        krankenv_beitr_regulär_beschäftigt.index
    ] = krankenv_beitr_regulär_beschäftigt
    out.loc[ges_krankenv_beitr_selbst.index] = ges_krankenv_beitr_selbst

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente


def ges_krankenv_beitr_m_tu(ges_krankenv_beitr_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Contribution for each tax unit to the public health insurance.

    Parameters
    ----------
    ges_krankenv_beitr_m 
        See :func:`ges_krankenv_beitr_m`.
    tu_id
        See :ref:`tu_id`.

    Returns
    -------

    """
    return ges_krankenv_beitr_m.groupby(tu_id).sum()


def pflegev_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    pflegev_beitr_rente: FloatSeries,
    pflegev_beitr_selbst: FloatSeries,
    pflegev_beitr_regulär_beschäftigt: FloatSeries,
    an_beitr_pflegev_midi_job: FloatSeries,
) -> FloatSeries:
    """Contribution for each individual to the public care insurance.

    Parameters
    ----------
    geringfügig_beschäftigt 
        See :func:`geringfügig_beschäftigt`.
    pflegev_beitr_rente 
        See :func:`pflegev_beitr_rente`.
    pflegev_beitr_selbst 
        See :func:`pflegev_beitr_selbst`.
    pflegev_beitr_regulär_beschäftigt 
        See :func:`pflegev_beitr_regulär_beschäftigt`.
    an_beitr_pflegev_midi_job 
        See :func:`an_beitr_pflegev_midi_job`.

    Returns
    -------

    """
    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_pflegev_midi_job.index] = an_beitr_pflegev_midi_job
    out.loc[pflegev_beitr_regulär_beschäftigt.index] = pflegev_beitr_regulär_beschäftigt
    out.loc[pflegev_beitr_selbst.index] = pflegev_beitr_selbst

    # Add the care insurance contribution for pensions
    return out + pflegev_beitr_rente


def krankenv_beitr_regulär_beschäftigt(
    lohn_krankenv_regulär_beschäftigt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for regualr jobs


    Parameters
    ----------
    lohn_krankenv_regulär_beschäftigt 
        See :func:`lohn_krankenv_regulär_beschäftigt`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * lohn_krankenv_regulär_beschäftigt
    )


def pflegev_beitr_regulär_beschäftigt(
    pflegev_zusatz_kinderlos: FloatSeries, lohn_krankenv_regulär_beschäftigt: 
        FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates care insurance contributions for regular jobs.


    Parameters
    ----------
    pflegev_zusatz_kinderlos 
        See :func:`pflegev_zusatz_kinderlos`.
    lohn_krankenv_regulär_beschäftigt
        See :func:`lohn_krankenv_regulär_beschäftigt`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------
    Pandas Series containing monthly care insurance contributions for self employed
    income.

    """
    out = (
        lohn_krankenv_regulär_beschäftigt
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )

    zusatz_kinderlos = (
        lohn_krankenv_regulär_beschäftigt.loc[pflegev_zusatz_kinderlos]
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
    )

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos
    return out


def lohn_krankenv_regulär_beschäftigt(
    bruttolohn_m: FloatSeries, krankenv_beitr_bemess_grenze: FloatSeries, 
    regulär_beschäftigt: BoolSeries
) -> FloatSeries:
    """Calculate the wage, which is subject to pension insurance contributions.


    Parameters
    ----------
    bruttolohn_m 
        See :func:`bruttolohn_m`.
    regulär_beschäftigt
        See :func:`regulär_beschäftigt`.
    krankenv_beitr_bemess_grenze 
        See :func:`krankenv_beitr_bemess_grenze`.


    Returns
    -------

    """
    bruttolohn_m_regulär_beschäftigt = bruttolohn_m.loc[regulär_beschäftigt]
    bemess_grenze = krankenv_beitr_bemess_grenze.loc[regulär_beschäftigt]
    return bruttolohn_m_regulär_beschäftigt.clip(upper=bemess_grenze)


def ges_krankenv_beitr_selbst(krankenv_pflichtig_eink_selbst: FloatSeries, 
                              soz_vers_beitr_params: dict) -> FloatSeries:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    krankenv_pflichtig_eink_selbst 
        See :func:`krankenv_pflichtig_eink_selbst`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

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
    pflegev_zusatz_kinderlos: FloatSeries, 
    krankenv_pflichtig_eink_selbst: FloatSeries, soz_vers_beitr_params: dict
):
    """Calculates care insurance contributions.

    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------
    pflegev_zusatz_kinderlos
        See :func:`pflegev_zusatz_kinderlos`.
        
    krankenv_pflichtig_eink_selbst 
        See :func:`krankenv_pflichtig_eink_selbst`.
    
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

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


def bezugsgröße(wohnort_ost: BoolSeries, soz_vers_beitr_params: dict) -> FloatSeries:
    """Threshold for self employment income subject to health insurance.

    Selecting by place of living the income threshold for self employed up to which the
    rate of health insurance contributions apply.

    Parameters
    ----------
    wohnort_ost
        See :func:`wohnort_ost`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

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
    eink_selbst_m: FloatSeries, bezugsgröße: FloatSeries, selbstständig_ges_krankenv: FloatSeries
) -> FloatSeries:
    """Choose the amount selfemployed income which is subject to health insurance
    contribution.

    Parameters
    ----------
    eink_selbst_m
        See :func:`eink_selbst_m`.
    bezugsgröße 
        See :func:`bezugsgröße`.
    selbstständig_ges_krankenv 
        See :func:`selbstständig_ges_krankenv`.
    
    Returns
    -------

    """
    bezugsgröße_selbstv = bezugsgröße.loc[selbstständig_ges_krankenv]
    eink_selbst_m_selbstv = eink_selbst_m.loc[selbstständig_ges_krankenv]
    dreiviertel_bezugsgröße = bezugsgröße_selbstv * 0.75
    return eink_selbst_m_selbstv.clip(upper=dreiviertel_bezugsgröße)


def krankenv_pflichtig_rente(ges_rente_m: FloatSeries, 
                             krankenv_beitr_bemess_grenze: FloatSeries) -> FloatSeries:
    """Choose the amount pension which is subject to health insurance contribution.

    Parameters
    ----------
    ges_rente_m 
        See :func:`ges_rente_m`.
    krankenv_beitr_bemess_grenze 
        See :func:`krankenv_beitr_bemess_grenze`.

    Returns
    -------

    """
    return ges_rente_m.clip(upper=krankenv_beitr_bemess_grenze)


def krankenv_beitr_bemess_grenze(wohnort_ost: BoolSeries, 
                                 soz_vers_beitr_params: dict) -> FloatSeries:
    """Calculating the income threshold up to which the rate of health insurance
    contributions apply.

    Parameters
    ----------
    wohnort_ost
        See :func:`wohnort_ost`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

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
    pflegev_zusatz_kinderlos: FloatSeries, krankenv_pflichtig_rente: FloatSeries, 
    soz_vers_beitr_params: dict) -> FloatSeries:
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    pflegev_zusatz_kinderlos
        See :func:`pflegev_zusatz_kinderlos`.
    krankenv_pflichtig_rente
        See :func:`krankenv_pflichtig_rente`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

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


def ges_krankenv_beitr_rente(krankenv_pflichtig_rente: FloatSeries, 
                             soz_vers_beitr_params: dict) -> FloatSeries:
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    krankenv_pflichtig_rente
        See :func:`krankenv_pflichtig_rente`.    
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for pension income.
    """

    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * krankenv_pflichtig_rente
    )


def ges_beitr_krankenv_midi_job(midi_job_bemessungsentgelt: FloatSeries, 
                                soz_vers_beitr_params: dict) -> FloatSeries:
    """Calculating the sum of employee and employer health insurance contribution.


    Parameters
    ----------
    midi_job_bemessungsentgelt
        See :func:`midi_job_bemessungsentgelt`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------

    """
    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    ) * midi_job_bemessungsentgelt


def ag_beitr_krankenv_midi_job(bruttolohn_m: FloatSeries, 
                               in_gleitzone: BoolSeries, 
                               soz_vers_beitr_params: dict) -> FloatSeries:
    """Calculating the employer health insurance contribution.

    Parameters
    ----------
    bruttolohn_m 
        See :func:`bruttolohn_m`.
    in_gleitzone 
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    return (
        bruttolohn_m__in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )


def an_beitr_pflegev_midi_job(ges_beitr_pflegev_midi_job: FloatSeries, 
                              ag_beitr_pflegev_midi_job: FloatSeries) -> FloatSeries:
    """Calculating the employer care insurance contribution.


    Parameters
    ----------
    ges_beitr_pflegev_midi_job
        See :func:`ges_beitr_pflegev_midi_job`.
    ag_beitr_pflegev_midi_job 
        See :func:`ag_beitr_pflegev_midi_job`. 
        
    Returns
    -------

    """
    return ges_beitr_pflegev_midi_job - ag_beitr_pflegev_midi_job


def an_beitr_krankenv_midi_job(ges_beitr_krankenv_midi_job: FloatSeries, 
                               ag_beitr_krankenv_midi_job: FloatSeries) -> FloatSeries:
    """Calculating the employer health insurance contribution.


    Parameters
    ----------
    ges_beitr_krankenv_midi_job
        See :func:`ges_beitr_krankenv_midi_job`.
    ag_beitr_krankenv_midi_job
        See :func:`ag_beitr_krankenv_midi_job`.
    Returns
    -------

    """
    return ges_beitr_krankenv_midi_job - ag_beitr_krankenv_midi_job


def ag_beitr_pflegev_midi_job(bruttolohn_m: FloatSeries, 
                              in_gleitzone: BoolSeries, 
                              soz_vers_beitr_params: dict) -> FloatSeries:
    """
    Calculating the employer care insurance contribution.

    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    in_gleitzone
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    return (
        bruttolohn_m__in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )


def ges_beitr_pflegev_midi_job(
    pflegev_zusatz_kinderlos: FloatSeries, 
    midi_job_bemessungsentgelt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the sum of employee and employer care insurance contribution.


    Parameters
    ----------
    pflegev_zusatz_kinderlos 
        See :func:`pflegev_zusatz_kinderlos`.
    midi_job_bemessungsentgelt
        See :func:`midi_job_bemessungsentgelt`.
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------

    """
    out = (
        midi_job_bemessungsentgelt
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )

    zusatz_kinderlos = (
        midi_job_bemessungsentgelt.loc[pflegev_zusatz_kinderlos]
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
    )

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos

    return out


def selbstständig_ges_krankenv(selbstständig: BoolSeries, 
                               prv_krankenv: BoolSeries) -> BoolSeries:
    """
    Create boolean Series indicating selfemployed insures via public health insurance.

    Parameters
    ----------
    selbstständig 
        See :ref:`prv_krankenv`.
    prv_krankenv 
        See :ref:`prv_krankenv`.

    Returns
    -------

    """
    return selbstständig & ~prv_krankenv


def pflegev_zusatz_kinderlos(hat_kinder: BoolSeries, alter: IntSeries) -> BoolSeries: 
    """
    Create boolean Series indicating addtional care insurance contribution for
    childless individuals.

    Parameters
    ----------
    hat_kinder 
        See :ref:`hat_kinder`.
    alter 
        See :ref:`alter`. 
        
    Returns
    -------

    """
    # Todo: No hardcoded 22.
    return ~hat_kinder & alter.gt(22)
