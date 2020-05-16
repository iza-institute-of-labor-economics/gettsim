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


def abgelt_st_m_tu(zu_verst_kapital_eink_tu, abgelt_st_params):
    out = abgelt_st_params["abgelt_st_satz"] * zu_verst_kapital_eink_tu
    return out.rename("abgelt_st_m_tu")


def zu_verst_kapital_eink_tu(
    brutto_eink_5_tu, gem_veranlagt_tu, eink_st_abzuege_params
):
    out = (
        brutto_eink_5_tu
        - np.select([gem_veranlagt_tu, ~gem_veranlagt_tu], [2, 1])
        * (
            eink_st_abzuege_params["sparerpauschbetrag"]
            + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
        )
    ).clip(lower=0)
    return out.rename("zu_verst_kapital_eink_tu")


def gem_veranlagt_tu(tu_id, gem_veranlagt):
    return gem_veranlagt.groupby(tu_id).apply(any)
