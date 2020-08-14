from gettsim.piecewise_functions import piecewise_polynomial


def _st_kein_kind_freib_tu(
    _zu_verst_eink_kein_kinderfreib_tu, anz_erwachsene_tu, eink_st_params
):
    """ Taxes without child allowance.

    Parameters
    ----------
    _zu_verst_eink_kein_kinderfreib_tu
    anz_erwachsene_tu
    eink_st_params

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_kein_kinderfreib_tu / anz_erwachsene_tu

    return anz_erwachsene_tu * _st_tarif(zu_verst_eink_per_indiv, params=eink_st_params)


def _st_kind_freib_tu(_zu_verst_eink_kinderfreib_tu, anz_erwachsene_tu, eink_st_params):
    """Taxes with child allowance.

    Parameters
    ----------
    _zu_verst_eink_kinderfreib_tu
    anz_erwachsene_tu
    eink_st_params

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_kinderfreib_tu / anz_erwachsene_tu

    return anz_erwachsene_tu * _st_tarif(zu_verst_eink_per_indiv, params=eink_st_params)


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
        thresholds=params["eink_st_tarif"]["thresholds"],
        rates=params["eink_st_tarif"]["rates"],
        intercepts_at_lower_thresholds=params["eink_st_tarif"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return eink_st
