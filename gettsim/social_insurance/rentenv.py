import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


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
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return rentenv_beitr_m.groupby(tu_id).sum()


def rentenv_beitr_regular_job(
    ges_beitr_arbeitsl_v_midi_jobreturn: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates pension insurance contributions for regular jobs.

    Parameters
    ----------
    ges_beitr_arbeitsl_v_midi_jobreturn
        See :func:`ges_beitr_arbeitsl_v_midi_jobreturn`.

    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    return (
        ges_beitr_arbeitsl_v_midi_jobreturn
        * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )


def ag_beitr_rentenv_midi_job(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the employer pension insurance contribution.

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
    out = (
        bruttolohn_m__in_gleitzone * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )
    return out


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
