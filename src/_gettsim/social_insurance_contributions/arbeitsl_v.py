"""Functions for modeling unemployment and pension insurance."""
from _gettsim.shared import dates_active


def sozialv_beitr_m(
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


def sozialv_beitr_arbeitg_m(
    ges_pflegev_beitr_arbeitg_m: float,
    ges_krankenv_beitr_arbeitg_m: float,
    ges_rentenv_beitr_arbeitg_m: float,
    arbeitsl_v_beitr_arbeitg_m: float,
) -> float:
    """Sum of all social insurance contributions of the respective employer.

    Parameters
    ----------
    ges_pflegev_beitr_arbeitg_m
        See :func:`ges_pflegev_beitr_arbeitg_m`.
    ges_krankenv_beitr_arbeitg_m
        See :func:`ges_krankenv_beitr_arbeitg_m`.
    ges_rentenv_beitr_arbeitg_m
        See :func:`ges_rentenv_beitr_arbeitg_m`.
    arbeitsl_v_beitr_arbeitg_m
        See :func:`arbeitsl_v_beitr_arbeitg_m`.

    Returns
    -------

    """
    out = (
        ges_pflegev_beitr_arbeitg_m
        + ges_krankenv_beitr_arbeitg_m
        + ges_rentenv_beitr_arbeitg_m
        + arbeitsl_v_beitr_arbeitg_m
    )
    return out


def _sozialv_beitr_arbeitn_arbeitg_m(
    sozialv_beitr_m: float,
    sozialv_beitr_arbeitg_m: float,
) -> float:
    """Sum of all social insurance contributions of an employer and employee.

    Parameters
    ----------
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.
    sozialv_beitr_arbeitg_m
        See :func:`sozialv_beitr_arbeitg_m`.
    Returns
    -------

    """
    out = sozialv_beitr_m + sozialv_beitr_arbeitg_m
    return out


def arbeitsl_v_beitr_m(
    geringfügig_beschäftigt: bool,
    in_gleitzone: bool,
    _arbeitsl_v_beitr_midijob_arbeitn_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
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
        out = _arbeitsl_v_beitr_midijob_arbeitn_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


def arbeitsl_v_beitr_arbeitg_m(
    geringfügig_beschäftigt: bool,
    in_gleitzone: bool,
    _arbeitsl_v_beitr_midijob_arbeitg_m: float,
    _ges_rentenv_beitr_bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Contribution of the respective employer to the unemployment insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _arbeitsl_v_beitr_midijob_arbeitg_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitg_m`.
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
        out = _arbeitsl_v_beitr_midijob_arbeitg_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


def _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m(
    midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the sum of employee and employer unemployment insurance contribution
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


@dates_active(
    end="2022-09-30",
    change_name="_arbeitsl_v_beitr_midijob_arbeitg_m",
)
def _arbeitsl_v_beitr_midijob_arbeitg_m_anteil_bruttolohn(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the employer unemployment insurance contribution until September
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


@dates_active(start="2022-10-01", change_name="_arbeitsl_v_beitr_midijob_arbeitg_m")
def _arbeitsl_v_beitr_midijob_arbeitg_m_residuum(
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
    out = (
        _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m
        - _arbeitsl_v_beitr_midijob_arbeitn_m
    )
    return out


@dates_active(
    end="2022-09-30",
    change_name="_arbeitsl_v_beitr_midijob_arbeitn_m",
)
def _arbeitsl_v_beitr_midijob_arbeitn_m_residuum(
    _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m: float,
    _arbeitsl_v_beitr_midijob_arbeitg_m: float,
) -> float:
    """Calculating the employee unemployment insurance contribution until September
    2022.

    Parameters
    ----------
    _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m`.
    _arbeitsl_v_beitr_midijob_arbeitg_m
        See :func:`_arbeitsl_v_beitr_midijob_arbeitg_m`.

    Returns
    -------

    """
    out = (
        _arbeitsl_v_beitr_midijob_sum_arbeitn_arbeitg_m
        - _arbeitsl_v_beitr_midijob_arbeitg_m
    )
    return out


@dates_active(start="2022-10-01", change_name="_arbeitsl_v_beitr_midijob_arbeitn_m")
def _arbeitsl_v_beitr_midijob_arbeitn_m_anteil_beitragspfl_einnahme(
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
    out = (
        _midijob_beitragspfl_einnahme_arbeitn_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
    return out
