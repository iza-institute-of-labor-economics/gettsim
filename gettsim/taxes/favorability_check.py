"""This module contains the 'Higher-Yield Test':

It compares the tax burden that results from various definitions of the tax base. Most
importantly, it compares the tax burden without applying the child allowance
(kein_kinderfreib) AND receiving child benefit with the tax burden including the child
allowance (kinderfreib), but without child benefit. The most beneficial (for the
household) is chosen. If child allowance is claimed, kindergeld is set to zero. A
similar check applies to whether it is more profitable to tax capital incomes with the
standard 25% rate or to include it in the tariff.

"""
from gettsim.shared import add_rounding_spec
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderfreib_günstiger_tu(
    eink_st_kein_kinderfreib_tu: FloatSeries,
    kindergeld_basis_m_tu: FloatSeries,
    kinderbonus_basis_m_tu: FloatSeries,
    eink_st_kinderfreib_tu: FloatSeries,
) -> BoolSeries:
    """Return whether Kinderfreibetrag is more favorable than Kindergeld.

    Parameters
    ----------
    eink_st_kein_kinderfreib_tu
        See :func:`eink_st_kein_kinderfreib_tu`.
    kindergeld_basis_m_tu
        See :func:`kindergeld_basis_m_tu`.
    kinderbonus_basis_m_tu
        See :func:`kinderbonus_basis_m_tu`.
    eink_st_kinderfreib_tu
        See :func:`eink_st_kinderfreib_tu`.

    Returns
    -------

    """
    eink_st_kein_kinderfreib = eink_st_kein_kinderfreib_tu - 12 * (
        kindergeld_basis_m_tu + kinderbonus_basis_m_tu
    )
    return eink_st_kein_kinderfreib > eink_st_kinderfreib_tu


@add_rounding_spec(params_key="eink_st")
def eink_st_tu_bis_1996(eink_st_kinderfreib_tu: FloatSeries) -> FloatSeries:
    """Income tax calculation until 1996.

    Until 1996 individuals could claim child allowance and recieve child benefit.
    Therefore the tax burden is allways smaller.
    Parameters
    ----------
    eink_st_kinderfreib_tu
        See :func:`eink_st_kinderfreib_tu`.

    Returns
    -------

    """
    return eink_st_kinderfreib_tu


@add_rounding_spec(params_key="eink_st")
def eink_st_tu_ab_1997(
    eink_st_kein_kinderfreib_tu: FloatSeries,
    eink_st_kinderfreib_tu: FloatSeries,
    kinderfreib_günstiger_tu: BoolSeries,
) -> FloatSeries:
    """Income tax calculation since 1997.

    Parameters
    ----------
    eink_st_kein_kinderfreib_tu
        See :func:`eink_st_kein_kinderfreib_tu`.
    eink_st_kinderfreib_tu
        See :func:`eink_st_kinderfreib_tu`.
    kinderfreib_günstiger_tu
        See :func:`kinderfreib_günstiger_tu`.

    Returns
    -------

    """
    out = eink_st_kein_kinderfreib_tu
    out.loc[kinderfreib_günstiger_tu] = eink_st_kinderfreib_tu.loc[
        kinderfreib_günstiger_tu
    ]
    return out


def kindergeld_m_bis_1996(kindergeld_basis_m: FloatSeries) -> FloatSeries:
    """Kindergeld calculation until 1996.

    Until 1996 individuals could claim child allowance and recieve child benefit.

    Parameters
    ----------
    kindergeld_basis_m
        See :func:`kindergeld_basis_m`.

    Returns
    -------

    """
    return kindergeld_basis_m


def kindergeld_m_ab_1997(
    kinderfreib_günstiger_tu: BoolSeries,
    kindergeld_basis_m: FloatSeries,
    tu_id: IntSeries,
) -> FloatSeries:
    """Kindergeld calculation since 1997.

    Parameters
    ----------
    kinderfreib_günstiger_tu
        See :func:`kinderfreib_günstiger_tu`.
    kindergeld_basis_m
        See :func:`kindergeld_basis_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    beantrage_kinderfreib = tu_id.replace(kinderfreib_günstiger_tu)
    out = kindergeld_basis_m
    out.loc[beantrage_kinderfreib] = 0
    return out


def kinderbonus_m(
    kinderfreib_günstiger_tu: BoolSeries,
    kinderbonus_basis_m: FloatSeries,
    tu_id: IntSeries,
) -> FloatSeries:
    """Calculate Kinderbonus (one-time payment, non-allowable against transfer payments).

    Parameters
    ----------
    kinderfreib_günstiger_tu
        See :func:`kinderfreib_günstiger_tu`.
    kinderbonus_basis_m
        See :func:`kinderbonus_basis_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    beantrage_kinderfreib = tu_id.replace(kinderfreib_günstiger_tu)
    out = kinderbonus_basis_m
    out.loc[beantrage_kinderfreib] = 0
    return out


def kindergeld_m_hh(kindergeld_m: FloatSeries, hh_id: IntSeries) -> FloatSeries:
    """Aggregate Child benefit on the household level.

    Aggregate Child benefit on the household level, as we could have several tax_units
    in one household.

    Parameters
    ----------
    kindergeld_m
        See :func:`kindergeld_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return kindergeld_m.groupby(hh_id).sum()


def kindergeld_m_tu(kindergeld_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate Child benefit on the tax unit level.

    Parameters
    ----------
    kindergeld_m
        See :func:`kindergeld_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kindergeld_m.groupby(tu_id).sum()


def kinderbonus_m_hh(kinderbonus_m: FloatSeries, hh_id: IntSeries) -> FloatSeries:
    """Aggregate Kinderbonus on the household level.

    Aggregate Kinderbonus on the household level, as we could have several tax_units
    in one household.

    Parameters
    ----------
    kinderbonus_m
        See :func:`kinderbonus_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return kinderbonus_m.groupby(hh_id).sum()


def kinderbonus_m_tu(kinderbonus_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate Kinderbonus on the tax unit level.

    Parameters
    ----------
    kinderbonus_m
        See :func:`kinderbonus_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kinderbonus_m.groupby(tu_id).sum()
