from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


def _st_kein_kind_freib(_zu_verst_eink_kein_kinderfreib, eink_st_params):
    """ Taxes without child allowance.

    Parameters
    ----------
    _zu_verst_eink_kein_kinderfreib
    eink_st_params

    Returns
    -------

    """
    return _st_tarif(_zu_verst_eink_kein_kinderfreib, params=eink_st_params)


def _st_kein_kind_freib_tu(_st_kein_kind_freib, tu_id):
    return _st_kein_kind_freib.groupby(tu_id).sum()


def _st_kind_freib(_zu_verst_eink_kinderfreib, eink_st_params):
    """Taxes with child allowance.

    Parameters
    ----------
    _zu_verst_eink_kinderfreib
    eink_st_params

    Returns
    -------

    """
    return _st_tarif(_zu_verst_eink_kinderfreib, params=eink_st_params)


def _st_kind_freib_tu(_st_kind_freib, tu_id):
    return _st_kind_freib.groupby(tu_id).sum()


def _st_tarif(x, params):
    """ The German Income Tax Tariff.
     Modelled only after 2002 so far.

    It's not calculated as in the tax code, but rather a gemoetric decomposition of the
    area beneath the marginal tax rate function.
    This facilitates the implementation of alternative tax schedules

    args:
        x (Series): taxable income
        params (dict): tax-benefit parameters specific to year and reform
    """
    eink_st = piecewise_polynomial(
        x=x,
        lower_thresholds=params["eink_st_tarif"]["lower_thresholds"],
        upper_thresholds=params["eink_st_tarif"]["upper_thresholds"],
        rates=params["eink_st_tarif"]["rates"],
        intercepts_at_lower_thresholds=params["eink_st_tarif"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return eink_st
