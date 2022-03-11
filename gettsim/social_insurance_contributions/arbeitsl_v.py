"""Functions for modeling unemployment and pension insurance."""
import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries


def sozialv_beitr_gesamt_m(
    ges_pflegev_beitr_m: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    ges_rentenv_beitr_m: FloatSeries,
    arbeitsl_v_beitr_m: FloatSeries,
) -> FloatSeries:
    """Sum of all social insurance contributions.


    Parameters
    ----------
    ges_pflegev_beitr_m
        See :func:`ges_pflegev_beitr_m`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    ges_rentenv_beitr_m
        See :func:`ges_rentenv_beitr_m`.
    arbeitsl_v_beitr_m
        See :func:`arbeitsl_v_beitr_m`.

    Returns
    -------

    """
    return (
        ges_pflegev_beitr_m
        + ges_krankenv_beitr_m
        + ges_rentenv_beitr_m
        + arbeitsl_v_beitr_m
    )


def arbeitsl_v_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    _arbeitsl_v_beitr_midi_job_m: FloatSeries,
    _ges_rentenv_beitr_bruttolohn_m: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculate the contribution for each individual to the unemployment insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _arbeitsl_v_beitr_midi_job_m
        See :func:`_arbeitsl_v_beitr_midi_job_m`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )
    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions, for minijobs it remains 0
    out.loc[_arbeitsl_v_beitr_midi_job_m.index] = _arbeitsl_v_beitr_midi_job_m
    out.loc[arbeitsl_v_regulär_beschäftigt_m.index] = arbeitsl_v_regulär_beschäftigt_m

    return out


def _arbeitsl_v_beitr_midi_job_m(
    midi_job_bemessungsentgelt_m: FloatSeries,
    bruttolohn_m: FloatSeries,
    in_gleitzone: BoolSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt_m
        See :func:`midi_job_bemessungsentgelt_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    ges_beitr_midi_job_m = (
        midi_job_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )
    ag_beitr_midi_job_m = (
        bruttolohn_m.loc[in_gleitzone]
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )
    return ges_beitr_midi_job_m - ag_beitr_midi_job_m
