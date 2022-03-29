def ges_krankenv_beitr_m(
    geringfügig_beschäftigt: bool,
    ges_krankenv_beitr_rente_m: float,
    ges_krankenv_beitr_selbst_m: float,
    in_gleitzone: bool,
    _ges_krankenv_beitr_midi_job_m: float,
    _ges_krankenv_beitr_bruttolohn_m: float,
    soz_vers_beitr_params: dict,
    selbstständig: bool,
) -> float:
    """Contribution for each individual to the public health insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_krankenv_beitr_rente_m
        See :func:`ges_krankenv_beitr_rente_m`.
    ges_krankenv_beitr_selbst_m
        See :func:`ges_krankenv_beitr_selbst_m`.
    _ges_krankenv_beitr_midi_job_m
        See :func:`_ges_krankenv_beitr_midi_job_m`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _ges_krankenv_beitr_bruttolohn_m
        See :func:`_ges_krankenv_beitr_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.


    Returns
    -------

    """
    beitr_regulär_beschäftigt_m = (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["an"]
        * _ges_krankenv_beitr_bruttolohn_m
    )

    if selbstständig:
        out = ges_krankenv_beitr_selbst_m
    elif geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_krankenv_beitr_midi_job_m
    else:
        out = beitr_regulär_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente_m


def _ges_krankenv_beitr_bruttolohn_m(
    bruttolohn_m: float,
    _ges_krankenv_beitr_bemess_grenze_m: float,
    regulär_beschäftigt: bool,
) -> float:
    """Calculate the wage subject to public health insurance contributions.


    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    regulär_beschäftigt
        See :func:`regulär_beschäftigt`.
    _ges_krankenv_beitr_bemess_grenze_m
        See :func:`_ges_krankenv_beitr_bemess_grenze_m`.


    Returns
    -------

    """
    if regulär_beschäftigt:
        out = min(bruttolohn_m, _ges_krankenv_beitr_bemess_grenze_m)
    else:
        out = 0.0

    return out


def ges_krankenv_beitr_selbst_m(
    _ges_krankenv_bemessungsgrundlage_eink_selbst: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_eink_selbst
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbst`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Monthly health insurance contributions for self employed income.
    """
    beitr_satz = (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["ag"]
    )
    return _ges_krankenv_bemessungsgrundlage_eink_selbst * beitr_satz


def _ges_krankenv_bemessungsgrundlage_eink_selbst(
    eink_selbst_m: float,
    _ges_krankenv_bezugsgröße_selbst_m: float,
    selbstständig: bool,
    in_priv_krankenv: bool,
    soz_vers_beitr_params: dict,
) -> float:
    """Choose the amount of selfemployed income which is subject to health insurance
    contribution.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    _ges_krankenv_bezugsgröße_selbst_m
        See :func:`_ges_krankenv_bezugsgröße_selbst_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    in_priv_krankenv
        See basic input variable :ref:`in_priv_krankenv <in_priv_krankenv>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    # Calculate if selfemployed insures via public health insurance.
    if selbstständig and not in_priv_krankenv:
        bezugsgröße_selbstv_m = _ges_krankenv_bezugsgröße_selbst_m
        eink_selbst_selbstv_m = eink_selbst_m
    else:
        bezugsgröße_selbstv_m = 0.0
        eink_selbst_selbstv_m = 0.0

    anteil_ges_krankenv_bezugsgröße_selbst_m = (
        soz_vers_beitr_params["bezugsgröße_selbst_anteil"] * bezugsgröße_selbstv_m
    )

    if eink_selbst_selbstv_m > anteil_ges_krankenv_bezugsgröße_selbst_m:
        out = anteil_ges_krankenv_bezugsgröße_selbst_m
    else:
        out = eink_selbst_selbstv_m
    return out


def _ges_krankenv_bemessungsgrundlage_rente_m(
    sum_ges_rente_priv_rente_m: float,
    _ges_krankenv_beitr_bemess_grenze_m: float,
) -> float:
    """Choose the amount of pension which is subject to health insurance contribution.

    Parameters
    ----------
    sum_ges_rente_priv_rente_m
        See :func:`sum_ges_rente_priv_rente_m`.
    _ges_krankenv_beitr_bemess_grenze_m
        See :func:`_ges_krankenv_beitr_bemess_grenze_m`.

    Returns
    -------

    """
    out = min(sum_ges_rente_priv_rente_m, _ges_krankenv_beitr_bemess_grenze_m)
    return out


def ges_krankenv_beitr_rente_m(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Monthly health insurance contributions for pension income.
    """
    out = (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["an"]
        * _ges_krankenv_bemessungsgrundlage_rente_m
    )
    return out


def _ges_krankenv_beitr_midi_job_m(
    midi_job_bemessungsentgelt_m: float,
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employer health insurance contribution.

    Parameters
    ----------
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    gesamtbeitrag_midi_job_m = (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["ag"]
    ) * midi_job_bemessungsentgelt_m

    ag_beitr_midi_job_m = (
        bruttolohn_m * soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["ag"]
    )
    return gesamtbeitrag_midi_job_m - ag_beitr_midi_job_m
