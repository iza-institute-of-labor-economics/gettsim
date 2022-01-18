"""This module contains the 'Higher-Yield Test':

It compares the tax burden that results from various definitions of the tax base. Most
importantly, it compares the tax burden without applying the child allowance
(kein_kinder_fb) AND receiving child benefit with the tax burden including the child
allowance (kinder_fb), but without child benefit. The most beneficial (for the
household) is chosen. If child allowance is claimed, kindergeld is set to zero. A
similar check applies to whether it is more profitable to tax capital incomes with the
standard 25% rate or to include it in the tariff.

"""
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def beantrage_kinder_fb_tu(
    st_kein_kinder_fb_tu: FloatSeries,
    kindergeld_m_basis_tu: FloatSeries,
    kinderbonus_m_basis_tu: FloatSeries,
    st_kinder_fb_tu: FloatSeries,
) -> BoolSeries:
    """Check if individual claims child allowance (kinderfreibetrag).

    Parameters
    ----------
    st_kein_kinder_fb_tu
        See :func:`st_kein_kinder_fb_tu`.
    kindergeld_m_basis_tu
        See :func:`kindergeld_m_basis_tu`.
    kinderbonus_m_basis_tu
        See :func:`kinderbonus_m_basis_tu`.
    st_kinder_fb_tu
        See :func:`st_kinder_fb_tu`.

    Returns
    -------

    """
    st_kein_kinder_fb = st_kein_kinder_fb_tu - 12 * (
        kindergeld_m_basis_tu + kinderbonus_m_basis_tu
    )
    return st_kein_kinder_fb > st_kinder_fb_tu


def eink_st_tu_bis_1996(st_kinder_fb_tu: FloatSeries) -> FloatSeries:
    """Income tax calculation until 1996.

    Until 1996 individuals could claim child allowance and recieve child benefit.
    Therefore the tax burden is allways smaller.
    Parameters
    ----------
    st_kinder_fb_tu
        See :func:`st_kinder_fb_tu`.

    Returns
    -------

    """
    return st_kinder_fb_tu


def eink_st_tu_ab_1997(
    st_kein_kinder_fb_tu: FloatSeries,
    st_kinder_fb_tu: FloatSeries,
    beantrage_kinder_fb_tu: BoolSeries,
) -> FloatSeries:
    """Income tax calculation since 1997.

    Parameters
    ----------
    st_kein_kinder_fb_tu
        See :func:`st_kein_kinder_fb_tu`.
    st_kinder_fb_tu
        See :func:`st_kinder_fb_tu`.
    beantrage_kinder_fb_tu
        See :func:`beantrage_kinder_fb_tu`.

    Returns
    -------

    """
    out = st_kein_kinder_fb_tu
    out.loc[beantrage_kinder_fb_tu] = st_kinder_fb_tu.loc[beantrage_kinder_fb_tu]
    return out


def kindergeld_m_bis_1996(kindergeld_m_basis: FloatSeries) -> FloatSeries:
    """Kindergeld calculation until 1996.

    Until 1996 individuals could claim child allowance and recieve child benefit.

    Parameters
    ----------
    kindergeld_m_basis
        See :func:`kindergeld_m_basis`.

    Returns
    -------

    """
    return kindergeld_m_basis


def kindergeld_m_ab_1997(
    beantrage_kinder_fb_tu: BoolSeries,
    kindergeld_m_basis: FloatSeries,
    tu_id: IntSeries,
) -> FloatSeries:
    """Kindergeld calculation since 1997.

    Parameters
    ----------
    beantrage_kinder_fb_tu
        See :func:`beantrage_kinder_fb_tu`.
    kindergeld_m_basis
        See :func:`kindergeld_m_basis`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    beantrage_kinder_fb = tu_id.replace(beantrage_kinder_fb_tu)
    out = kindergeld_m_basis
    out.loc[beantrage_kinder_fb] = 0
    return out


def kinderbonus_m(
    beantrage_kinder_fb_tu: BoolSeries,
    kinderbonus_m_basis: FloatSeries,
    tu_id: IntSeries,
) -> FloatSeries:
    """Calculate Kinderbonus (one-time payment, non-allowable against transfer payments).

    Parameters
    ----------
    beantrage_kinder_fb_tu
        See :func:`beantrage_kinder_fb_tu`.
    kinderbonus_m_basis
        See :func:`kinderbonus_m_basis`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    beantrage_kinder_fb = tu_id.replace(beantrage_kinder_fb_tu)
    out = kinderbonus_m_basis
    out.loc[beantrage_kinder_fb] = 0
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
