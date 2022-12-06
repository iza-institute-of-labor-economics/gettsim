from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.shared import add_rounding_spec


def eink_st_ohne_kinderfreib_tu(
    _zu_verst_eink_ohne_kinderfreib_tu: float,
    anz_erwachsene_tu: int,
    eink_st_params: dict,
) -> float:
    """Taxes without child allowance on tax unit level.

    Parameters
    ----------
    _zu_verst_eink_ohne_kinderfreib_tu
        See :func:`_zu_verst_eink_ohne_kinderfreib_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_ohne_kinderfreib_tu / anz_erwachsene_tu
    out = anz_erwachsene_tu * _eink_st_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


def eink_st_mit_kinderfreib_tu(
    zu_verst_eink_mit_kinderfreib_tu: float,
    anz_erwachsene_tu: int,
    eink_st_params: dict,
) -> float:
    """Taxes with child allowance on tax unit level.

    Parameters
    ----------
    zu_verst_eink_mit_kinderfreib_tu
        See :func:`zu_verst_eink_mit_kinderfreib_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = zu_verst_eink_mit_kinderfreib_tu / anz_erwachsene_tu
    out = anz_erwachsene_tu * _eink_st_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


def _eink_st_tarif(x: float, params: dict) -> float:
    """The German income tax tariff.

    Parameters
    ----------
    x : float
        The series of floats which the income tax schedule is applied to.
    params : dict
        Dictionary created in respy.piecewise_functions.

    Returns
    -------

    """
    out = piecewise_polynomial(
        x=x,
        thresholds=params["eink_st_tarif"]["thresholds"],
        rates=params["eink_st_tarif"]["rates"],
        intercepts_at_lower_thresholds=params["eink_st_tarif"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out


@add_rounding_spec(params_key="eink_st")
def eink_st_tu_bis_1996(eink_st_mit_kinderfreib_tu: float) -> float:
    """Income tax calculation on tax unit level until 1996.

    Until 1996 individuals could claim Kinderfreibetrag and receive Kindergeld
    at the same time.

    Therefore the tax burden is allways smaller.

    Parameters
    ----------
    eink_st_mit_kinderfreib_tu
        See :func:`eink_st_mit_kinderfreib_tu`.

    Returns
    -------

    """
    return eink_st_mit_kinderfreib_tu


@add_rounding_spec(params_key="eink_st")
def eink_st_tu_ab_1997(
    eink_st_ohne_kinderfreib_tu: float,
    eink_st_mit_kinderfreib_tu: float,
    kinderfreib_günstiger_tu: bool,
) -> float:
    """Income tax calculation on tax unit level since 1997.

    Parameters
    ----------
    eink_st_ohne_kinderfreib_tu
        See :func:`eink_st_ohne_kinderfreib_tu`.
    eink_st_mit_kinderfreib_tu
        See :func:`eink_st_mit_kinderfreib_tu`.
    kinderfreib_günstiger_tu
        See :func:`kinderfreib_günstiger_tu`.

    Returns
    -------

    """
    if kinderfreib_günstiger_tu:
        out = eink_st_mit_kinderfreib_tu
    else:
        out = eink_st_ohne_kinderfreib_tu

    return out


def kinderfreib_günstiger_tu(
    eink_st_ohne_kinderfreib_tu: float,
    kindergeld_basis_m_tu: float,
    kinderbonus_basis_m_tu: float,
    eink_st_mit_kinderfreib_tu: float,
) -> bool:
    """Return whether Kinderfreibetrag is more favorable than Kindergeld.

    Parameters
    ----------
    eink_st_ohne_kinderfreib_tu
        See :func:`eink_st_ohne_kinderfreib_tu`.
    kindergeld_basis_m_tu
        See :func:`kindergeld_basis_m_tu`.
    kinderbonus_basis_m_tu
        See :func:`kinderbonus_basis_m_tu`.
    eink_st_mit_kinderfreib_tu
        See :func:`eink_st_mit_kinderfreib_tu`.

    Returns
    -------

    """
    eink_st_kein_kinderfreib = eink_st_ohne_kinderfreib_tu - 12 * (
        kindergeld_basis_m_tu + kinderbonus_basis_m_tu
    )
    out = eink_st_kein_kinderfreib > eink_st_mit_kinderfreib_tu
    return out
