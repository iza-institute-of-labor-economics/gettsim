import numpy as np
import pandas as pd


def abgelt_st_m(gem_veranlagt, kind, abgelt_st_m_tu, tu_id):
    """ Capital Income Tax / Abgeltungsteuer
        since 2009, captial income is taxed with a flatrate of 25%.
    """
    out = np.select(
        [gem_veranlagt & ~kind, ~gem_veranlagt & ~kind, kind],
        [tu_id.replace(abgelt_st_m_tu) / 2, tu_id.replace(abgelt_st_m_tu), 0],
    )
    return pd.Series(data=out, index=tu_id.index, name="abgelt_st_m")


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
    out = (
        brutto_eink_5_tu
        - np.select([gemeinsam_veranlagte_tu, ~gemeinsam_veranlagte_tu], [2, 1])
        * (
            eink_st_abzuege_params["sparerpauschbetrag"]
            + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
        )
    ).clip(lower=0)
    return out
