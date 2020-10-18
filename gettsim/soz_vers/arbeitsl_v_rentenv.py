"""Functions for modeling unemployment and pension insurance."""
import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def sozialv_beitr_m(
    pflegev_beitr_m: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    rentenv_beitr_m: FloatSeries,
    arbeitsl_v_beitr_m: FloatSeries,
) -> FloatSeries:
    """Sum of all social insurance contributions.


    Parameters
    ----------
    pflegev_beitr_m
        See :func:`pflegev_beitr_m`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    rentenv_beitr_m
        See :func:`rentenv_beitr_m`.
    arbeitsl_v_beitr_m
        See :func:`arbeitsl_v_beitr_m`.

    Returns
    -------

    """
    return pflegev_beitr_m + ges_krankenv_beitr_m + rentenv_beitr_m + arbeitsl_v_beitr_m


def rentenv_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    rentenv_beitr_regular_job: FloatSeries,
    an_beitr_rentenv_midi_job: FloatSeries,
) -> FloatSeries:
    """Contribution for each individual to the pension insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    rentenv_beitr_regular_job
        See :func:`rentenv_beitr_regular_job`.

    an_beitr_rentenv_midi_job
        See :func:`an_beitr_rentenv_midi_job`.


    Returns
    -------

    """

    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_rentenv_midi_job.index] = an_beitr_rentenv_midi_job
    out.loc[rentenv_beitr_regular_job.index] = rentenv_beitr_regular_job

    return out


def rentenv_beitr_m_tu(rentenv_beitr_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Calculate the contribution of each tax unit to the pension insurance.

    Parameters
    ----------
    rentenv_beitr_m
        See :func:`rentenv_beitr_m`.

    tu_id
        See :ref:`tu_id`.

    Returns
    -------

    """
    return rentenv_beitr_m.groupby(tu_id).sum()


def arbeitsl_v_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    an_beitr_arbeitsl_v_midi_job: FloatSeries,
    arbeitsl_v_regular_job: FloatSeries,
) -> FloatSeries:
    """Calculate the contribution for each individual to the unemployment insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    an_beitr_arbeitsl_v_midi_job
        See :func:`an_beitr_arbeitsl_v_midi_job`.

    arbeitsl_v_regular_job
        See :func:`arbeitsl_v_regular_job`.

    Returns
    -------

    """
    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions, for minijobs it remains 0
    out.loc[an_beitr_arbeitsl_v_midi_job.index] = an_beitr_arbeitsl_v_midi_job
    out.loc[arbeitsl_v_regular_job.index] = arbeitsl_v_regular_job

    return out


def arbeitsl_v_regular_job(
    ges_beitr_arbeitsl_v_midi_jobreturn: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates unemployment insurance contributions for regualr jobs.

    Parameters
    ----------
    ges_beitr_arbeitsl_v_midi_jobreturn
        See :func:`ges_beitr_arbeitsl_v_midi_jobreturn`.

    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------

    """
    return (
        ges_beitr_arbeitsl_v_midi_jobreturn
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def rentenv_beitr_regular_job(
    ges_beitr_arbeitsl_v_midi_jobreturn: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates pension insurance contributions for regular jobs.

    Parameters
    ----------
    ges_beitr_arbeitsl_v_midi_jobreturn
        See :func:`ges_beitr_arbeitsl_v_midi_jobreturn`.

    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------

    """
    return (
        ges_beitr_arbeitsl_v_midi_jobreturn
        * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )


def ges_beitr_arbeitsl_v_midi_jobreturn(
    bruttolohn_m: FloatSeries,
    rentenv_beitr_bemess_grenze: FloatSeries,
    regulär_beschäftigt: BoolSeries,
) -> FloatSeries:
    """Calculate the wage, which is subject to pension insurance contributions.

    Parameters
    ----------
    bruttolohn_m
        See :ref:`soz_vers_beitr_params`.

    regulär_beschäftigt
        See :func:`regulär_beschäftigt`.

    rentenv_beitr_bemess_grenze
        See :func:`rentenv_beitr_bemess_grenze`.


    Returns
    -------

    """
    bruttolohn_m_regulär_beschäftigt = bruttolohn_m.loc[regulär_beschäftigt]
    bemess_grenze = rentenv_beitr_bemess_grenze.loc[regulär_beschäftigt]
    return bruttolohn_m_regulär_beschäftigt.clip(upper=bemess_grenze)


def rentenv_beitr_bemess_grenze(
    wohnort_ost: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """

    Parameters
    ----------
    wohnort_ost
    soz_vers_beitr_params

    Returns
    -------

    """
    out = wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["ost"],
            False: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["west"],
        }
    )
    return out


def ges_beitr_arbeitsl_v_midi_job(
    midi_job_bemessungsentgelt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the sum of employee and employer unemployment insurance contribution.

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
        midi_job_bemessungsentgelt
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def ges_beitr_rentenv_midi_job(
    midi_job_bemessungsentgelt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the sum of employee and employer pension insurance contribution.

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
        midi_job_bemessungsentgelt
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )


def ag_beitr_rentenv_midi_job(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the employer pension insurance contribution.

    Parameters
    ----------
    bruttolohn_m
        See :ref:`bruttolohn_m`.

    in_gleitzone
        See :func:`in_gleitzone`.

    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    out = (
        bruttolohn_m__in_gleitzone * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )
    return out


def ag_beitr_arbeitsl_v_midi_job(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    bruttolohn_m
        See :ref:`bruttolohn_m`.

    in_gleitzone
        See :func:`in_gleitzone`.

    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.

    Returns
    -------

    """
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    return (
        bruttolohn_m_in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def an_beitr_rentenv_midi_job(
    ges_beitr_rentenv_midi_job: FloatSeries, ag_beitr_rentenv_midi_job: FloatSeries
) -> FloatSeries:
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    ges_beitr_rentenv_midi_job
        See :func:`ges_beitr_rentenv_midi_job`.

    ag_beitr_rentenv_midi_job
        See :func:`ag_beitr_rentenv_midi_job`.

    Returns
    -------

    """
    return ges_beitr_rentenv_midi_job - ag_beitr_rentenv_midi_job


def an_beitr_arbeitsl_v_midi_job(
    ges_beitr_arbeitsl_v_midi_job: FloatSeries,
    ag_beitr_arbeitsl_v_midi_job: FloatSeries,
) -> FloatSeries:
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    ges_beitr_arbeitsl_v_midi_job
        See :func:`ges_beitr_arbeitsl_v_midi_job`.

    ag_beitr_arbeitsl_v_midi_job
        See :func:`ag_beitr_arbeitsl_v_midi_job`.

    Returns
    -------

    """
    return ges_beitr_arbeitsl_v_midi_job - ag_beitr_arbeitsl_v_midi_job
