from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def _mini_job_grenze(wohnort_ost: BoolSeries, soz_vers_beitr_params: BoolSeries) -> FloatSeries:
    """Sum wage threshold for marginal employment exempt from Social Insurance contributions.

    Parameters
    ----------
    
    wohnort_ost 
        See :ref:`wohnort_ost`. 
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.
           

    Returns
    ------- 
    FloatSeries with the sum of wage threshold. 
    """
    
    
    
    
    
     
    wohnort_ost : pd.Series
        Boolean variable for whether individual lives in East Germany.
    soz_vers_beitr_params : dict
        Dictionary containing the policy parameters
    
    
    
    
    Pandas Series containing the income threshold for marginal employment.
    """
    return wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["ost"],
            False: soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"][
                "west"
            ],
        }
    )







def _geringfügig_beschäftigt(bruttolohn_m: FloatSeries, _mini_job_grenze: FloatSeries) -> BoolSeries:
    """Check if individual earns less than marginal employment threshold.
    
    Parameters
    ---------- 
    
    bruttolohn_m
        See :ref:`bruttolohn_m`. 
    _mini_job_grenze
        See :ref:`_mini_job_grenze`.    
   

    Returns
    ------- 
    BoolSeries indicating if person earns less than marginal employment threshold.
    """
    
    
    
    
    
     bruttolohn_m : pd.Series
                   The wage of each individual.
    _mini_job_grenze : np.array
                      Array containing the income threshold for marginal employment.
    
    
    
    
    Pandas Series containing a boolean variable indicating if individual is marginal
    employed.

    """
    return bruttolohn_m <= _mini_job_grenze 







def _in_gleitzone(bruttolohn_m: FloatSeries, _geringfügig_beschäftigt: BoolSeries, soz_vers_beitr_params: FloatSeries) -> BoolSeries:
    """Check if individual earns less than threshold for regular employment, but more than threshold of marginal employment.

    Parameters
    ---------- 
    
    bruttolohn_m 
        See :ref:`bruttolohn_m`. 
    _geringfügig_beschäftigt
        See :ref:`_geringfügig_beschäftigt`. 
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.
    
    
    
    Returns
    ------- 
    BoolSeries indicating persons which earns less than threshold for regular employment, but more then threshold of marginal employment.
    """
    
    
    
    bruttolohn_m : pd.Series
                   The wage of each individual.
    _geringfügig_beschäftigt : pd.Series
                              Boolean Series indicating marginal employment.
    soz_vers_beitr_params
    
    
    
    
    
    
    Pandas Series containing a boolean variable indicating if individual's wage is more
    then marginal employment threshold but less than regular employment.
    """
    return (
        bruttolohn_m <= soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
    ) & (~_geringfügig_beschäftigt)







def _midi_job_bemessungsentgelt(bruttolohn_m: FloatSeries, _in_gleitzone: BoolSeries, soz_vers_beitr_params: FloatSeries) -> FloatSeries:
    """Sum the bemessungsentgelt for midi jobs which then will be subject to social insurances.

    Parameters
    ---------- 
    
    bruttolohn_m 
        See :ref:`bruttolohn_m`.
    _in_gleitzone 
        See :ref:`_in_gleitzone`. 
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.
    

    Returns
    ------- 
    FloatSeries with the sum of the bemessungsentgelt for midi jobs which then will be subject to social insurances.
    """






 bruttolohn_m : pd.Series
                   The wage of each individual.
    _in_gleitzone : pd.Series
                   Boolean Series indicating midi job regulation.
    soz_vers_beitr_params


    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI.
    # Therefore sum the contributions which are the same for employee and employer
    allg_soz_vers_beitr = (
        soz_vers_beitr_params["soz_vers_beitr"]["rentenv"]
        + soz_vers_beitr_params["soz_vers_beitr"]["pflegev"]["standard"]
        + soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = (
        allg_soz_vers_beitr
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
    )
    ag_anteil = (
        allg_soz_vers_beitr
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )

    # Sum over the shares which are specific for midi jobs.
    pausch_mini = (
        soz_vers_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["rentenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["st"]
    )
    # Now calculate final factor
    f = round(pausch_mini / (an_anteil + ag_anteil), 4)

    # Now use the factor to calculate the overall bemessungsentgelt
    mini_job_anteil = (
        f * soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
    )
    lohn_über_mini = (
        bruttolohn_m.loc[_in_gleitzone]
        - soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
    )
    gewichtete_midi_job_rate = (
        soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
            - soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        )
    ) - (
        soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
            - soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        )
        * f
    )
    return mini_job_anteil + lohn_über_mini * gewichtete_midi_job_rate






def _regulär_beschäftigt(bruttolohn_m: FloatSeries, soz_vers_beitr_params: BoolSeries) -> BoolSeries:
    """Check if person is employed or not. 

    Parameters
    ---------- 
    
    bruttolohn_m 
        See :ref:`bruttolohn_m`. 
    soz_vers_beitr_params
        See :ref:`soz_vers_beitr_params`.
    
 
    Returns
    ------- 
    BoolSeries indicating employed persons. 
    """
    
    
    
    bruttolohn_m : pd.Series
                   The wage of each individual.
    soz_vers_beitr_params
    
    
    bool

    """
    return (
        bruttolohn_m >= soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
    )
