from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def abgelt_st_tu(
    zu_verst_kapitaleink_tu: FloatSeries, abgelt_st_params: dict
) -> FloatSeries:
    """Calculate abgeltungssteuer per tax unit.

    Parameters
    ----------
    zu_verst_kapitaleink_tu
        See :func:`zu_verst_kapitaleink_tu`.
    abgelt_st_params
        See params documentation :ref:`abgelt_st_params <abgelt_st_params>`.

    Returns
    -------

    """
    return abgelt_st_params["satz"] * zu_verst_kapitaleink_tu


def zu_verst_kapitaleink_tu(
    kapitaleink_brutto_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
    """Calculate taxable income per tax unit.

    Parameters
    ----------
    kapitaleink_brutto_tu
        See :func:`kapitaleink_brutto_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    out = (
        kapitaleink_brutto_tu
        - anz_erwachsene_tu
        * (
            eink_st_abzüge_params["sparerpauschbetrag"]
            + eink_st_abzüge_params["sparer_werbungskosten_pauschbetrag"]
        )
    ).clip(lower=0)
    return out
