"""Functions for modeling unemployment and pension insurance."""
import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries


def sozialv_beitr_m(
    pflegev_beitr_m: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    rentenv_beitr_m: FloatSeries,
    arbeitslv_beitr_m: FloatSeries,
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
    arbeitslv_beitr_m
        See :func:`arbeitslv_beitr_m`.

    Returns
    -------

    """
    return pflegev_beitr_m + ges_krankenv_beitr_m + rentenv_beitr_m + arbeitslv_beitr_m


def arbeitslv_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    an_beitr_arbeitslv_midi_job_m: FloatSeries,
    arbeitslv_regulär_beschäft_m: FloatSeries,
) -> FloatSeries:
    """Calculate the contribution for each individual to the unemployment insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    an_beitr_arbeitslv_midi_job_m
        See :func:`an_beitr_arbeitslv_midi_job_m`.

    arbeitslv_regulär_beschäft_m
        See :func:`arbeitslv_regulär_beschäft_m`.

    Returns
    -------

    """
    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions, for minijobs it remains 0
    out.loc[an_beitr_arbeitslv_midi_job_m.index] = an_beitr_arbeitslv_midi_job_m
    out.loc[arbeitslv_regulär_beschäft_m.index] = arbeitslv_regulär_beschäft_m

    return out


def arbeitslv_regulär_beschäft_m(
    bruttolohn_sozialv_beitr_m: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates unemployment insurance contributions for regular jobs.

    Parameters
    ----------
    bruttolohn_sozialv_beitr_m
        See :func:`bruttolohn_sozialv_beitr_m`.

    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    return (
        bruttolohn_sozialv_beitr_m
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def bruttolohn_sozialv_beitr_m(
    bruttolohn_m: FloatSeries,
    rentenv_beitr_bemess_grenze: FloatSeries,
    regulär_beschäft: BoolSeries,
) -> FloatSeries:
    """Calculate the wage, which is subject to social insurance contributions.

    Parameters
    ----------
    bruttolohn_m
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    regulär_beschäft
        See :func:`regulär_beschäft`.

    rentenv_beitr_bemess_grenze
        See :func:`rentenv_beitr_bemess_grenze`.


    Returns
    -------

    """
    bruttolohn_m_regulär_beschäft = bruttolohn_m.loc[regulär_beschäft]
    bemess_grenze = rentenv_beitr_bemess_grenze.loc[regulär_beschäft]
    return bruttolohn_m_regulär_beschäft.clip(upper=bemess_grenze)


def ges_beitr_arbeitslv_midi_job_m(
    midi_job_bemessungsentgelt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the sum of employee and employer unemployment insurance contribution.

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
        midi_job_bemessungsentgelt
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def ag_beitr_arbeitslv_midi_job_m(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the employer unemployment insurance contribution.

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
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def an_beitr_arbeitslv_midi_job_m(
    ges_beitr_arbeitslv_midi_job_m: FloatSeries,
    ag_beitr_arbeitslv_midi_job_m: FloatSeries,
) -> FloatSeries:
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    ges_beitr_arbeitslv_midi_job_m
        See :func:`ges_beitr_arbeitslv_midi_job_m`.

    ag_beitr_arbeitslv_midi_job_m
        See :func:`ag_beitr_arbeitslv_midi_job_m`.

    Returns
    -------

    """
    return ges_beitr_arbeitslv_midi_job_m - ag_beitr_arbeitslv_midi_job_m
