def ges_krankenv_beitr_m(
    geringfügig_beschäftigt: bool,
    ges_krankenv_beitr_rente_m: float,
    ges_krankenv_beitr_selbst_m: float,
    in_gleitzone: bool,
    ges_krankenv_beitr_midi_job_m: float,
    _ges_krankenv_beitr_reg_beschäftigt: float,
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
    ges_krankenv_beitr_midi_job_m
        See :func:`ges_krankenv_beitr_midi_job_m`.
    _ges_krankenv_beitr_reg_beschäftigt
        See :func:`_ges_krankenv_beitr_reg_beschäftigt`.
    in_gleitzone
        See :func:`in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.


    Returns
    -------

    """

    if selbstständig:
        out = ges_krankenv_beitr_selbst_m
    elif geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = ges_krankenv_beitr_midi_job_m
    else:
        out = _ges_krankenv_beitr_reg_beschäftigt

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente_m


def _ges_krankenv_beitr_reg_beschaeftigt_bis_06_2005(
    _ges_krankenv_bruttolohn_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions for regular jobs until 2008.

    As contribution rates differ between insurance entities until 2008, we rely on
    average contribution rate ('durchschnitt').

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """

    return (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["durchschnitt"] / 2
    ) * _ges_krankenv_bruttolohn_m


def _ges_krankenv_beitr_reg_beschaeftigt_ab_07_2005_bis_2008(
    _ges_krankenv_bruttolohn_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions for regular jobs

    Between 07/2005 and 12/2019,
    contributions were not equally split between employer and employee. Until
    2008, there was no statutory contribution rate. We hence apply the average
    rate.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        (soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["durchschnitt"] / 2)
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
    ) * _ges_krankenv_bruttolohn_m


def _ges_krankenv_beitr_reg_beschaeftigt_ab_2009_bis_2018(
    _ges_krankenv_bruttolohn_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions for regular jobs

    Between 07/2005 and 12/2019,
    contributions were not equally split between employer and employee. Until
    2008, there was no statutory contribution rate. We hence apply the average
    rate.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        (soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"] / 2)
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
    ) * _ges_krankenv_bruttolohn_m


def _ges_krankenv_beitr_reg_beschaeftigt_ab_2019(
    _ges_krankenv_bruttolohn_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions for regular jobs

    Since 2019, contributions are split equally between employee and employer,
    taking into account the top-up rate (we assume the average) and the statutory
    contribution rate.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """

    return (
        (
            soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"]
            + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
        )
        / 2
    ) * _ges_krankenv_bruttolohn_m


def _ges_krankenv_bruttolohn_m(
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


def _ges_krankenv_beitr_selbst_before2005(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    beitr_satz = soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["durchschnitt"]
    return _ges_krankenv_bemessungsgrundlage_rente_m * beitr_satz


def _ges_krankenv_beitr_selbst_2005_2008(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    beitr_satz = (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["durchschnitt"]
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
    )
    return _ges_krankenv_bemessungsgrundlage_rente_m * beitr_satz


def _ges_krankenv_beitr_selbst_ab_2009(
    _ges_krankenv_bemessungsgrundlage_eink_selbst, soz_vers_beitr_params: dict
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
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"]
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
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


def _ges_krankenv_beitr_rente_until2005(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions for pension incomes until 2008.

    As contribution rates differ between insurance entities until 2008, we rely on
    average contribution rate ('durchschnitt').

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions on pension income
    income.
    """

    return (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["durchschnitt"] / 2
    ) * _ges_krankenv_bemessungsgrundlage_rente_m


def _ges_krankenv_beitr_rente_2005_2008(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions for pension incomes

    Between 07/2005 and 12/2019,
    contributions were not equally split between employer and employee. Until
    2008, there was no statutory contribution rate. We hence apply the average
    rate.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    out = (
        (soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["durchschnitt"] / 2)
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
    ) * _ges_krankenv_bemessungsgrundlage_rente_m
    return out


def _ges_krankenv_beitr_rente_2009_2018(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions for pension incomes

    Between 07/2005 and 12/2019,
    contributions were not equally split between employer and employee. Until
    2008, there was no statutory contribution rate. We hence apply the average
    rate.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    out = (
        (soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"] / 2)
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
    ) * _ges_krankenv_bemessungsgrundlage_rente_m
    return out


def _ges_krankenv_beitr_rente_ab_2019(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculates health insurance contributions for pension incomes

    Since 2019, contributions are split equally between employee and employer,
    taking into account the top-up rate (we assume the average) and the statutory
    contribution rate.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    out = (
        (
            soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"]
            + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
        )
        / 2
    ) * _ges_krankenv_bemessungsgrundlage_rente_m

    return out


def _ges_beitr_ges_krankenv_midi_job_ab_2003_bis_2008(
    midi_job_bemessungsentgelt_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculating the sum of employee and employer health insurance contribution.


    Parameters
    ----------
    midi_job_bemessungsentgelt_m
        See :func:`midi_job_bemessungsentgelt_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    out = (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["durchschnitt"]
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
    ) * midi_job_bemessungsentgelt_m
    return out


def _ges_beitr_ges_krankenv_midi_job_ab_2009(
    midi_job_bemessungsentgelt_m: float, soz_vers_beitr_params: dict
) -> float:
    """Calculating the sum of employee and employer health insurance contribution.


    Parameters
    ----------
    midi_job_bemessungsentgelt_m
        See :func:`midi_job_bemessungsentgelt_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    out = (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"]
        + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["zusatz"]
    ) * midi_job_bemessungsentgelt_m
    return out


def _ag_beitr_ges_krankenv_midi_job_ab_2003_bis_2008(
    bruttolohn_m: float, in_gleitzone: bool, soz_vers_beitr_params: dict
) -> float:
    """Calculating the employer health insurance contribution.

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
    if in_gleitzone:
        out = (
            bruttolohn_m
            * soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["durchschnitt"]
            / 2
        )
    else:
        out = 0.0

    return out


def _ag_beitr_ges_krankenv_midi_job_ab_2009(
    bruttolohn_m: float, in_gleitzone: bool, soz_vers_beitr_params: dict
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
    if in_gleitzone:
        out = (
            bruttolohn_m
            * soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"]
            / 2
        )
    else:
        out = 0.0

    return out


def an_beitr_ges_krankenv_midi_job(
    ges_krankenv_beitr_midi_job_m: float,
    ag_beitr_ges_krankenv_midi_job: float,
) -> float:
    """Calculating the employer health insurance contribution.


    Parameters
    ----------
    ges_krankenv_beitr_midi_job_m
        See :func:`ges_krankenv_beitr_midi_job_m`.
    ag_beitr_ges_krankenv_midi_job
        See :func:`ag_beitr_ges_krankenv_midi_job`.
    Returns
    -------

    """
    return ges_krankenv_beitr_midi_job_m - ag_beitr_ges_krankenv_midi_job


def selbstständig_ges_krankenv(selbstständig: bool, in_priv_krankenv: bool) -> bool:
    """
    Create boolean Series indicating selfemployed insures via public health insurance.
    Parameters
    ----------
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    in_priv_krankenv
        See basic input variable :ref:`in_priv_krankenv <in_priv_krankenv>`.
    Returns
    -------
    """
    return selbstständig & (not in_priv_krankenv)
