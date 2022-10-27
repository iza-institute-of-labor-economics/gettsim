def ges_rentenv_beitr_m(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_midi_job_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    soz_vers_beitr_params: dict,
    in_gleitzone: bool,
) -> float:
    """Contribution for each individual to the pension insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    _ges_rentenv_beitr_midi_job_m
        See :func:`_ges_rentenv_beitr_midi_job_m`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    in_gleitzone
        See :func:`in_gleitzone`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_rentenv_beitr_midi_job_m
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


def _ges_rentenv_beitr_midi_job_m_bis_2022(
    midi_job_bemessungsentgelt_m: float,
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employee unemployment insurance contribution
    until October 2022.

    Parameters
    ----------
    midi_job_bemessungsentgelt_m
        See :func:`midi_job_bemessungsentgelt_m`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    ges_beitr_midi_job = (
        midi_job_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
    )
    ag_beitr_midi_job = (
        bruttolohn_m * soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
    )
    return ges_beitr_midi_job - ag_beitr_midi_job


def _ges_rentenv_beitr_midi_job_m_ab_2022(
    midi_sond_beitragspfl_einnahme_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employee unemployment insurance contribution
    since October 2022.

    Parameters
    ----------
    midi_sond_beitragspfl_einnahme_m
        See :func:`midi_sond_beitragspfl_einnahme_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    an_beitr_midi_job = (
        midi_sond_beitragspfl_einnahme_m
        * soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
    )
    return an_beitr_midi_job


def _ges_rentenv_beitr_bruttolohn_m(
    bruttolohn_m: float,
    _ges_rentenv_beitr_bemess_grenze_m: float,
) -> float:
    """Calculate the wage subject to pension and
    unemployment insurance contributions.

    Parameters
    ----------
    bruttolohn_m
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    _ges_rentenv_beitr_bemess_grenze_m
        See :func:`_ges_rentenv_beitr_bemess_grenze_m`.


    Returns
    -------

    """
    out = min(bruttolohn_m, _ges_rentenv_beitr_bemess_grenze_m)
    return out
