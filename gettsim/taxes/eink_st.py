import numpy as np
import pandas as pd

from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


def _st_kein_kind_freib(_zu_verst_eink_kein_kinderfreib, eink_st_params):
    """

    Parameters
    ----------
    _zu_verst_eink_kein_kinderfreib
    eink_st_params

    Returns
    -------

    """
    if eink_st_params["jahr"] < 2002:
        raise ValueError("Income Tax Pre 2002 not yet modelled!")
    out = st_tarif(_zu_verst_eink_kein_kinderfreib, eink_st_params)
    return pd.Series(
        index=_zu_verst_eink_kein_kinderfreib.index,
        data=out,
        name="_st_kein_kind_freib",
    )


def _st_kein_kind_freib_tu(_st_kein_kind_freib, tu_id):
    out = _st_kein_kind_freib.groupby(tu_id).apply(sum)
    return out.rename("_st_kein_kind_freib_tu")


def _st_kind_freib(_zu_versteuerndes_eink_kind_freib, eink_st_params):
    """

    Parameters
    ----------
    _zu_versteuerndes_eink_kind_freib
    eink_st_params

    Returns
    -------

    """
    if eink_st_params["jahr"] < 2002:
        raise ValueError("Income Tax Pre 2002 not yet modelled!")
    out = st_tarif(_zu_versteuerndes_eink_kind_freib, eink_st_params)
    return pd.Series(
        index=_zu_versteuerndes_eink_kind_freib.index, data=out, name="_st_kind_freib"
    )


def _st_kind_freib_tu(_st_kind_freib, tu_id):
    out = _st_kind_freib.groupby(tu_id).apply(sum)
    return out.rename("_st_kind_freib_tu")


@np.vectorize
def st_tarif(x, params):
    """ The German Income Tax Tariff
    modelled only after 2002 so far

    It's not calculated as in the tax code, but rather a gemoetric decomposition of the
    area beneath the marginal tax rate function.
    This facilitates the implementation of alternative tax schedules

    args:
        x (float): taxable income
        params (dict): tax-benefit parameters specific to year and reform
    """
    eink_st = piecewise_polynomial(
        x,
        lower_thresholds=params["eink_st_tarif"]["lower_thresholds"],
        upper_thresholds=params["eink_st_tarif"]["upper_thresholds"],
        rates=params["eink_st_tarif"]["rates"],
        intercepts_at_lower_thresholds=params["eink_st_tarif"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return eink_st
