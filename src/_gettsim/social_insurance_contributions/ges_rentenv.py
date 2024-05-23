from _gettsim.shared import policy_info


@policy_info(end_date="2003-03-31", name_in_dag="ges_rentenv_beitr_arbeitnehmer_m")
def ges_rentenv_beitr_arbeitnehmer_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's public pension insurance contribution.

    Before Midijob introduction in April 2003.

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
    ges_rentenv_beitr_regular_job_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if geringfügig_beschäftigt:
        out = 0.0
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


@policy_info(start_date="2003-04-01", name_in_dag="ges_rentenv_beitr_arbeitnehmer_m")
def ges_rentenv_beitr_arbeitnehmer_m_mit_midijob(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_midijob_arbeitnehmer_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    in_gleitzone: bool,
) -> float:
    """Employee's public pension insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_rentenv_beitr_midijob_arbeitnehmer_m
        See :func:`_ges_rentenv_beitr_midijob_arbeitnehmer_m`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    in_gleitzone
        See :func:`in_gleitzone`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_rentenv_beitr_midijob_arbeitnehmer_m
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


@policy_info(end_date="2003-03-31", name_in_dag="ges_rentenv_beitr_arbeitgeber_m")
def ges_rentenv_beitr_arbeitgeber_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    bruttolohn_m: float,
) -> float:
    """Employer's public pension insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if geringfügig_beschäftigt:
        out = bruttolohn_m * sozialv_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


@policy_info(start_date="2003-04-01", name_in_dag="ges_rentenv_beitr_arbeitgeber_m")
def ges_rentenv_beitr_arbeitgeber_m_mit_midijob(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_midijob_arbeitgeber_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    in_gleitzone: bool,
    bruttolohn_m: float,
) -> float:
    """Employer's public pension insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_rentenv_beitr_midijob_arbeitgeber_m
        See :func:`_ges_rentenv_beitr_midijob_arbeitgeber_m`.
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        _ges_rentenv_beitr_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if geringfügig_beschäftigt:
        out = bruttolohn_m * sozialv_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
    elif in_gleitzone:
        out = _ges_rentenv_beitr_midijob_arbeitgeber_m
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


@policy_info(start_date="2003-04-01")
def _ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m(
    midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employer and employee pension insurance contribution for midijobs.
    Midijobs were introduced in April 2003.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    ges_beitr_midijob = (
        midijob_bemessungsentgelt_m
        * 2
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )
    return ges_beitr_midijob


@policy_info(
    end_date="2022-09-30",
    name_in_dag="_ges_rentenv_beitr_midijob_arbeitgeber_m",
)
def _ges_rentenv_beitr_midijob_arbeitgeber_m_anteil_bruttolohn(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution until September 2022.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    return out


@policy_info(
    start_date="2022-10-01", name_in_dag="_ges_rentenv_beitr_midijob_arbeitgeber_m"
)
def _ges_rentenv_beitr_midijob_arbeitgeber_m_residuum(
    _ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m: float,
    _ges_rentenv_beitr_midijob_arbeitnehmer_m: float,
) -> float:
    """Employer's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    _ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        See :func:`_ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m`.
    _ges_rentenv_beitr_midijob_arbeitnehmer_m
        See :func:`_ges_rentenv_beitr_midijob_arbeitnehmer_m`.

    Returns
    -------

    """
    out = (
        _ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _ges_rentenv_beitr_midijob_arbeitnehmer_m
    )
    return out


@policy_info(
    end_date="2022-09-30",
    name_in_dag="_ges_rentenv_beitr_midijob_arbeitnehmer_m",
)
def _ges_rentenv_beitr_midijob_arbeitnehmer_m_residuum(
    _ges_rentenv_beitr_midijob_arbeitgeber_m: float,
    _ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m: float,
) -> float:
    """Employee's unemployment insurance contribution for midijobs until September 2022.

    Parameters
    ----------
    _ges_rentenv_beitr_midijob_arbeitgeber_m
        See :func:`_ges_rentenv_beitr_midijob_arbeitgeber_m`.
    _ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        See :func:`_ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m`.

    Returns
    -------

    """
    an_beitr_midijob = (
        _ges_rentenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _ges_rentenv_beitr_midijob_arbeitgeber_m
    )
    return an_beitr_midijob


@policy_info(
    start_date="2022-10-01", name_in_dag="_ges_rentenv_beitr_midijob_arbeitnehmer_m"
)
def _ges_rentenv_beitr_midijob_arbeitnehmer_m_anteil_beitragspfl_einnahme(
    _midijob_beitragspfl_einnahme_arbeitnehmer_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution for midijobs since October 2022.

    Parameters
    ----------
    _midijob_beitragspfl_einnahme_arbeitnehmer_m
        See :func:`_midijob_beitragspfl_einnahme_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    an_beitr_midijob = (
        _midijob_beitragspfl_einnahme_arbeitnehmer_m
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )
    return an_beitr_midijob


def _ges_rentenv_beitr_bruttolohn_m(
    bruttolohn_m: float,
    _ges_rentenv_beitr_bemess_grenze_m: float,
) -> float:
    """Wage subject to pension and unemployment insurance contributions.

    Parameters
    ----------
    bruttolohn_m
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    _ges_rentenv_beitr_bemess_grenze_m
        See :func:`_ges_rentenv_beitr_bemess_grenze_m`.


    Returns
    -------

    """
    out = min(bruttolohn_m, _ges_rentenv_beitr_bemess_grenze_m)
    return out
