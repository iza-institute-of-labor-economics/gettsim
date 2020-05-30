import datetime

import numpy as np
import pandas as pd


def unterhaltsvors_m_tu(unterhaltsvors_m, tu_id):
    """

    Parameters
    ----------
    unterhaltsvors_m
    tu_id

    Returns
    -------

    """
    return unterhaltsvors_m.groupby(tu_id).sum()


def unterhaltsvors_m_hh(unterhaltsvors_m, hh_id):
    """

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
    unterhaltsvors_m = pd.Series(index=tu_id.index, data=np.nan)

    # UHV before 07/2017. Not implemented yet, as it was only paid for 6 years. So we
    # return nans.
    if unterhalt_params["datum"] < datetime.date(2017, 7, 1):
        return unterhaltsvors_m

    # Benefit amount depends on the tax allowance for children ("sächliches
    # Existenzminimum") and the child benefit for the first child.
    unterhaltsvors_m = unterhaltsvors_m.fillna(0)

    # The right-hand-side variable is aggregated by tax units whereas we need personal
    # ids on the left-hand-side. Index with tax unit identifier for expansion and remove
    # index because it is
    unterhaltsvorschuss_eink = unterhaltsvorschuss_eink_tu[tu_id].to_numpy()

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

    unterhaltsvors_m[:] = np.ceil(np.select(conditions, choices)).astype(int)

    # TODO: Check against actual transfers
    return unterhaltsvors_m


def unterhaltsvorschuss_eink_tu(
    bruttolohn_m_tu,
    sonstig_eink_m_tu,
    eink_selbstst_m_tu,
    vermiet_eink_m_tu,
    kapital_eink_m_tu,
    ges_rente_m_tu,
    arbeitsl_geld_m_tu,
):
    out = (
        bruttolohn_m_tu
        + sonstig_eink_m_tu
        + eink_selbstst_m_tu
        + vermiet_eink_m_tu
        + kapital_eink_m_tu
        + ges_rente_m_tu
        + arbeitsl_geld_m_tu
    )

    return out


def eink_selbstst_m_tu(eink_selbstst_m, tu_id):
    return eink_selbstst_m.groupby(tu_id).sum()


def vermiet_eink_m_tu(vermiet_eink_m, tu_id):
    return vermiet_eink_m.groupby(tu_id).sum()


def kapital_eink_m_tu(kapital_eink_m, tu_id):
    return kapital_eink_m.groupby(tu_id).sum()


def ges_rente_m_tu(ges_rente_m, tu_id):
    return ges_rente_m.groupby(tu_id).sum()
