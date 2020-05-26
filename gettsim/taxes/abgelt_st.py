def abgelt_st_m(gem_veranlagt, kind, abgelt_st_m_tu, tu_id):
    """ Capital Income Tax / Abgeltungsteuer
        since 2009, captial income is taxed with a flatrate of 25%.
    """
    # First assign all individuals the tax unit value
    out = tu_id.replace(abgelt_st_m_tu)
    # Half it for married couples
    out.loc[gem_veranlagt] /= 2
    # Set it to zero for kids
    out.loc[kind] = 0
    return out


def abgelt_st_m_tu(_zu_verst_kapital_eink_tu, abgelt_st_params):
    """

    Parameters
    ----------
    _zu_verst_kapital_eink_tu
    abgelt_st_params

    Returns
    -------

    """
    return abgelt_st_params["abgelt_st_satz"] * _zu_verst_kapital_eink_tu


def _zu_verst_kapital_eink_tu(
    brutto_eink_5_tu, gemeinsam_veranlagte_tu, eink_st_abzuege_params
):
    """

    Parameters
    ----------
    brutto_eink_5_tu
    gemeinsam_veranlagte_tu
    eink_st_abzuege_params

    Returns
    -------

    """
    multi_plikations_faktor = gemeinsam_veranlagte_tu.replace({True: 2, False: 1})
    out = (
        brutto_eink_5_tu
        - multi_plikations_faktor
        * (
            eink_st_abzuege_params["sparerpauschbetrag"]
            + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
        )
    ).clip(lower=0)
    return out
