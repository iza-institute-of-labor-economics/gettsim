from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def st_kein_kind_freib_tu(
    zu_verst_eink_kein_kinderfreib_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    eink_st_params: dict,
) -> FloatSeries:
    """Taxes without child allowance.

    Parameters
    ----------
    zu_verst_eink_kein_kinderfreib_tu
        See :func:`zu_verst_eink_kein_kinderfreib_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = zu_verst_eink_kein_kinderfreib_tu / anz_erwachsene_tu

    return anz_erwachsene_tu * st_tarif(zu_verst_eink_per_indiv, params=eink_st_params)


def st_kind_freib_tu(
    zu_verst_eink_kinderfreib_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    eink_st_params: dict,
) -> FloatSeries:
    """Taxes with child allowance.

    Parameters
    ----------
    zu_verst_eink_kinderfreib_tu
        See :func:`zu_verst_eink_kinderfreib_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = zu_verst_eink_kinderfreib_tu / anz_erwachsene_tu
    return anz_erwachsene_tu * st_tarif(zu_verst_eink_per_indiv, params=eink_st_params)


def st_tarif(x: FloatSeries, params: dict) -> FloatSeries:
    """The German Income Tax Tariff.

    Modelled only after 2002 so far.
    It's not calculated as in the tax code, but rather a gemoetric decomposition of the
    area beneath the marginal tax rate function.
    This facilitates the implementation of alternative tax schedules

    Parameters
    ----------
    x : Floatseries
        Some floatseries wherest_tarif is applied to.
    params : dict
        Dictionary created in respy.piecewise_functions.

    Returns
    -------

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
