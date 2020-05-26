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
    _geringfügig_beschäftigt, _rentenv_beitr_regular_job, _an_beitr_rentenv_midi_job,
):
    """Contribution for each individual to the pension insurance.

    Parameters
    ----------
    _geringfügig_beschäftigt
    _rentenv_beitr_regular_job
    _an_beitr_rentenv_midi_job

    Returns
    -------

    """

    out = _geringfügig_beschäftigt.astype(float) * 0

    # Set contribution 0 for people in minijob
    out.loc[_geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[_an_beitr_rentenv_midi_job.index] = _an_beitr_rentenv_midi_job
    out.loc[_rentenv_beitr_regular_job.index] = _rentenv_beitr_regular_job

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
    return rentenv_beitr_m.groupby(tu_id).apply(sum)


def arbeitsl_v_beitr_m(
    _geringfügig_beschäftigt, _an_beitr_arbeitsl_v_midi_job, _arbeitsl_v_regular_job,
):
    """
    Calculate the contribution for each individual to the unemployment insurance.

    Parameters
    ----------
    _geringfügig_beschäftigt
    _an_beitr_arbeitsl_v_midi_job
    _arbeitsl_v_regular_job

    Returns
    -------

    """
    out = _geringfügig_beschäftigt.astype(float) * 0

    # Set contribution 0 for people in minijob
    out.loc[_geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[_an_beitr_arbeitsl_v_midi_job.index] = _an_beitr_arbeitsl_v_midi_job
    out.loc[_arbeitsl_v_regular_job.index] = _arbeitsl_v_regular_job

    return out


def _arbeitsl_v_regular_job(
    _ges_beitr_arbeitsl_v_midi_jobreturn, soz_vers_beitr_params
):
    """
    Calculates unemployment insurance contributions for regualr jobs.

    Parameters
    ----------
    _ges_beitr_arbeitsl_v_midi_jobreturn : pd.Series
                                     Wage subject to pension and unemployment insurance
                                     contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    return _ges_beitr_arbeitsl_v_midi_jobreturn.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )


def _rentenv_beitr_regular_job(
    _ges_beitr_arbeitsl_v_midi_jobreturn, soz_vers_beitr_params
):
    """
    Calculates pension insurance contributions for regualr jobs.

    Parameters
    ----------
    _ges_beitr_arbeitsl_v_midi_jobreturn : pd.Series
                                     Wage subject to pension and unemployment
                                     insurance contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    return _ges_beitr_arbeitsl_v_midi_jobreturn.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )


def _rentenv_beitr_bemess_grenze(wohnort_ost, soz_vers_beitr_params):
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
    return wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["ost"],
            False: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["west"],
        }
    )


def _ges_beitr_arbeitsl_v_midi_jobreturn(
    bruttolohn_m, _rentenv_beitr_bemess_grenze, _regulär_beschäftigt
):
    """
    Calculate the wage, which is subject to pension insurance contributions.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    _regulär_beschäftigt : pd.Series
                          Boolean Series indicating regular employment.

    _rentenv_beitr_bemess_grenze : pd.Series
                                 Threshold for wahe subcect to pension insurance
                                 contributions.


    Returns
    -------

    """
    bruttolohn_m__regulär_beschäftigt = bruttolohn_m.loc[_regulär_beschäftigt]
    bemess_grenze = _rentenv_beitr_bemess_grenze.loc[_regulär_beschäftigt]
    out = bruttolohn_m__regulär_beschäftigt.where(
        bruttolohn_m__regulär_beschäftigt < bemess_grenze, bemess_grenze
    )
    return out.rename("_ges_beitr_arbeitsl_v_midi_jobreturn")


def ges_beitr_arbeitsl_v_midi_job(_midi_job_bemessungsentgelt, soz_vers_beitr_params):
    """
    Calculating the sum of employee and employer unemployment insurance contribution.

    Parameters
    ----------
    _midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = _midi_job_bemessungsentgelt.multiply(
        2 * soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )
    return out.rename("ges_beitr_arbeitsl_v_midi_job")


def _ges_beitr_rentenv_midi_job(_midi_job_bemessungsentgelt, soz_vers_beitr_params):
    """
    Calculating the sum of employee and employer pension insurance contribution.

    Parameters
    ----------
    _midi_job_bemessungsentgelt : pd.Series
                                 The Bemessungsentgelt subject to social insurance
                                 contributions.
    soz_vers_beitr_params

    Returns
    -------

    """
    out = _midi_job_bemessungsentgelt.multiply(
        2 * soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )
    return out.rename("_ges_beitr_rentenv_midi_job")


def _ag_beitr_rentenv_midi_job(bruttolohn_m, _in_gleitzone, soz_vers_beitr_params):
    """
    Calculating the employer pension insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    _in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[_in_gleitzone]
    out = bruttolohn_m__in_gleitzone.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
    )
    return out.rename("_ag_beitr_rentenv_midi_job")


def _ag_beitr_arbeitsl_v_midi_job(bruttolohn_m, _in_gleitzone, soz_vers_beitr_params):
    """
    Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    _in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params

    Returns
    -------

    """
    bruttolohn_m__in_gleitzone = bruttolohn_m.loc[_in_gleitzone]
    out = bruttolohn_m__in_gleitzone.multiply(
        soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )
    return out.rename("_ag_beitr_arbeitsl_v_midi_job")


def _an_beitr_rentenv_midi_job(_ges_beitr_rentenv_midi_job, _ag_beitr_rentenv_midi_job):
    """
    Calculating the employer unemployment insurance contribution.

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
    out = _ges_beitr_rentenv_midi_job - _ag_beitr_rentenv_midi_job
    return out.rename("_an_beitr_rentenv_midi_job")


def _an_beitr_arbeitsl_v_midi_job(
    ges_beitr_arbeitsl_v_midi_job, _ag_beitr_arbeitsl_v_midi_job
):
    """
    Calculating the employer unemployment insurance contribution.

    Parameters
    ----------
    ges_beitr_arbeitsl_v_midi_job : pd.Series
                                    Sum of employer and employee unemployment
                                    insurance contributions.

    _ag_beitr_arbeitsl_v_midi_job : pd.Series
                                   Employer unemployment insurance contribution.

    Returns
    -------

    """
    out = ges_beitr_arbeitsl_v_midi_job - _ag_beitr_arbeitsl_v_midi_job
    return out.rename("_an_beitr_arbeitsl_v_midi_job")
