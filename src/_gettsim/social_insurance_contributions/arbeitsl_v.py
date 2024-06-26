"""Functions for modeling unemployment and pension insurance."""

from _gettsim.shared import policy_info


def sozialv_beitr_arbeitnehmer_m(
    ges_pflegev_beitr_arbeitnehmer_m: float,
    ges_krankenv_beitr_arbeitnehmer_m: float,
    ges_rentenv_beitr_arbeitnehmer_m: float,
    arbeitsl_v_beitr_arbeitnehmer_m: float,
) -> float:
    """Sum of employee's social insurance contributions.

    Parameters
    ----------
    ges_pflegev_beitr_arbeitnehmer_m
        See :func:`ges_pflegev_beitr_arbeitnehmer_m`.
    ges_krankenv_beitr_arbeitnehmer_m
        See :func:`ges_krankenv_beitr_arbeitnehmer_m`.
    ges_rentenv_beitr_arbeitnehmer_m
        See :func:`ges_rentenv_beitr_arbeitnehmer_m`.
    arbeitsl_v_beitr_arbeitnehmer_m
        See :func:`arbeitsl_v_beitr_arbeitnehmer_m`.

    Returns
    -------

    """
    out = (
        ges_pflegev_beitr_arbeitnehmer_m
        + ges_krankenv_beitr_arbeitnehmer_m
        + ges_rentenv_beitr_arbeitnehmer_m
        + arbeitsl_v_beitr_arbeitnehmer_m
    )
    return out


def sozialv_beitr_arbeitgeber_m(
    ges_pflegev_beitr_arbeitgeber_m: float,
    ges_krankenv_beitr_arbeitgeber_m: float,
    ges_rentenv_beitr_arbeitgeber_m: float,
    arbeitsl_v_beitr_arbeitgeber_m: float,
) -> float:
    """Sum of employer's social insurance contributions.

    Parameters
    ----------
    ges_pflegev_beitr_arbeitgeber_m
        See :func:`ges_pflegev_beitr_arbeitgeber_m`.
    ges_krankenv_beitr_arbeitgeber_m
        See :func:`ges_krankenv_beitr_arbeitgeber_m`.
    ges_rentenv_beitr_arbeitgeber_m
        See :func:`ges_rentenv_beitr_arbeitgeber_m`.
    arbeitsl_v_beitr_arbeitgeber_m
        See :func:`arbeitsl_v_beitr_arbeitgeber_m`.

    Returns
    -------

    """
    out = (
        ges_pflegev_beitr_arbeitgeber_m
        + ges_krankenv_beitr_arbeitgeber_m
        + ges_rentenv_beitr_arbeitgeber_m
        + arbeitsl_v_beitr_arbeitgeber_m
    )
    return out


def _sozialv_beitr_summe_m(
    sozialv_beitr_arbeitnehmer_m: float,
    sozialv_beitr_arbeitgeber_m: float,
) -> float:
    """Sum of employer's and employee's social insurance contributions.

    Parameters
    ----------
    sozialv_beitr_arbeitnehmer_m
        See :func:`sozialv_beitr_arbeitnehmer_m`.
    sozialv_beitr_arbeitgeber_m
        See :func:`sozialv_beitr_arbeitgeber_m`.
    Returns
    -------

    """
    out = sozialv_beitr_arbeitnehmer_m + sozialv_beitr_arbeitgeber_m
    return out


@policy_info(end_date="2003-03-31", name_in_dag="arbeitsl_v_beitr_arbeitnehmer_m")
def arbeitsl_v_beitr_arbeitnehmer_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if geringfügig_beschäftigt:
        out = 0.0
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_info(start_date="2003-04-01", name_in_dag="arbeitsl_v_beitr_arbeitnehmer_m")
def arbeitsl_v_beitr_arbeitnehmer_m_mit_midijob(
    geringfügig_beschäftigt: bool,
    in_gleitzone: bool,
    _arbeitsl_v_beitr_midijob_arbeitnehmer_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _arbeitsl_v_beitr_midijob_arbeitnehmer_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitnehmer_m`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _arbeitsl_v_beitr_midijob_arbeitnehmer_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_info(end_date="2003-03-31", name_in_dag="arbeitsl_v_beitr_arbeitgeber_m")
def arbeitsl_v_beitr_arbeitgeber_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution until March 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if geringfügig_beschäftigt:
        out = 0.0
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_info(start_date="2003-04-01", name_in_dag="arbeitsl_v_beitr_arbeitgeber_m")
def arbeitsl_v_beitr_arbeitgeber_m_mit_midijob(
    geringfügig_beschäftigt: bool,
    in_gleitzone: bool,
    _arbeitsl_v_beitr_midijob_arbeitgeber_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution since April 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _arbeitsl_v_beitr_midijob_arbeitgeber_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitgeber_m`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _arbeitsl_v_beitr_midijob_arbeitgeber_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_info(start_date="2003-04-01")
def _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m(
    midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee's and employer's unemployment insurance contribution
    for midijobs.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = (
        midijob_bemessungsentgelt_m
        * 2
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    return out


@policy_info(
    start_date="2003-04-01",
    end_date="2022-09-30",
    name_in_dag="_arbeitsl_v_beitr_midijob_arbeitgeber_m",
)
def _arbeitsl_v_beitr_midijob_arbeitgeber_m_anteil_bruttolohn(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employers' unemployment insurance contribution for Midijobs until September
    2022.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.

    Returns
    -------

    """
    out = bruttolohn_m * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    return out


@policy_info(
    start_date="2022-10-01", name_in_dag="_arbeitsl_v_beitr_midijob_arbeitgeber_m"
)
def _arbeitsl_v_beitr_midijob_arbeitgeber_m_residuum(
    _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m: float,
    _arbeitsl_v_beitr_midijob_arbeitnehmer_m: float,
) -> float:
    """Employer's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        See :func:`_arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m`.
    _arbeitsl_v_beitr_midijob_arbeitnehmer_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitnehmer_m`.

    Returns
    -------

    """
    out = (
        _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _arbeitsl_v_beitr_midijob_arbeitnehmer_m
    )
    return out


@policy_info(
    start_date="2003-04-01",
    end_date="2022-09-30",
    name_in_dag="_arbeitsl_v_beitr_midijob_arbeitnehmer_m",
)
def _arbeitsl_v_beitr_midijob_arbeitnehmer_m_residuum(
    _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m: float,
    _arbeitsl_v_beitr_midijob_arbeitgeber_m: float,
) -> float:
    """Employee's unemployment insurance contribution for Midijobs until September
    2022.

    Parameters
    ----------
    _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        See :func:`_arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m`.
    _arbeitsl_v_beitr_midijob_arbeitgeber_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitgeber_m`.

    Returns
    -------

    """
    out = (
        _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _arbeitsl_v_beitr_midijob_arbeitgeber_m
    )
    return out


@policy_info(
    start_date="2022-10-01", name_in_dag="_arbeitsl_v_beitr_midijob_arbeitnehmer_m"
)
def _arbeitsl_v_beitr_midijob_arbeitnehmer_m_anteil_beitragspfl_einnahme(
    _midijob_beitragspfl_einnahme_arbeitnehmer_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    _midijob_beitragspfl_einnahme_arbeitnehmer_m
        See :func:`_midijob_beitragspfl_einnahme_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = (
        _midijob_beitragspfl_einnahme_arbeitnehmer_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    return out
