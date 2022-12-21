def ges_krankenv_beitr_m(
    geringfügig_beschäftigt: bool,
    ges_krankenv_beitr_rente_m: float,
    ges_krankenv_beitr_selbst_m: float,
    in_gleitzone: bool,
    _ges_krankenv_midijob_arbeitn_m: float,
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
    _ges_krankenv_midijob_arbeitn_m
        See :func:`_ges_krankenv_midijob_arbeitn_m`.
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
        out = _ges_krankenv_midijob_arbeitn_m
    else:
        out = _ges_krankenv_beitr_reg_beschäftigt

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente_m


def ges_krankenv_beitr_arbeitg_m(
    geringfügig_beschäftigt: bool,
    in_gleitzone: bool,
    bruttolohn_m: float,
    _ges_krankenv_midijob_arbeitg_m: float,
    _ges_krankenv_bruttolohn_m: float,
    selbstständig: bool,
    soz_vers_beitr_params: dict,
    _ges_krankenv_beitr_satz_arbeitg: float,
) -> float:
    """Contribution of the respective employer to the public health insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_krankenv_midijob_arbeitg_m
        See :func:`_ges_krankenv_midijob_arbeitg_m`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.
    in_gleitzone
        See :func:`in_gleitzone`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------

    """

    if selbstständig:
        out = 0.0
    elif geringfügig_beschäftigt:
        out = bruttolohn_m * soz_vers_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
    elif in_gleitzone:
        out = _ges_krankenv_midijob_arbeitg_m
    else:
        out = _ges_krankenv_bruttolohn_m * _ges_krankenv_beitr_satz_arbeitg

    return out


def ges_krankenv_beitr_satz_bis_2018(soz_vers_beitr_params: dict) -> float:
    """Select contribution rates of employees for health insurance until 2018.

    The contribution rates consists of a general rate (split equally between employers
    and employees) and a top-up rate which is fully paid by employees.

    Parameters
    ----------
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    params = soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]

    # Contribution rates differ between insurance entities until 2008.
    # We, hence, rely on average contribution rates "mean_allgemein" for these years.
    allgemeiner_beitrag = (
        params["allgemein"] if "allgemein" in params else params["mean_allgemein"]
    )

    # From July 2005 until 2014, Sonderbeitrag is in place
    # From 2015 on, a Zusatzbeitrag is in place which differs between
    # insurance entities
    if "sonderbeitrag" in params:
        zusatzbeitrag = params["sonderbeitrag"]
    elif "mean_zusatzbeitrag" in params:
        zusatzbeitrag = params["mean_zusatzbeitrag"]
    else:
        zusatzbeitrag = 0
    return allgemeiner_beitrag / 2 + zusatzbeitrag


def ges_krankenv_beitr_satz_ab_2019(soz_vers_beitr_params: dict) -> float:
    """Select contribution rates of employees for health insurance since 2019.

    Zusatzbeitrag is now split equally between employers and employees.

    Parameters
    ----------
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    params = soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]
    allgemeiner_beitrag = params["allgemein"]
    zusatzbeitrag = params["mean_zusatzbeitrag"]
    return (allgemeiner_beitrag + zusatzbeitrag) / 2


def _ges_krankenv_beitr_satz_arbeitg_bis_2018(soz_vers_beitr_params: dict) -> float:
    """Select contribution rates of employers for health insurance until 2018.

    Parameters
    ----------
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    params = soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]

    # Contribution rates differ between insurance entities until 2008.
    # We, hence, rely on average contribution rates "mean_allgemein".
    allgemeiner_beitrag = (
        params["allgemein"] if "allgemein" in params else params["mean_allgemein"]
    )

    return allgemeiner_beitrag / 2


def _ges_krankenv_beitr_satz_arbeitg_ab_2019(ges_krankenv_beitr_satz: float) -> float:
    """Select contribution rates of employers for health insurance since 2019.

    The full contribution rate is now split equally between employers and employees.

    Parameters
    ----------
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.

    Returns
    -------

    """
    return ges_krankenv_beitr_satz


def _ges_krankenv_bruttolohn_m(
    bruttolohn_m: float,
    _ges_krankenv_beitr_bemess_grenze_m: float,
    regulär_beschäftigt: bool,
) -> float:
    """Calculate the wage subject to public health insurance contributions. This affects
    marginally employed persons and high wages for above the assessment ceiling.

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


def _ges_krankenv_beitr_reg_beschäftigt(
    _ges_krankenv_bruttolohn_m: float, ges_krankenv_beitr_satz: float
) -> float:
    """Calculates health insurance contributions for regular jobs.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for regularly
    employed income.

    """

    return ges_krankenv_beitr_satz * _ges_krankenv_bruttolohn_m


def _ges_krankenv_bemessungsgrundlage_eink_selbst(
    eink_selbst_m: float,
    _ges_krankenv_bezugsgröße_selbst_m: float,
    selbstständig: bool,
    in_priv_krankenv: bool,
    soz_vers_beitr_params: dict,
) -> float:
    """Choose the amount of self-employed income which is subject to health insurance
    contributions. Only affects those self-employed who voluntarily contribute to the
    public health system. For those, contributions are assessed either on total self-
    employement income or 3/4 of the 'Bezugsgröße'.

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
    # Calculate if self employed insures via public health insurance.
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


def ges_krankenv_beitr_selbst_m(
    _ges_krankenv_bemessungsgrundlage_eink_selbst: float,
    ges_krankenv_beitr_satz: float,
    _ges_krankenv_beitr_satz_arbeitg: float,
) -> float:
    """Calculates health insurance contributions for self employed income. Self-employed
    pay the full contribution (employer + employee).

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_eink_selbst
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbst`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.

    """
    out = (
        ges_krankenv_beitr_satz + _ges_krankenv_beitr_satz_arbeitg
    ) * _ges_krankenv_bemessungsgrundlage_eink_selbst
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
    return min(sum_ges_rente_priv_rente_m, _ges_krankenv_beitr_bemess_grenze_m)


def ges_krankenv_beitr_rente_m(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, ges_krankenv_beitr_satz: float
) -> float:
    """Calculates health insurance contributions for pension incomes.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions on pension income
    income.

    """

    return ges_krankenv_beitr_satz * _ges_krankenv_bemessungsgrundlage_rente_m


def _ges_krankenv_midijob_sum_arbeitn_arbeitg_m(
    midijob_bemessungsentgelt_m: float,
    ges_krankenv_beitr_satz: float,
    _ges_krankenv_beitr_satz_arbeitg: float,
) -> float:
    """Calculating the sum of employee and employer health insurance contribution for
    midijobs.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.

    Returns
    -------

    """
    out = (
        ges_krankenv_beitr_satz + _ges_krankenv_beitr_satz_arbeitg
    ) * midijob_bemessungsentgelt_m
    return out


def _ges_krankenv_midijob_arbeitg_m_bis_09_2022(
    bruttolohn_m: float, in_gleitzone: bool, _ges_krankenv_beitr_satz_arbeitg: float
) -> float:
    """Calculating the employer health insurance contribution for midijobs until
    September 2022.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.
    Returns
    -------

    """
    if in_gleitzone:
        out = _ges_krankenv_beitr_satz_arbeitg * bruttolohn_m
    else:
        out = 0.0

    return out


def _ges_krankenv_midijob_arbeitg_m_ab_10_2022(
    _ges_krankenv_midijob_sum_arbeitn_arbeitg_m: float,
    _ges_krankenv_midijob_arbeitn_m: float,
    in_gleitzone: bool,
) -> float:
    """Calculating the employer health insurance contribution for midijobs since October
    2022.

    Parameters
    ----------
    _ges_krankenv_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_krankenv_midijob_sum_arbeitn_arbeitg_m`.
    _ges_krankenv_midijob_arbeitn_m
        See :func:`_ges_krankenv_midijob_arbeitn_m`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.
    Returns
    -------

    """
    if in_gleitzone:
        out = (
            _ges_krankenv_midijob_sum_arbeitn_arbeitg_m
            - _ges_krankenv_midijob_arbeitn_m
        )
    else:
        out = 0.0

    return out


def _ges_krankenv_midijob_arbeitn_m_bis_09_2022(
    _ges_krankenv_midijob_sum_arbeitn_arbeitg_m: float,
    _ges_krankenv_midijob_arbeitg_m: float,
) -> float:
    """Calculating the employee health insurance contribution for midijobs until
    September 2022.

    Parameters
    ----------
    _ges_krankenv_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_krankenv_midijob_sum_arbeitn_arbeitg_m`.
    _ges_krankenv_midijob_arbeitg_m
        See :func:`_ges_krankenv_midijob_arbeitg_m`.
    Returns
    -------

    """
    return _ges_krankenv_midijob_sum_arbeitn_arbeitg_m - _ges_krankenv_midijob_arbeitg_m


def _ges_krankenv_midijob_arbeitn_m_ab_10_2022(
    _midijob_beitragspf_einnahme_arbeitn_m: float,
    ges_krankenv_beitr_satz: float,
) -> float:
    """Calculating the employee health insurance contribution for midijobs since October
    2022.

    Parameters
    ----------
    _midijob_beitragspf_einnahme_arbeitn_m
        See :func:`_midijob_beitragspf_einnahme_arbeitn_m`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    Returns
    -------

    """
    return _midijob_beitragspf_einnahme_arbeitn_m * ges_krankenv_beitr_satz
