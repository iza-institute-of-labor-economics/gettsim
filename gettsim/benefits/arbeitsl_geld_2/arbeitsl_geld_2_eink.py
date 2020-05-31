def eink_anr_arbeitsl_geld_2(_arbeitsl_geld_2_eink, eink_anr_frei):
    """

    Parameters
    ----------
    _arbeitsl_geld_2_eink
    eink_anr_frei

    Returns
    -------

    """
    return (_arbeitsl_geld_2_eink - eink_anr_frei).clip(lower=0)


def arbeitsl_geld_2_brutto_eink_hh(_arbeitsl_geld_2_brutto_eink, hh_id):
    """

    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink
    hh_id

    Returns
    -------

    """
    return _arbeitsl_geld_2_brutto_eink.groupby(hh_id).sum()


def _arbeitsl_geld_2_eink(
    _arbeitsl_geld_2_brutto_eink, eink_st_m, soli_st_m, sozialv_beitr_m
):
    """
    Relevant net income of alg2. The function deducts income tax and social security
    contributions.

    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink
    eink_st_m
    soli_st_m
    sozialv_beitr_m

    Returns
    -------

    """
    return (
        _arbeitsl_geld_2_brutto_eink - eink_st_m - soli_st_m - sozialv_beitr_m
    ).clip(lower=0)


def eink_anr_arbeitsl_geld_2_hh(eink_anr_arbeitsl_geld_2, hh_id):
    """

    Parameters
    ----------
    eink_anr_arbeitsl_geld_2
    hh_id

    Returns
    -------

    """
    return eink_anr_arbeitsl_geld_2.groupby(hh_id).sum()


def _arbeitsl_geld_2_brutto_eink(
    bruttolohn_m,
    sonstig_eink_m,
    eink_selbstst_m,
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
    eink_selbstst_m
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
        + eink_selbstst_m
        + vermiet_eink_m
        + kapital_eink_m
        + ges_rente_m
        + arbeitsl_geld_m
        + elterngeld_m
    )
