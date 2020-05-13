import numpy as np
import pandas as pd


def sozialv_beitr_m(
    pflegev_beitr_m, ges_krankenv_beitr_m, rentenv_beitr_m, arbeitsl_v_beitr_m
):
    sozialv_beitr_m = (
        pflegev_beitr_m + ges_krankenv_beitr_m + rentenv_beitr_m + arbeitsl_v_beitr_m
    )

    return pd.Series(data=sozialv_beitr_m, name="sozialv_beitr_m")


def rentenv_beitr_m(
    geringfügig_beschäftigt, rentenv_beitr_regular_job, an_beitr_rentenv_midi_job,
):

    rentenv_beitr_m = pd.Series(
        index=geringfügig_beschäftigt.index, name="rentenv_beitr_m", dtype=float
    )

    # Set contribution 0 for people in minijob
    rentenv_beitr_m.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    rentenv_beitr_m.loc[an_beitr_rentenv_midi_job.index] = an_beitr_rentenv_midi_job
    rentenv_beitr_m.loc[rentenv_beitr_regular_job.index] = rentenv_beitr_regular_job

    return rentenv_beitr_m


def arbeitsl_v_beitr_m(
    geringfügig_beschäftigt, an_beitr_arbeitsl_v_midi_job, arbeitsl_v_regular_job,
):
    arbeitsl_v_beitr_m = pd.Series(
        index=geringfügig_beschäftigt.index, name="arbeitsl_v_beitr_m", dtype=float
    )

    # Set contribution 0 for people in minijob
    arbeitsl_v_beitr_m.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    arbeitsl_v_beitr_m.loc[
        an_beitr_arbeitsl_v_midi_job.index
    ] = an_beitr_arbeitsl_v_midi_job
    arbeitsl_v_beitr_m.loc[arbeitsl_v_regular_job.index] = arbeitsl_v_regular_job

    return arbeitsl_v_beitr_m


def arbeitsl_v_regular_job(lohn_rente_regulär_beschäftigt, params):
    """
    Calculates unemployment insurance contributions for regualr jobs.

    Parameters
    ----------
    lohn_rente_regulär_beschäftigt : pd.Series
                                     Wage subject to pension and unemployment insurance
                                     contributions.
    params

    Returns
    -------

    """
    out = lohn_rente_regulär_beschäftigt.multiply(
        params["soz_vers_beitr"]["arbeitsl_v"]
    )
    return out.rename("arbeitsl_v_regular_job")


def rentenv_beitr_regular_job(lohn_rente_regulär_beschäftigt, params):
    """
    Calculates pension insurance contributions for regualr jobs.

    Parameters
    ----------
    lohn_rente_regulär_beschäftigt : pd.Series
                                     Wage subject to pension and unemployment
                                     insurance contributions.
    params

    Returns
    -------

    """
    out = lohn_rente_regulär_beschäftigt.multiply(params["soz_vers_beitr"]["rentenv"])
    return out.rename("rentenv_beitr_regular_job")


def rentenv_beitr_bemess_grenze(wohnort_ost, params):
    """
    Selecting the threshold up to which income is subject to pension insurance
    contribution

    Parameters
    ----------
    wohnort_ost : pd.Series
                  Boolean variable indicating individual living in east germany.
    params

    Returns
    -------

    """
    out = np.select(
        [wohnort_ost, ~wohnort_ost],
        [
            params["beitr_bemess_grenze"]["rentenv"]["ost"],
            params["beitr_bemess_grenze"]["rentenv"]["west"],
        ],
    )
    return pd.Series(
        index=wohnort_ost.index, data=out, name="rentenv_beitr_bemess_grenze"
    )


def lohn_rente_regulär_beschäftigt(
    bruttolohn_m, rentenv_beitr_bemess_grenze, regulär_beschäftigt
):
    """
    Calculate the wage, which is subject to pension insurance contributions.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    regulär_beschäftigt : pd.Series
                          Boolean Series indicating regular employment.

    rentenv_beitr_bemess_grenze : pd.Series
                                 Threshold for wahe subcect to pension insurance
                                 contributions.


    Returns
    -------

    """
    bruttolohn_m_regulär_beschäftigt = bruttolohn_m.loc[regulär_beschäftigt]
    bemess_grenze = rentenv_beitr_bemess_grenze.loc[regulär_beschäftigt]
    out = bruttolohn_m_regulär_beschäftigt.where(
        bruttolohn_m_regulär_beschäftigt < bemess_grenze, bemess_grenze
    )
    return out.rename("lohn_rente_regulär_beschäftigt")


def ges_beitr_arbeitsl_v_midi_job(midi_job_bemessungsentgelt, params):
    """
    Calculating the sum of employee and employer unemployment insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    params

    Returns
    -------

    """
    out = midi_job_bemessungsentgelt.multiply(
        2 * params["soz_vers_beitr"]["arbeitsl_v"]
    )
    return out.rename("ges_beitr_arbeitsl_v_midi_job")


def ges_beitr_rentenv_midi_job(midi_job_bemessungsentgelt, params):
    """
    Calculating the sum of employee and employer pension insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    params

    Returns
    -------

    """
    out = midi_job_bemessungsentgelt.multiply(2 * params["soz_vers_beitr"]["rentenv"])
    return out.rename("ges_beitr_rentenv_midi_job")


def ag_beitr_rentenv_midi_job(bruttolohn_m, in_gleitzone, params):
    """
    Calculating the employer pension insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    params

    Returns
    -------

    """
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    out = bruttolohn_m_in_gleitzone.multiply(params["soz_vers_beitr"]["rentenv"])
    return out.rename("ag_beitr_rentenv_midi_job")


def ag_beitr_arbeitsl_v_midi_job(bruttolohn_m, in_gleitzone, params):
    """
    Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    params

    Returns
    -------

    """
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    out = bruttolohn_m_in_gleitzone.multiply(params["soz_vers_beitr"]["arbeitsl_v"])
    return out.rename("ag_beitr_arbeitsl_v_midi_job")


def an_beitr_rentenv_midi_job(ges_beitr_rentenv_midi_job, ag_beitr_rentenv_midi_job):
    """
    Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    ges_beitr_rentenv_midi_job : pd.Series
                                    Sum of employer and employee pension
                                    insurance contributions.

    ag_beitr_rentenv_midi_job : pd.Series
                                   Employer pension insurance contribution.

    Returns
    -------

    """
    out = ges_beitr_rentenv_midi_job - ag_beitr_rentenv_midi_job
    return out.rename("an_beitr_rentenv_midi_job")


def an_beitr_arbeitsl_v_midi_job(
    ges_beitr_arbeitsl_v_midi_job, ag_beitr_arbeitsl_v_midi_job
):
    """
    Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    ges_beitr_arbeitsl_v_midi_job : pd.Series
                                    Sum of employer and employee unemployment
                                    insurance contributions.

    ag_beitr_arbeitsl_v_midi_job : pd.Series
                                   Employer unemployment insurance contribution.

    Returns
    -------

    """
    out = ges_beitr_arbeitsl_v_midi_job - ag_beitr_arbeitsl_v_midi_job
    return out.rename("an_beitr_arbeitsl_v_midi_job")
