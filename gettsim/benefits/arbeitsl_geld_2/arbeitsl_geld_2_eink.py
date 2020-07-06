def arbeitsl_geld_2_eink_hh(arbeitsl_geld_2_eink, hh_id):
    """

    Parameters
    ----------
    arbeitsl_geld_2_eink
    hh_id

    Returns
    -------

    """
    return arbeitsl_geld_2_eink.groupby(hh_id).sum()


def arbeitsl_geld_2_eink(
    _arbeitsl_geld_2_brutto_eink,
    eink_st_tu,
    tu_id,
    soli_st_tu,
    _anz_erwachsene_tu,
    sozialv_beitr_m,
    eink_anr_frei,
):
    """

    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink
    sozialv_beitr_m
    eink_st_tu
    tu_id
    soli_st_tu
    _anz_erwachsene_tu
    eink_anr_frei

    Returns
    -------

    """
    return (
        _arbeitsl_geld_2_brutto_eink
        - tu_id.replace((eink_st_tu / _anz_erwachsene_tu) / 12)
        - tu_id.replace((soli_st_tu / _anz_erwachsene_tu) / 12)
        - sozialv_beitr_m
        - eink_anr_frei
    ).clip(lower=0)


def _arbeitsl_geld_2_brutto_eink_hh(_arbeitsl_geld_2_brutto_eink, hh_id):
    """

    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink
    hh_id

    Returns
    -------

    """
    return _arbeitsl_geld_2_brutto_eink.groupby(hh_id).sum()


def _arbeitsl_geld_2_brutto_eink(
    bruttolohn_m,
    sonstig_eink_m,
    eink_selbst_m,
    vermiet_eink_m,
    kapital_eink_m,
    ges_rente_m,
    arbeitsl_geld_m,
    elterngeld_m,
):
    """
    Calculating the gross income relevant for alg2.

    Parameters
    ----------
    bruttolohn_m
    sonstig_eink_m
    eink_selbst_m
    vermiet_eink_m
    kapital_eink_m
    ges_rente_m
    arbeitsl_geld_m
    elterngeld_m

    Returns
    -------

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
