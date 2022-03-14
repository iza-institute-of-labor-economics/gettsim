from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


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
