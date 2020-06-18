def abgelt_st_tu(_zu_verst_kapital_eink_tu, abgelt_st_params):
    """Abgeltungssteuer per tax unit.

    Parameters
    ----------
    _zu_verst_kapital_eink_tu
    abgelt_st_params

    Returns
    -------

    """
    return abgelt_st_params["abgelt_st_satz"] * _zu_verst_kapital_eink_tu


def _zu_verst_kapital_eink_tu(
    brutto_eink_5_tu, _anz_erwachsene_tu, eink_st_abzuege_params
):
    """Taxable income per tax unit.

    Parameters
    ----------
    brutto_eink_5_tu
    _anz_erwachsene_tu
    eink_st_abzuege_params

    Returns
    -------

    """
    out = (
        brutto_eink_5_tu
        - _anz_erwachsene_tu
        * (
            eink_st_abzuege_params["sparerpauschbetrag"]
            + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
        )
    ).clip(lower=0)
    return out
