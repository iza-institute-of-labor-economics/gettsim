from _gettsim.shared import dates_active


def ges_rentenv_beitr_m(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_midijob_arbeitn_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    in_gleitzone: bool,
) -> float:
    """Contribution for each individual to the pension insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    _ges_rentenv_beitr_midijob_arbeitn_m
        See :func:`_ges_rentenv_beitr_midijob_arbeitn_m`.
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
        out = _ges_rentenv_beitr_midijob_arbeitn_m
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


def ges_rentenv_beitr_arbeitg_m(
    geringfügig_beschäftigt: bool,
    _ges_rentenv_beitr_midijob_arbeitg_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    in_gleitzone: bool,
    bruttolohn_m: float,
) -> float:
    """Contribution of the respective employer to the pension insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_rentenv_beitr_midijob_arbeitg_m
        See :func:`_ges_rentenv_beitr_midijob_arbeitg_m`.
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
        out = _ges_rentenv_beitr_midijob_arbeitg_m
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


def _ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m(
    midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the sum of employee and employer pension insurance contribution for
    midijobs.

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


@dates_active(
    end="2022-09-30",
    change_name="_ges_rentenv_beitr_midijob_arbeitg_m",
)
def _ges_rentenv_beitr_midijob_arbeitg_m_anteil_bruttolohn(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the employer unemployment insurance contribution until September
    2022.

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


@dates_active(start="2022-10-01", change_name="_ges_rentenv_beitr_midijob_arbeitg_m")
def _ges_rentenv_beitr_midijob_arbeitg_m_residuum(
    _ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m: float,
    _ges_rentenv_beitr_midijob_arbeitn_m: float,
) -> float:
    """Calculating the employer unemployment insurance contribution since October 2022.

    Parameters
    ----------
    _ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m`.
    _ges_rentenv_beitr_midijob_arbeitn_m
        See :func:`_ges_rentenv_beitr_midijob_arbeitn_m`.

    Returns
    -------

    """
    out = (
        _ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m
        - _ges_rentenv_beitr_midijob_arbeitn_m
    )
    return out


@dates_active(
    end="2022-09-30",
    change_name="_ges_rentenv_beitr_midijob_arbeitn_m",
)
def _ges_rentenv_beitr_midijob_arbeitn_m_residuum(
    _ges_rentenv_beitr_midijob_arbeitg_m: float,
    _ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m: float,
) -> float:
    """Calculating the employee unemployment insurance contribution until September
    2022.

    Parameters
    ----------
    _ges_rentenv_beitr_midijob_arbeitg_m
        See :func:`_ges_rentenv_beitr_midijob_arbeitg_m`.
    _ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m`.

    Returns
    -------

    """
    an_beitr_midijob = (
        _ges_rentenv_beitr_midijob_sum_arbeitn_arbeitg_m
        - _ges_rentenv_beitr_midijob_arbeitg_m
    )
    return an_beitr_midijob


@dates_active(start="2022-10-01", change_name="_ges_rentenv_beitr_midijob_arbeitn_m")
def _ges_rentenv_beitr_midijob_arbeitn_m_anteil_beitragspfl_einnahme(
    _midijob_beitragspfl_einnahme_arbeitn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the employee unemployment insurance contribution since October 2022.

    Parameters
    ----------
    _midijob_beitragspfl_einnahme_arbeitn_m
        See :func:`_midijob_beitragspfl_einnahme_arbeitn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    an_beitr_midijob = (
        _midijob_beitragspfl_einnahme_arbeitn_m
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )
    return an_beitr_midijob


def _ges_rentenv_beitr_bruttolohn_m(
    bruttolohn_m: float,
    _ges_rentenv_beitr_bemess_grenze_m: float,
) -> float:
    """Calculate the wage subject to pension and unemployment insurance contributions.

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
