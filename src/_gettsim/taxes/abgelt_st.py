from _gettsim.shared import dates_active


@dates_active(start="2009-01-01")
def abgelt_st_y_tu(zu_verst_kapitaleink_y_tu: float, abgelt_st_params: dict) -> float:
    """Calculate abgeltungssteuer on tax unit level.

    Parameters
    ----------
    zu_verst_kapitaleink_y_tu
        See :func:`zu_verst_kapitaleink_y_tu`.
    abgelt_st_params
        See params documentation :ref:`abgelt_st_params <abgelt_st_params>`.

    Returns
    -------

    """
    return abgelt_st_params["satz"] * zu_verst_kapitaleink_y_tu


def zu_verst_kapitaleink_y_tu(
    kapitaleink_brutto_y_tu: float,
    anz_erwachsene_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate taxable income on tax unit level.

    Parameters
    ----------
    kapitaleink_brutto_y_tu
        See :func:`kapitaleink_brutto_y_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = kapitaleink_brutto_y_tu - anz_erwachsene_tu * (
        eink_st_abzuege_params["sparerpauschbetrag"]
        + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    )

    return max(out, 0.0)
