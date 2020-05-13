import numpy as np
import pandas as pd


def mini_job_grenze(wohnort_ost, params):
    """
    Calculating the wage threshold for marginal employment.
    Parameters
    ----------
    wohnort_ost : pd.Series
                  Boolean variable indicating individual living in east germany.
    params : dict
             Dictionary containing the policy parameters

    Returns
    -------
    Pandas Series containing the income threshold for marginal employment.
    """
    out = np.select(
        [wohnort_ost, ~wohnort_ost],
        [
            params["geringfügige_eink_grenzen"]["mini_job"]["ost"],
            params["geringfügige_eink_grenzen"]["mini_job"]["west"],
        ],
    )
    return pd.Series(index=wohnort_ost.index, data=out, name="mini_job_grenze")


def geringfügig_beschäftigt(bruttolohn_m, mini_job_grenze):
    """
    Checking if individual earns less then marginal employment threshold.
    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    mini_job_grenze : np.array
                      Array containing the income threshold for marginal employment.

    Returns
    -------
    Pandas Series containing a boolean variable indicating if individual is marginal
    employed.

    """
    out = bruttolohn_m.le(mini_job_grenze)
    return out.rename("geringfügig_beschäftigt")


def in_gleitzone(bruttolohn_m, geringfügig_beschäftigt, params):
    """
    Checking if individual earns less then threshold for regular employment,
    but more then threshold of marginal employment.

    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    geringfügig_beschäftigt : pd.Series
                              Boolean Series indicating marginal employment.
    params

    Returns
    -------
    Pandas Series containing a boolean variable indicating if individual's wage is more
    then marginal employment threshold but less than regular employment.
    """
    out = (bruttolohn_m.le(params["geringfügige_eink_grenzen"]["midi_job"])) & (
        ~geringfügig_beschäftigt
    )
    return out.rename("in_gleitzone")


def midi_job_bemessungsentgelt(bruttolohn_m, in_gleitzone, params):
    """
    Calcualting the bemessungsentgelt for midi jobs which then will be subject to
    social insurances.

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
    # First calculate the factor F from the formula in § 163 (10) SGB VI.
    # Therefore sum the contributions which are the same for employee and employer
    allg_soz_vers_beitr = (
        params["soz_vers_beitr"]["rentenv"]
        + params["soz_vers_beitr"]["pflegev"]["standard"]
        + params["soz_vers_beitr"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = allg_soz_vers_beitr + params["soz_vers_beitr"]["ges_krankenv"]["an"]
    ag_anteil = allg_soz_vers_beitr + params["soz_vers_beitr"]["ges_krankenv"]["ag"]

    # Sum over the shares which are specific for midi jobs.
    pausch_mini = (
        params["ag_abgaben_geringf"]["ges_krankenv"]
        + params["ag_abgaben_geringf"]["rentenv"]
        + params["ag_abgaben_geringf"]["st"]
    )
    # Now calculate final factor
    f = round(pausch_mini / (an_anteil + ag_anteil), 4)

    # Now use the factor to calculate the overall bemessungsentgelt
    mini_job_anteil = f * params["geringfügige_eink_grenzen"]["mini_job"]["west"]
    lohn_über_mini = (
        bruttolohn_m.loc[in_gleitzone]
        - params["geringfügige_eink_grenzen"]["mini_job"]["west"]
    )
    gewichtete_midi_job_rate = (
        params["geringfügige_eink_grenzen"]["midi_job"]
        / (
            params["geringfügige_eink_grenzen"]["midi_job"]
            - params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        )
    ) - (
        params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        / (
            params["geringfügige_eink_grenzen"]["midi_job"]
            - params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        )
        * f
    )
    out = mini_job_anteil + lohn_über_mini * gewichtete_midi_job_rate
    return out.rename("midi_job_bemessungsentgelt")


def regulär_beschäftigt(bruttolohn_m, params):
    """
    Creating boolean Series indicating regular employment.
    Parameters
    ----------
    bruttolohn_m : pd.Series
                   The wage of each individual.
    params

    Returns
    -------

    """
    out = bruttolohn_m.ge(params["geringfügige_eink_grenzen"]["midi_job"])
    return out.rename("regulär_beschäftigt")
