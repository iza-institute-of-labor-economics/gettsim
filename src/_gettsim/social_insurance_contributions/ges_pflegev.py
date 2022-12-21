def ges_pflegev_zusatz_kinderlos(
    hat_kinder: bool,
    alter: int,
    soz_vers_beitr_params: dict,
) -> bool:
    """Whether additional care insurance contribution for childless individuals applies.

    Parameters
    ----------
    hat_kinder
        See basic input variable :ref:`hat_kinder <hat_kinder>`.
    alter
        See basic input variable :ref:`alter <alter>`.

    Returns
    -------

    """
    if "ges_pflegev_zusatz_kinderlos_mindestalter" in soz_vers_beitr_params:
        altersgrenze = soz_vers_beitr_params[
            "ges_pflegev_zusatz_kinderlos_mindestalter"
        ]
        out = (not hat_kinder) and alter >= altersgrenze
    else:
        out = False
    return out


def ges_pflegev_beitr_m(
    geringfügig_beschäftigt: bool,
    ges_pflegev_beitr_rente_m: float,
    ges_pflegev_beitr_selbst_m: float,
    _ges_pflegev_beitr_midijob_arbeitn_m: float,
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
    _ges_pflegev_beitr_midijob_arbeitn_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitn_m`.
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
        out = _ges_pflegev_beitr_midijob_arbeitn_m
    else:
        out = beitr_regulär_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + ges_pflegev_beitr_rente_m


def ges_pflegev_beitr_arbeitg_m(
    geringfügig_beschäftigt: bool,
    _ges_pflegev_beitr_midijob_arbeitg_m: float,
    _ges_krankenv_bruttolohn_m: float,
    soz_vers_beitr_params: dict,
    in_gleitzone: bool,
    selbstständig: bool,
) -> float:
    """Contribution of the respective employer to the public care insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_pflegev_beitr_midijob_arbeitg_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitg_m`.
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

    if selbstständig:
        out = 0.0
    if geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_pflegev_beitr_midijob_arbeitg_m
    else:
        out = beitr_regulär_beschäftigt_m

    return out


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


def _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m_bis_09_2022(
    midijob_bemessungsentgelt_m: float,
    soz_vers_beitr_params: dict,
    ges_pflegev_zusatz_kinderlos: bool,
) -> float:
    """Calculating the sum of employee and employer care insurance contribution for
    midijobs until September 2022.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """

    gesamtbeitrag_midijob_m = (
        midijob_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        gesamtbeitrag_midijob_m += (
            midijob_bemessungsentgelt_m
            * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return gesamtbeitrag_midijob_m


def _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m_ab_10_2022(
    midijob_bemessungsentgelt_m: float,
    soz_vers_beitr_params: dict,
    ges_pflegev_zusatz_kinderlos: bool,
) -> float:
    """Calculating the sum of employee and employer care insurance contribution for
    midijobs since October 2022.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """

    gesamtbeitrag_midijob_m = (
        midijob_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        gesamtbeitrag_midijob_m += (
            midijob_bemessungsentgelt_m
            * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return gesamtbeitrag_midijob_m


def _ges_pflegev_beitr_midijob_arbeitg_m_bis_09_2022(
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employer care insurance contribution until September 2022.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------

    """
    out = bruttolohn_m * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    return out


def _ges_pflegev_beitr_midijob_arbeitg_m_ab_10_2022(
    _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m: float,
    _ges_pflegev_beitr_midijob_arbeitn_m: float,
) -> float:
    """Calculating the employer care insurance contribution since October 2022.

    Parameters
    ----------
    _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m`.
    _ges_pflegev_beitr_midijob_arbeitn_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitn_m`.


    Returns
    -------

    """
    out = (
        _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m
        - _ges_pflegev_beitr_midijob_arbeitn_m
    )
    return out


def _ges_pflegev_beitr_midijob_arbeitn_m_bis_09_2022(
    _ges_pflegev_beitr_midijob_arbeitg_m: float,
    _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m: float,
) -> float:
    """Calculating the employee care insurance contribution until September 2022.

    Parameters
    ----------
    _ges_pflegev_beitr_midijob_arbeitg_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitg_m`.
    _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m`.

    Returns
    -------

    """
    out = (
        _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m
        - _ges_pflegev_beitr_midijob_arbeitg_m
    )

    return out


def _ges_pflegev_beitr_midijob_arbeitn_m_ab_10_2022(
    ges_pflegev_zusatz_kinderlos: bool,
    _midijob_beitragspf_einnahme_arbeitn_m: float,
    midijob_bemessungsentgelt_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employee care insurance contribution since October 2022.

    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    _midijob_beitragspf_einnahme_arbeitn_m
        See :func:`_midijob_beitragspf_einnahme_arbeitn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    # Calculate the employee care insurance contribution
    an_beitr_midijob_m = (
        _midijob_beitragspf_einnahme_arbeitn_m
        * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        an_beitr_midijob_m += (
            midijob_bemessungsentgelt_m
            * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m
