from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def abgelt_st_tu(
    zu_verst_kapital_eink_tu: FloatSeries, abgelt_st_params: dict
) -> FloatSeries:
    """Abgeltungssteuer per tax unit.

    Parameters
    ----------
    zu_verst_kapital_eink_tu
        See :func:`zu_verst_kapital_eink_tu`.
    abgelt_st_params
        See :ref:`abgelt_st_params`.

    Returns
    -------

    """
    return abgelt_st_params["abgelt_st_satz"] * zu_verst_kapital_eink_tu


def zu_verst_kapital_eink_tu(
    brutto_eink_5_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    eink_st_abzuege_params: dict,
) -> FloatSeries:
    """Taxable income per tax unit.

    Parameters
    ----------
    brutto_eink_5_tu
        See :func:`brutto_eink_5_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See :ref:`eink_st_abzuege_params`.

    Returns
    -------

    """
    out = (
        brutto_eink_5_tu
        - anz_erwachsene_tu
        * (
            eink_st_abzuege_params["sparerpauschbetrag"]
            + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
        )
    ).clip(lower=0)
    return out
