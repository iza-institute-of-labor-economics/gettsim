import numpy as np
import pandas as pd


def sozialv_beitr_m(
    pflegev_beitr_m, ges_krankenv_beitr_m, rentenv_beitr_m, arbeitsl_v_beitr_m
):
    """
    Sum of all social insurance contributions.

    Parameters
    ----------
    pflegev_beitr_m
    ges_krankenv_beitr_m
    rentenv_beitr_m
    arbeitsl_v_beitr_m

    Returns
    -------

    """
    out = pflegev_beitr_m + ges_krankenv_beitr_m + rentenv_beitr_m + arbeitsl_v_beitr_m

    return out.rename("sozialv_beitr_m")


def rentenv_beitr_m(
    geringfügig_beschäftigt, rentenv_beitr_regular_job, an_beitr_rentenv_midi_job,
):
    """
    Calculate the contribution for each individual to the pension insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
    rentenv_beitr_regular_job
    an_beitr_rentenv_midi_job

    Returns
    -------

    """

    out = pd.Series(
        index=geringfügig_beschäftigt.index, name="rentenv_beitr_m", dtype=float
    )

    # Set contribution 0 for people in minijob
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_rentenv_midi_job.index] = an_beitr_rentenv_midi_job
    out.loc[rentenv_beitr_regular_job.index] = rentenv_beitr_regular_job

    return out


def rentenv_beitr_m_tu(rentenv_beitr_m, tu_id):
    """
    Calculate the contribution of each tax unit to the pension insurance.

    Parameters
    ----------
    rentenv_beitr_m
    tu_id

    Returns
    -------

    """
    out = rentenv_beitr_m.groupby(tu_id).apply(sum)
    return out.rename("rentenv_beitr_m_tu")


def arbeitsl_v_beitr_m(
    geringfügig_beschäftigt, an_beitr_arbeitsl_v_midi_job, arbeitsl_v_regular_job,
):
    """
    Calculate the contribution for each individual to the unemployment insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
    an_beitr_arbeitsl_v_midi_job
    arbeitsl_v_regular_job

    Returns
    -------

    """
    out = pd.Series(
        index=geringfügig_beschäftigt.index, name="arbeitsl_v_beitr_m", dtype=float
    )

    # Set contribution 0 for people in minijob
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_arbeitsl_v_midi_job.index] = an_beitr_arbeitsl_v_midi_job
    out.loc[arbeitsl_v_regular_job.index] = arbeitsl_v_regular_job

    return out


def arbeitsl_v_regular_job(lohn_rente_regulär_beschäftigt, soz_vers_beitr_params):
    """
    Calculates unemployment insurance contributions for regualr jobs.

    Parameters
    ----------
    lohn_rente_regulär_beschäftigt : pd.Series
                                     Wage subject to pension and unemployment insurance
                                     contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = lohn_rente_regulär_beschäftigt.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )
    return out.rename("arbeitsl_v_regular_job")


def rentenv_beitr_regular_job(lohn_rente_regulär_beschäftigt, soz_vers_beitr_params):
    """
    Calculates pension insurance contributions for regualr jobs.

    Parameters
    ----------
    lohn_rente_regulär_beschäftigt : pd.Series
                                     Wage subject to pension and unemployment
                                     insurance contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = lohn_rente_regulär_beschäftigt.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )
    return out.rename("rentenv_beitr_regular_job")


def rentenv_beitr_bemess_grenze(wohnort_ost, soz_vers_beitr_params):
    """
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
    out = np.select(
        [wohnort_ost, ~wohnort_ost],
        [
            soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["ost"],
            soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["west"],
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


def ges_beitr_arbeitsl_v_midi_job(midi_job_bemessungsentgelt, soz_vers_beitr_params):
    """
    Calculating the sum of employee and employer unemployment insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = midi_job_bemessungsentgelt.multiply(
        2 * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )
    return out.rename("ges_beitr_arbeitsl_v_midi_job")


def ges_beitr_rentenv_midi_job(midi_job_bemessungsentgelt, soz_vers_beitr_params):
    """
    Calculating the sum of employee and employer pension insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = midi_job_bemessungsentgelt.multiply(
        2 * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )
    return out.rename("ges_beitr_rentenv_midi_job")


def ag_beitr_rentenv_midi_job(bruttolohn_m, in_gleitzone, soz_vers_beitr_params):
    """
    Calculating the employer pension insurance contribution.

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
    out = bruttolohn_m_in_gleitzone.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )
    return out.rename("ag_beitr_rentenv_midi_job")


def ag_beitr_arbeitsl_v_midi_job(bruttolohn_m, in_gleitzone, soz_vers_beitr_params):
    """
    Calculating the employer unemployment insurance contribution.

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
    out = bruttolohn_m_in_gleitzone.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )
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
