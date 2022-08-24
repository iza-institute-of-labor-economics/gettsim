def ges_pflegev_zusatz_kinderlos(
    hat_kinder: bool,
    alter: int,
    soz_vers_beitr_params: dict,
) -> bool:
    """
    Whether additional care insurance contribution for childless individuals applies.

    Parameters
    ----------
    hat_kinder
        See basic input variable :ref:`hat_kinder <hat_kinder>`.
    alter
        See basic input variable :ref:`alter <alter>`.

    Returns
    -------

    """
    altersgrenze = soz_vers_beitr_params["ges_pflegev_zusatz_kinderlos_mindestalter"]
    out = (not hat_kinder) and alter >= altersgrenze
    return out


def ges_pflegev_beitr_m(
    geringfügig_beschäftigt: bool,
    ges_pflegev_beitr_rente_m: float,
    ges_pflegev_beitr_selbst_m: float,
    _ges_pflegev_beitr_midi_job_m: float,
    ges_pflegev_zusatz_kinderlos: bool,
    _ges_krankenv_bruttolohn_m: float,
    soz_vers_beitr_params: dict,
    in_gleitzone: bool,
    selbstständig: bool,
) -> float:
    """Contribution for each individual to the public care insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_pflegev_beitr_rente_m
        See :func:`ges_pflegev_beitr_rente_m`.
    ges_pflegev_beitr_selbst_m
        See :func:`ges_pflegev_beitr_selbst_m`.
    _ges_pflegev_beitr_midi_job_m
        See :func:`_ges_pflegev_beitr_midi_job_m`.
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------

    """

    # Calculate care insurance contributions for regular jobs.
    beitr_regulär_beschäftigt_m = (
        _ges_krankenv_bruttolohn_m
        * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        beitr_regulär_beschäftigt_m += (
            _ges_krankenv_bruttolohn_m
            * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    if selbstständig:
        out = ges_pflegev_beitr_selbst_m
    elif geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_pflegev_beitr_midi_job_m
    else:
        out = beitr_regulär_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + ges_pflegev_beitr_rente_m


def ges_pflegev_beitr_selbst_m(
    ges_pflegev_zusatz_kinderlos: bool,
    _ges_krankenv_bemessungsgrundlage_eink_selbst: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculates care insurance contributions for self-employed individuals.

    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.

    _ges_krankenv_bemessungsgrundlage_eink_selbst
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbst`.

    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Monthly care insurance contributions for self employed income.
    """
    out = (
        _ges_krankenv_bemessungsgrundlage_eink_selbst
        * 2
        * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        out += (
            _ges_krankenv_bemessungsgrundlage_eink_selbst
            * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return out


def ges_pflegev_beitr_rente_m(
    ges_pflegev_zusatz_kinderlos: bool,
    _ges_krankenv_bemessungsgrundlage_rente_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Monthly health insurance contributions for pension income.
    """
    out = (
        _ges_krankenv_bemessungsgrundlage_rente_m
        * 2
        * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        out += (
            _ges_krankenv_bemessungsgrundlage_rente_m
            * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return out


def _ges_pflegev_beitr_midi_job_m(
    ges_pflegev_zusatz_kinderlos: bool,
    midi_job_bemessungsentgelt_m: float,
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employer care insurance contribution.


    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    midi_job_bemessungsentgelt_m
        See :func:`midi_job_bemessungsentgelt_m`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------

    """
    # Calculate the sum of employee and employer care insurance contribution.
    gesamtbeitrag_midi_job_m = (
        midi_job_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        gesamtbeitrag_midi_job_m += (
            midi_job_bemessungsentgelt_m
            * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    ag_beitr_midi_job_m = (
        bruttolohn_m * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )
    return gesamtbeitrag_midi_job_m - ag_beitr_midi_job_m
