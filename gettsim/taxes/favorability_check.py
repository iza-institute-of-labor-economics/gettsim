"""This module contains the 'Higher-Yield Test':

It compares the tax burden that results from various definitions of the tax base. Most
importantly, it compares the tax burden without applying the child allowance
(kein_kind_freib) AND receiving child benefit with the tax burden including the child
allowance (kind_freib), but without child benefit. The most beneficial (for the
household) is chosen. If child allowance is claimed, kindergeld is set to zero. A
similar check applies to whether it is more profitable to tax capital incomes with the
standard 25% rate or to include it in the tariff.

"""


def _beantrage_kind_freib_tu(
    _st_kein_kind_freib_tu, _kindergeld_m_tu_basis, _st_kind_freib_tu
):
    """Check if individual claims child allowance.

    Parameters
    ----------
    _st_kein_kind_freib_tu
    _kindergeld_m_tu_basis
    _st_kind_freib_tu

    Returns
    -------

    """
    st_kein_kind_freib = _st_kein_kind_freib_tu - 12 * _kindergeld_m_tu_basis
    return st_kein_kind_freib > _st_kind_freib_tu


def eink_st_tu_bis_1996(_st_kind_freib_tu):
    """Income tax calculation until 1996.

    Until 1996 individuals could claim child allowance and recieve child benefit.
    Therefore the tax burden is allways smaller.
    Parameters
    ----------
    _st_kind_freib_tu

    Returns
    -------

    """
    return _st_kind_freib_tu


def eink_st_tu_ab_1997(
    _st_kein_kind_freib_tu, _st_kind_freib_tu, _beantrage_kind_freib_tu,
):
    """Income tax calculation since 1997.

    Parameters
    ----------
    _st_kein_kind_freib_tu
    _st_kind_freib_tu
    _beantrage_kind_freib_tu

    Returns
    -------

    """
    out = _st_kein_kind_freib_tu
    out.loc[_beantrage_kind_freib_tu] = _st_kind_freib_tu.loc[_beantrage_kind_freib_tu]
    return out


def kindergeld_m_bis_1996(_kindergeld_m_basis):
    """Kindergeld calculation until 1996.

    Until 1996 individuals could claim child allowance and recieve child benefit.

    Parameters
    ----------
    _kindergeld_m_basis

    Returns
    -------

    """
    return _kindergeld_m_basis


def kindergeld_m_ab_1997(
    _beantrage_kind_freib_tu, _kindergeld_m_basis, tu_id,
):
    """Kindergeld calculation since 1997.

    Parameters
    ----------
    _beantrage_kind_freib_tu
    _kindergeld_m_basis
    tu_id

    Returns
    -------

    """
    _beantrage_kind_freib = tu_id.replace(_beantrage_kind_freib_tu)
    out = _kindergeld_m_basis
    out.loc[_beantrage_kind_freib] = 0
    return out


def kindergeld_m_hh(kindergeld_m, hh_id):
    """Aggregate Child benefit on the household level.

    Aggregate Child benefit on the household level, as we could have several tax_units
    in one household.

    Parameters
    ----------
    kindergeld_m
    hh_id

    Returns
    -------

    """
    return kindergeld_m.groupby(hh_id).sum()


def kindergeld_m_tu(kindergeld_m, tu_id):
    """Aggregate Child benefit on the tax unit level.

    Parameters
    ----------
    kindergeld_m
    tu_id

    Returns
    -------

    """
    return kindergeld_m.groupby(tu_id).sum()
