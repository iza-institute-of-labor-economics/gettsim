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
    _arbeitsl_v_beitr_midijob_arbeitn_m: float,
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
    _arbeitsl_v_beitr_midijob_arbeitn_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitn_m`.
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
        out = _arbeitsl_v_beitr_midijob_arbeitn_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


def _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m_bis_10_2022(
    midijob_bemessungsentgelt_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the sum of employee and employer unemployment insurance
    contribution for midijobs until October 2022.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    gesamtbeitrag_midijob_m = (
        midijob_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    return gesamtbeitrag_midijob_m


def _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m_ab_10_2022(
    midijob_beitragspf_einnahme_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the sum of employee and employer unemployment insurance
    contribution for midijobs since October 2022.

    Parameters
    ----------
    midijob_beitragspf_einnahme_m
        See :func:`midijob_beitragspf_einnahme_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    gesamtbeitrag_midijob_m = (
        midijob_beitragspf_einnahme_m
        * 2
        * soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    return gesamtbeitrag_midijob_m


def _arbeitsl_v_beitr_midijob_arbeitg_m_bis_10_2022(
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employer unemployment insurance contribution until October 2022.

    Parameters
    ----------
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.

    Returns
    -------

    """
    ag_beitr_midijob_m = (
        bruttolohn_m * soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    return ag_beitr_midijob_m


def _arbeitsl_v_beitr_midijob_arbeitg_m_ab_10_2022(
    _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m: float,
    _arbeitsl_v_beitr_midijob_arbeitn_m: float,
) -> float:
    """Calculating the employer unemployment insurance contribution since October 2022.

    Parameters
    ----------
    _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m`.
    _arbeitsl_v_beitr_midijob_arbeitn_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitn_m`.

    Returns
    -------

    """
    ag_beitr_midijob_m = (
        _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m
        - _arbeitsl_v_beitr_midijob_arbeitn_m
    )
    return ag_beitr_midijob_m


def _arbeitsl_v_beitr_midijob_arbeitn_m_bis_10_2022(
    _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m: float,
    _arbeitsl_v_beitr_midijob_arbeitg_m: float,
) -> float:
    """Calculating the employee unemployment insurance contribution until October 2022.

    Parameters
    ----------
    _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m`.
    _arbeitsl_v_beitr_midijob_arbeitg_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitg_m`.

    Returns
    -------

    """
    an_beitr_midijob_m = (
        _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m
        - _arbeitsl_v_beitr_midijob_arbeitg_m
    )
    return an_beitr_midijob_m


def _arbeitsl_v_beitr_midijob_arbeitn_m_ab_10_2022(
    _midijob_beitragspf_einnahme_arbeitn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculating the employee unemployment insurance contribution since October 2022.

    Parameters
    ----------
    _midijob_beitragspf_einnahme_arbeitn_m
        See :func:`_midijob_beitragspf_einnahme_arbeitn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    an_beitr_midijob_m = (
        _midijob_beitragspf_einnahme_arbeitn_m
        * soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    return an_beitr_midijob_m
