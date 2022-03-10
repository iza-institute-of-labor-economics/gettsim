import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def ges_rentenv_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    ges_rentenv_beitr_regular_job_m: FloatSeries,
    an_beitr_ges_rentenv_midi_job_m: FloatSeries,
) -> FloatSeries:
    """Contribution for each individual to the pension insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    ges_rentenv_beitr_regular_job_m
        See :func:`ges_rentenv_beitr_regular_job_m`.

    an_beitr_ges_rentenv_midi_job_m
        See :func:`an_beitr_ges_rentenv_midi_job_m`.


    Returns
    -------

    """

    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_ges_rentenv_midi_job_m.index] = an_beitr_ges_rentenv_midi_job_m
    out.loc[ges_rentenv_beitr_regular_job_m.index] = ges_rentenv_beitr_regular_job_m

    return out


def ges_rentenv_beitr_m_tu(
    ges_rentenv_beitr_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Calculate the contribution of each tax unit to the pension insurance.

    Parameters
    ----------
    ges_rentenv_beitr_m
        See :func:`ges_rentenv_beitr_m`.

    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return ges_rentenv_beitr_m.groupby(tu_id).sum()


def ges_rentenv_beitr_regular_job_m(
    bruttolohn_ges_rentenv_beitr_m: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates pension insurance contributions for regular jobs.

    Parameters
    ----------
    bruttolohn_ges_rentenv_beitr_m
        See :func:`bruttolohn_ges_rentenv_beitr_m`.

    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    return (
        bruttolohn_ges_rentenv_beitr_m
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_rentenv"]
    )


def ag_beitr_ges_rentenv_midi_job_m(
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
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    out = (
        bruttolohn_m_in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_rentenv"]
    )
    return out


def an_beitr_ges_rentenv_midi_job_m(
    ges_beitr_ges_rentenv_midi_job_m: FloatSeries,
    ag_beitr_ges_rentenv_midi_job_m: FloatSeries,
) -> FloatSeries:
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    ges_beitr_ges_rentenv_midi_job_m
        See :func:`ges_beitr_ges_rentenv_midi_job_m`.

    ag_beitr_ges_rentenv_midi_job_m
        See :func:`ag_beitr_ges_rentenv_midi_job_m`.

    Returns
    -------

    """
    return ges_beitr_ges_rentenv_midi_job_m - ag_beitr_ges_rentenv_midi_job_m
