"""This module provides functions to compute alimony payments (Unterhalt)."""
import numpy as np


def unterhaltsvors_m_tu(unterhaltsvors_m, tu_id):
    """Monthly child support advance payment per tax unit.

   Made by government if the parent who has to pay does not.

    Parameters
    ----------
    unterhaltsvors_m
    tu_id

    Returns
    -------

    """
    return unterhaltsvors_m.groupby(tu_id).sum()


def unterhaltsvors_m_hh(unterhaltsvors_m, hh_id):
    """Monthly child support advance payment per household.

    Parameters
    ----------
    unterhaltsvors_m
    hh_id

    Returns
    -------

    """
    return unterhaltsvors_m.groupby(hh_id).sum()


def unterhaltsvors_m(
    tu_id,
    alleinerziehend,
    alter,
    unterhaltsvorschuss_eink_tu,
    unterhalt_params,
    kindergeld_params,
):
    """Advance on Alimony Payment / Unterhaltsvorschuss (UHV)

    Single Parents get alimony payments for themselves and for their child from the ex
    partner. If the ex partner is not able to pay the child alimony, the government pays
    the child alimony to the mother (or the father, if he has the kids)

    The amount is specified in §1612a BGB and, ultimately, in
    Mindesunterhaltsverordnung.

    """

    # Initialize output Series
    out = tu_id * 0

    # The right-hand-side variable is aggregated by tax units whereas we need personal
    # ids on the left-hand-side. Index with tax unit identifier for expansion and remove
    # index because it is
    unterhaltsvorschuss_eink = tu_id.replace(unterhaltsvorschuss_eink_tu)

    conditions = [
        (alter < 6) & alleinerziehend,
        (alter >= 6) & (alter < 12) & alleinerziehend,
        # Older kids get it only if the parent has income > 600€.
        (alter >= 12)
        & (alter < 18)
        & alleinerziehend
        & (
            unterhaltsvorschuss_eink
            > unterhalt_params["unterhaltsvorschuss_mindesteinkommen"]
        ),
    ]

    choices = [
        (unterhalt_params["mindestunterhalt"][6] - kindergeld_params["kindergeld"][1]),
        (unterhalt_params["mindestunterhalt"][12] - kindergeld_params["kindergeld"][1]),
        (unterhalt_params["mindestunterhalt"][17] - kindergeld_params["kindergeld"][1]),
    ]

    out[:] = np.ceil(np.select(conditions, choices)).astype(int)

    # TODO: Check against actual transfers
    return out


def unterhaltsvorschuss_eink_tu(
    bruttolohn_m_tu,
    sonstig_eink_m_tu,
    eink_selbst_m_tu,
    vermiet_eink_m_tu,
    kapital_eink_m_tu,
    ges_rente_m_tu,
    arbeitsl_geld_m_tu,
):
    out = (
        bruttolohn_m_tu
        + sonstig_eink_m_tu
        + eink_selbst_m_tu
        + vermiet_eink_m_tu
        + kapital_eink_m_tu
        + ges_rente_m_tu
        + arbeitsl_geld_m_tu
    )

    return out


def eink_selbst_m_tu(eink_selbst_m, tu_id):
    return eink_selbst_m.groupby(tu_id).sum()


def vermiet_eink_m_tu(vermiet_eink_m, tu_id):
    return vermiet_eink_m.groupby(tu_id).sum()


def kapital_eink_m_tu(kapital_eink_m, tu_id):
    return kapital_eink_m.groupby(tu_id).sum()


def ges_rente_m_tu(ges_rente_m, tu_id):
    return ges_rente_m.groupby(tu_id).sum()
