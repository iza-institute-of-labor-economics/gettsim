"""Functions for modeling unemployment and pension insurance."""
import numpy as np


def sozialv_beitr_m(
    pflegev_beitr_m, ges_krankenv_beitr_m, rentenv_beitr_m, arbeitsl_v_beitr_m
):
    """Sum of all social insurance contributions.


    Parameters
    ----------
    pflegev_beitr_m
    ges_krankenv_beitr_m
    rentenv_beitr_m
    arbeitsl_v_beitr_m

    Returns
    -------

    """
    return pflegev_beitr_m + ges_krankenv_beitr_m + rentenv_beitr_m + arbeitsl_v_beitr_m


def rentenv_beitr_m(
    geringfügig_beschäftigt, _rentenv_beitr_regular_job, _an_beitr_rentenv_midi_job,
):
    """Contribution for each individual to the pension insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
    _rentenv_beitr_regular_job
    _an_beitr_rentenv_midi_job

    Returns
    -------

    """

    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[_an_beitr_rentenv_midi_job.index] = _an_beitr_rentenv_midi_job
    out.loc[_rentenv_beitr_regular_job.index] = _rentenv_beitr_regular_job

    return out


def rentenv_beitr_m_tu(rentenv_beitr_m, tu_id):
    """Calculate the contribution of each tax unit to the pension insurance.

    Parameters
    ----------
    rentenv_beitr_m
    tu_id

    Returns
    -------

    """
    return rentenv_beitr_m.groupby(tu_id).sum()


def arbeitsl_v_beitr_m(
    geringfügig_beschäftigt, _an_beitr_arbeitsl_v_midi_job, _arbeitsl_v_regular_job,
):
    """Calculate the contribution for each individual to the unemployment insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
    _an_beitr_arbeitsl_v_midi_job
    _arbeitsl_v_regular_job

    Returns
    -------

    """
    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions, for minijobs it remains 0
    out.loc[_an_beitr_arbeitsl_v_midi_job.index] = _an_beitr_arbeitsl_v_midi_job
    out.loc[_arbeitsl_v_regular_job.index] = _arbeitsl_v_regular_job

    return out


def _arbeitsl_v_regular_job(
    _ges_beitr_arbeitsl_v_midi_jobreturn, soz_vers_beitr_params
):
    """Calculates unemployment insurance contributions for regualr jobs.

    Parameters
    ----------
    _ges_beitr_arbeitsl_v_midi_jobreturn : pd.Series
                                     Wage subject to pension and unemployment insurance
                                     contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    return (
        _ges_beitr_arbeitsl_v_midi_jobreturn
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def _rentenv_beitr_regular_job(
    _ges_beitr_arbeitsl_v_midi_jobreturn, soz_vers_beitr_params
):
    """Calculates pension insurance contributions for regualr jobs.

    Parameters
    ----------
    _ges_beitr_arbeitsl_v_midi_jobreturn : pd.Series
                                     Wage subject to pension and unemployment
                                     insurance contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    return (
        _ges_beitr_arbeitsl_v_midi_jobreturn
        * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )


def _rentenv_beitr_bemess_grenze(wohnort_ost, soz_vers_beitr_params):
    """Threshold up to which income is subject to pension insurance.

    Selecting the threshold up to which income is subject to pension insurance
    contribution

    Parameters
    ----------
    wohnort_ost : pd.Series
                  Boolean variable indicating individual living in east germany.
    soz_vers_beitr_params

    Returns
    -------

    """
    return wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["ost"],
            False: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["west"],
        }
    )


def _ges_beitr_arbeitsl_v_midi_jobreturn(
    bruttolohn_m, _rentenv_beitr_bemess_grenze, regulär_beschäftigt
):
    """Calculate the wage, which is subject to pension insurance contributions.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    regulär_beschäftigt : pd.Series
                          Boolean Series indicating regular employment.

    _rentenv_beitr_bemess_grenze : pd.Series
                                 Threshold for wahe subcect to pension insurance
                                 contributions.


    Returns
    -------

    """
    bruttolohn_m_regulär_beschäftigt = bruttolohn_m.loc[regulär_beschäftigt]
    bemess_grenze = _rentenv_beitr_bemess_grenze.loc[regulär_beschäftigt]
    return bruttolohn_m_regulär_beschäftigt.clip(upper=bemess_grenze)


def _ges_beitr_arbeitsl_v_midi_job(midi_job_bemessungsentgelt, soz_vers_beitr_params):
    """Calculating the sum of employee and employer unemployment insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    return (
        midi_job_bemessungsentgelt
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def _ges_beitr_rentenv_midi_job(midi_job_bemessungsentgelt, soz_vers_beitr_params):
    """Calculating the sum of employee and employer pension insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    return (
        midi_job_bemessungsentgelt
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )


def _ag_beitr_rentenv_midi_job(bruttolohn_m, in_gleitzone, soz_vers_beitr_params):
    """Calculating the employer pension insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    out = (
        bruttolohn_m__in_gleitzone * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )
    return out


def _ag_beitr_arbeitsl_v_midi_job(bruttolohn_m, in_gleitzone, soz_vers_beitr_params):
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params

    Returns
    -------

    """
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    return (
        bruttolohn_m_in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def _an_beitr_rentenv_midi_job(_ges_beitr_rentenv_midi_job, _ag_beitr_rentenv_midi_job):
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    _ges_beitr_rentenv_midi_job : pd.Series
                                    Sum of employer and employee pension
                                    insurance contributions.

    _ag_beitr_rentenv_midi_job : pd.Series
                                   Employer pension insurance contribution.

    Returns
    -------

    """
    return _ges_beitr_rentenv_midi_job - _ag_beitr_rentenv_midi_job


def _an_beitr_arbeitsl_v_midi_job(
    _ges_beitr_arbeitsl_v_midi_job, _ag_beitr_arbeitsl_v_midi_job
):
    """Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    _ges_beitr_arbeitsl_v_midi_job : pd.Series
                                    Sum of employer and employee unemployment
                                    insurance contributions.

    _ag_beitr_arbeitsl_v_midi_job : pd.Series
                                   Employer unemployment insurance contribution.

    Returns
    -------

    """
    return _ges_beitr_arbeitsl_v_midi_job - _ag_beitr_arbeitsl_v_midi_job
