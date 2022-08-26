"""Functions for modeling unemployment and pension insurance."""


def sozialv_beitr_gesamt_m(
    ges_pflegev_beitr_m: float,
    ges_krankenv_beitr_m: float,
    ges_rentenv_beitr_m: float,
    arbeitsl_v_beitr_m: float,
) -> float:
    """Sum of all social insurance contributions of an individual.


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
    out = (
        ges_pflegev_beitr_m
        + ges_krankenv_beitr_m
        + ges_rentenv_beitr_m
        + arbeitsl_v_beitr_m
    )
    return out


def arbeitsl_v_beitr_m(
    geringfügig_beschäftigt: bool,
    in_gleitzone: bool,
    _arbeitsl_v_beitr_midi_job_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Contribution for each individual to the unemployment insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    in_gleitzone
        See :func:`in_gleitzone`.
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
        * soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _arbeitsl_v_beitr_midi_job_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


def _arbeitsl_v_beitr_midi_job_m(
    midi_job_bemessungsentgelt_m: float,
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt_m
        See :func:`midi_job_bemessungsentgelt_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.

    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    gesamtbeitrag_midi_job_m = (
        midi_job_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    ag_beitr_midi_job_m = (
        bruttolohn_m * soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    return gesamtbeitrag_midi_job_m - ag_beitr_midi_job_m
