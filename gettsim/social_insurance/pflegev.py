import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def pflegev_zusatz_kinderlos(hat_kinder: BoolSeries, alter: IntSeries) -> BoolSeries:
    """
    Create boolean Series indicating addtional care insurance contribution for
    childless individuals.

    Parameters
    ----------
    hat_kinder
        See basic input variable :ref:`hat_kinder <hat_kinder>`.
    alter
        See basic input variable :ref:`alter <alter>`.

    Returns
    -------

    """
    # Todo: No hardcoded 22.
    return ~hat_kinder & alter.gt(22)


def pflegev_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    pflegev_beitr_rente: FloatSeries,
    pflegev_beitr_selbst: FloatSeries,
    pflegev_beitr_reg_beschäftigt: FloatSeries,
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
    pflegev_beitr_reg_beschäftigt
        See :func:`pflegev_beitr_reg_beschäftigt`.
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
    out.loc[pflegev_beitr_reg_beschäftigt.index] = pflegev_beitr_reg_beschäftigt
    out.loc[pflegev_beitr_selbst.index] = pflegev_beitr_selbst

    # Add the care insurance contribution for pensions
    return out + pflegev_beitr_rente


def pflegev_beitr_reg_beschäftigt(
    pflegev_zusatz_kinderlos: BoolSeries,
    bruttolohn_krankenv_beitr_m: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculates care insurance contributions for regular jobs.


    Parameters
    ----------
    pflegev_zusatz_kinderlos
        See :func:`pflegev_zusatz_kinderlos`.
    bruttolohn_krankenv_beitr_m
        See :func:`bruttolohn_krankenv_beitr_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly care insurance contributions for self employed
    income.

    """
    out = (
        bruttolohn_krankenv_beitr_m
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )

    zusatz_kinderlos = (
        bruttolohn_krankenv_beitr_m.loc[pflegev_zusatz_kinderlos]
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
    )

    out.loc[pflegev_zusatz_kinderlos] += zusatz_kinderlos
    return out


def pflegev_beitr_selbst(
    pflegev_zusatz_kinderlos: BoolSeries,
    krankenv_pflichtig_eink_selbst: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
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
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

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


def pflegev_beitr_rente(
    pflegev_zusatz_kinderlos: BoolSeries,
    krankenv_pflichtig_rente: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    pflegev_zusatz_kinderlos
        See :func:`pflegev_zusatz_kinderlos`.
    krankenv_pflichtig_rente
        See :func:`krankenv_pflichtig_rente`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

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


def an_beitr_pflegev_midi_job(
    ges_beitr_pflegev_midi_job: FloatSeries, ag_beitr_pflegev_midi_job: FloatSeries
) -> FloatSeries:
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


def ag_beitr_pflegev_midi_job(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """
    Calculating the employer care insurance contribution.

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
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    return (
        bruttolohn_m_in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
    )


def ges_beitr_pflegev_midi_job(
    pflegev_zusatz_kinderlos: BoolSeries,
    midi_job_bemessungsentgelt: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculating the sum of employee and employer care insurance contribution.


    Parameters
    ----------
    pflegev_zusatz_kinderlos
        See :func:`pflegev_zusatz_kinderlos`.
    midi_job_bemessungsentgelt
        See :func:`midi_job_bemessungsentgelt`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

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
