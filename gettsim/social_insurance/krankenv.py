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


def ges_krankenv_beitr_m_tu(
    ges_krankenv_beitr_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Contribution for each tax unit to the public health insurance.

    Parameters
    ----------
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return ges_krankenv_beitr_m.groupby(tu_id).sum()


def krankenv_beitr_regulär_beschäftigt(
    lohn_krankenv_regulär_beschäftigt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for regualr jobs


    Parameters
    ----------
    lohn_krankenv_regulär_beschäftigt
        See :func:`lohn_krankenv_regulär_beschäftigt`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * lohn_krankenv_regulär_beschäftigt
    )


def lohn_krankenv_regulär_beschäftigt(
    bruttolohn_m: FloatSeries,
    krankenv_beitr_bemess_grenze: FloatSeries,
    regulär_beschäftigt: BoolSeries,
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


def ges_krankenv_beitr_selbst(
    krankenv_pflichtig_eink_selbst: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    krankenv_pflichtig_eink_selbst
        See :func:`krankenv_pflichtig_eink_selbst`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

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


def krankenv_pflichtig_eink_selbst(
    eink_selbst_m: FloatSeries,
    bezugsgröße: FloatSeries,
    selbstständig_ges_krankenv: BoolSeries,
) -> FloatSeries:
    """Choose the amount selfemployed income which is subject to health insurance
    contribution.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
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


def krankenv_pflichtig_rente(
    ges_rente_m: FloatSeries, krankenv_beitr_bemess_grenze: FloatSeries
) -> FloatSeries:
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


def ges_krankenv_beitr_rente(
    krankenv_pflichtig_rente: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    krankenv_pflichtig_rente
        See :func:`krankenv_pflichtig_rente`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for pension income.
    """

    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * krankenv_pflichtig_rente
    )


def ges_beitr_krankenv_midi_job(
    midi_job_bemessungsentgelt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the sum of employee and employer health insurance contribution.


    Parameters
    ----------
    midi_job_bemessungsentgelt
        See :func:`midi_job_bemessungsentgelt`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    ) * midi_job_bemessungsentgelt


def ag_beitr_krankenv_midi_job(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the employer health insurance contribution.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    return (
        bruttolohn_m__in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )


def an_beitr_krankenv_midi_job(
    ges_beitr_krankenv_midi_job: FloatSeries, ag_beitr_krankenv_midi_job: FloatSeries
) -> FloatSeries:
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


def selbstständig_ges_krankenv(
    selbstständig: BoolSeries, prv_krankenv: BoolSeries
) -> BoolSeries:
    """
    Create boolean Series indicating selfemployed insures via public health insurance.

    Parameters
    ----------
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    prv_krankenv
        See basic input variable :ref:`prv_krankenv <prv_krankenv>`.

    Returns
    -------

    """
    return selbstständig & ~prv_krankenv
