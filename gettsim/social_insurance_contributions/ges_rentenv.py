import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def ges_rentenv_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    _ges_rentenv_beitr_midi_job_m_m: FloatSeries,
    _ges_rentenv_beitr_bruttolohn_m: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Contribution for each individual to the pension insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    _ges_rentenv_beitr_midi_job_m_m
        See :func:`_ges_rentenv_beitr_midi_job_m_m`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_rentenv"]
    )
    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[_ges_rentenv_beitr_midi_job_m_m.index] = _ges_rentenv_beitr_midi_job_m_m
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


def _ges_rentenv_beitr_midi_job_m_m(
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
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    ges_beitr_midi_job = (
        midi_job_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_rentenv"]
    )
    ag_beitr_midi_job = (
        bruttolohn_m.loc[in_gleitzone]
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_rentenv"]
    )
    return ges_beitr_midi_job - ag_beitr_midi_job


def _ges_rentenv_beitr_bruttolohn_m(
    bruttolohn_m: FloatSeries,
    _ges_rentenv_beitr_bemess_grenze_m: FloatSeries,
    regulär_beschäftigt: BoolSeries,
) -> FloatSeries:
    """Calculate the wage subject to pension and
    unemployment insurance contributions.

    Parameters
    ----------
    bruttolohn_m
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    regulär_beschäftigt
        See :func:`regulär_beschäftigt`.
    _ges_rentenv_beitr_bemess_grenze_m
        See :func:`_ges_rentenv_beitr_bemess_grenze_m`.


    Returns
    -------

    """
    bruttolohn_m_regulär_beschäftigt = bruttolohn_m.loc[regulär_beschäftigt]
    bemess_grenze = _ges_rentenv_beitr_bemess_grenze_m.loc[regulär_beschäftigt]
    return bruttolohn_m_regulär_beschäftigt.clip(upper=bemess_grenze)
