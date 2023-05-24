from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import add_rounding_spec, dates_active


def eink_st_ohne_kinderfreib_y_tu(
    _zu_verst_eink_ohne_kinderfreib_y_tu: float,
    anz_erwachsene_tu: int,
    eink_st_params: dict,
) -> float:
    """Taxes without child allowance on tax unit level. Also referred to as "tarifliche
    ESt II".

    Parameters
    ----------
    _zu_verst_eink_ohne_kinderfreib_y_tu
        See :func:`_zu_verst_eink_ohne_kinderfreib_y_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_ohne_kinderfreib_y_tu / anz_erwachsene_tu
    out = anz_erwachsene_tu * _eink_st_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )

    return out


def eink_st_mit_kinderfreib_y_tu(
    _zu_verst_eink_mit_kinderfreib_y_tu: float,
    anz_erwachsene_tu: int,
    eink_st_params: dict,
) -> float:
    """Taxes with child allowance on tax unit level. Also referred to as "tarifliche ESt
    I".

    Parameters
    ----------
    _zu_verst_eink_mit_kinderfreib_y_tu
        See :func:`_zu_verst_eink_mit_kinderfreib_y_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_mit_kinderfreib_y_tu / anz_erwachsene_tu
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


@dates_active(end="1996-12-31", change_name="eink_st_y_tu")
@add_rounding_spec(params_key="eink_st")
def eink_st_y_tu_kindergeld_kinderfreib_parallel(
    eink_st_mit_kinderfreib_y_tu: float,
) -> float:
    """Income tax calculation on tax unit level allowing for claiming Kinderfreibetrag
    and receiving Kindergeld at the same time.

    Parameters
    ----------
    eink_st_mit_kinderfreib_y_tu
        See :func:`eink_st_mit_kinderfreib_y_tu`.

    Returns
    -------

    """
    return eink_st_mit_kinderfreib_y_tu


@dates_active(start="1997-01-01", change_name="eink_st_y_tu")
@add_rounding_spec(params_key="eink_st")
def eink_st_y_tu_kindergeld_oder_kinderfreib(
    eink_st_ohne_kinderfreib_y_tu: float,
    eink_st_mit_kinderfreib_y_tu: float,
    kinderfreib_günstiger_tu: bool,
    eink_st_rel_kindergeld_y_tu: float,
) -> float:
    """Income tax calculation on tax unit level since 1997.

    Parameters
    ----------
    eink_st_ohne_kinderfreib_y_tu
        See :func:`eink_st_ohne_kinderfreib_y_tu`.
    eink_st_mit_kinderfreib_y_tu
        See :func:`eink_st_mit_kinderfreib_y_tu`.
    kinderfreib_günstiger_tu
        See :func:`kinderfreib_günstiger_tu`.
    eink_st_rel_kindergeld_y_tu
        See :func:`eink_st_rel_kindergeld_y_tu`.

    Returns
    -------

    """
    if kinderfreib_günstiger_tu:
        out = eink_st_mit_kinderfreib_y_tu + eink_st_rel_kindergeld_y_tu
    else:
        out = eink_st_ohne_kinderfreib_y_tu

    return out


def kinderfreib_günstiger_tu(
    eink_st_ohne_kinderfreib_y_tu: float,
    eink_st_mit_kinderfreib_y_tu: float,
    eink_st_rel_kindergeld_y_tu: float,
) -> bool:
    """Return whether Kinderfreibetrag is more favorable than Kindergeld.

    Parameters
    ----------
    eink_st_ohne_kinderfreib_y_tu
        See :func:`eink_st_ohne_kinderfreib_y_tu`.
    eink_st_mit_kinderfreib_y_tu
        See :func:`eink_st_mit_kinderfreib_y_tu`.
    eink_st_rel_kindergeld_y_tu
        See :func:`eink_st_rel_kindergeld_y_tu`.
    Returns
    -------

    """
    unterschiedsbeitrag = eink_st_ohne_kinderfreib_y_tu - eink_st_mit_kinderfreib_y_tu

    out = unterschiedsbeitrag > eink_st_rel_kindergeld_y_tu
    return out


def eink_st_rel_kindergeld_y_tu(
    kindergeld_m_tu: float,
    kinderbonus_m_tu: float,
    anz_erwachsene_tu: int,
) -> float:
    """Return Kindergeld relevant for income tax of the tax unit. For parents which do
    not file taxes together, only half of Kindergeld is considered.

    Source: § 31 Satz 4 EStG: "Bei nicht zusammenveranlagten Eltern wird der
    Kindergeldanspruch im Umfang des Kinderfreibetrags angesetzt."

    # ToDo: This factor need to be refactored once children are put in separate tax
    # ToDo: units and are linked to their parents (one or two)


    Parameters
    ----------
    kindergeld_m_tu
        See :func:`kindergeld_m_tu`.
    kinderbonus_m_tu
        See :func:`kinderbonus_m_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    Returns
    -------

    """
    out = 12 * (kindergeld_m_tu + kinderbonus_m_tu) * (anz_erwachsene_tu / 2)
    return out
