"""Contributions to the unemployment insurance."""

from _gettsim.shared import policy_info


@policy_info(end_date="2003-03-31", name_in_dag="arbeitsl_v_beitr_arbeitnehmer_m")
def arbeitsl_v_beitr_arbeitnehmer_m_vor_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
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
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_info(start_date="2003-04-01", name_in_dag="arbeitsl_v_beitr_arbeitnehmer_m")
def arbeitsl_v_beitr_arbeitnehmer_m_mit_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    einkommensgrenzen__in_gleitzone: bool,
    _arbeitsl_v_beitr_midijob_arbeitnehmer_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
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
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = _arbeitsl_v_beitr_midijob_arbeitnehmer_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_info(end_date="2003-03-31", name_in_dag="arbeitsl_v_beitr_arbeitgeber_m")
def arbeitsl_v_beitr_arbeitgeber_m_vor_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution until March 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
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
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_info(start_date="2003-04-01", name_in_dag="arbeitsl_v_beitr_arbeitgeber_m")
def arbeitsl_v_beitr_arbeitgeber_m_mit_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    einkommensgrenzen__in_gleitzone: bool,
    _arbeitsl_v_beitr_midijob_arbeitgeber_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution since April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
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
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = _arbeitsl_v_beitr_midijob_arbeitgeber_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_info(start_date="2003-04-01")
def _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m(
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee's and employer's unemployment insurance contribution
    for midijobs.

    Parameters
    ----------
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    return (
        einkommensgrenzen__midijob_bemessungsentgelt_m
        * 2
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )


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
    return bruttolohn_m * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]


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
    return (
        _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _arbeitsl_v_beitr_midijob_arbeitnehmer_m
    )


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
    return (
        _arbeitsl_v_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _arbeitsl_v_beitr_midijob_arbeitgeber_m
    )


@policy_info(
    start_date="2022-10-01", name_in_dag="_arbeitsl_v_beitr_midijob_arbeitnehmer_m"
)
def _arbeitsl_v_beitr_midijob_arbeitnehmer_m_anteil_beitragspfl_einnahme(
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m
        See :func:`einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    return (
        einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
