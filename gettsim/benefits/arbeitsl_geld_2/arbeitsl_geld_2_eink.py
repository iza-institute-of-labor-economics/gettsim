def arbeitsl_geld_2_eink_hh(arbeitsl_geld_2_eink: FloatSeries, 
                            hh_id: IntSeries) -> FloatSeries:
    """Sum up the income per household by unemployment insurance.

    Parameters
    ----------
    arbeitsl_geld_2_eink
        See :func:`arbeitsl_geld_2_eink`.
    hh_id
        See :ref:`hh_id`.
  
    Returns
    -------
    FloatSeries returns the income given by unemployment insurance per household. 
    """
    return arbeitsl_geld_2_eink.groupby(hh_id).sum()


def arbeitsl_geld_2_eink(
    _arbeitsl_geld_2_brutto_eink: FloatSeries,
    eink_st_tu: FloatSeries,
    tu_id: IntSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_m: FloatSeries,
    eink_anr_frei: FloatSeries,
) -> FloatSeries:
    
    """Sum up the income of a person by unemployment insurance.

    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink 
        See :func:`arbeitsl_geld_2_eink`.
    sozialv_beitr_m 
        See :func:`sozialv_beitr_m`.
    eink_st_tu 
        See :func:`eink_st_tu`. 
    tu_id 
        See :ref:`tu_id`.
    soli_st_tu 
        See :func:`soli_st_tu`.
    anz_erwachsene_tu 
        See :func:`anz_erwachsene_tu`.
    eink_anr_frei 
        See :func:`eink_anr_frei`.

    Returns
    -------
    """Float Series with the income of a person by unemployment insurance. 
    
    return (
        _arbeitsl_geld_2_brutto_eink
        - tu_id.replace((eink_st_tu / anz_erwachsene_tu) / 12)
        - tu_id.replace((soli_st_tu / anz_erwachsene_tu) / 12)
        - sozialv_beitr_m
        - eink_anr_frei
    ).clip(lower=0)


def _arbeitsl_geld_2_brutto_eink_hh(_arbeitsl_geld_2_brutto_eink: FloatSeries, 
                                    hh_id: IntSeries
   ) -> FloatSeries:
    
    """Income by unemployment insurance before tax. 
    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink 
        See :func:`_arbeitsl_geld_2_brutto_eink`.
    hh_id 
        See :ref:`hh_id`.

    Returns
    -------
    Float Series with the income of a person by unemployment insurance before tax. 
    """
    return _arbeitsl_geld_2_brutto_eink.groupby(hh_id).sum()


def _arbeitsl_geld_2_brutto_eink(
    bruttolohn_m: FloatSeries,
    sonstig_eink_m: FloatSeries,
    eink_selbst_m: FloatSeries,
    vermiet_eink_m: FloatSeries,
    kapital_eink_m: FloatSeries,
    ges_rente_m: FloatSeries,
    arbeitsl_geld_m: FloatSeries ,
    elterngeld_m: FloatSeries,
) -> FloatSeries:
    
    """Calculating the gross income relevant for alg2.

    Parameters
    ----------
    bruttolohn_m 
        See :ref:`hh_id`.
    sonstig_eink_m 
        See :ref:`sonstig_eink_m`. 
    eink_selbst_m 
        See :ref:`eink_selbst_m`. 
    vermiet_eink_m 
        See :ref:`vermiet_eink_m`. 
    kapital_eink_m 
        See :ref:`kapital_eink_m`. 
    ges_rente_m 
        See :ref:`ges_rente_m`. 
    arbeitsl_geld_m 
        See :func:`arbeitsl_geld_m`. 
    elterngeld_m 
        See :func:`elterngeld_m`. 

    Returns
    -------
    FloatSeries with the income by unemployment insurance before tax. 
    """
    return (
        bruttolohn_m
        + sonstig_eink_m
        + eink_selbst_m
        + vermiet_eink_m
        + kapital_eink_m
        + ges_rente_m
        + arbeitsl_geld_m
        + elterngeld_m
    )
