"""
Kinderzuschlag / Additional Child Benefit

    The purpose of Kinderzuschlag (Kiz) is to keep families out of ALG2. If they would
    be eligible to ALG2 due to the fact that their claim rises because of their
    children, they can claim Kiz.

    A couple of criteria need to be met.

    1. the household has to have some income

    2. net income minus housing benefit needs has to be lower than total ALG2 need plus
       additional child benefit.

    3. Over a certain income threshold (which depends on housing costs, and is therefore
       household-specific), parental income is deducted from child benefit claim.

    In contrast to ALG2, Kiz considers only the rental costs that are attributed to the
    parents. This is done by some fixed share which is updated on annual basis
    ('jährlicher Existenzminimumsbericht')
"""


def kinderzuschlag_m(
    _kinderzuschlag_m_vermögens_check,
    kinderzuschlag_vorrang,
    wohngeld_m_kinderzuschlag_vorrang,
    arbeitsl_geld_2_m_basis,
    anz_rentner_per_hh,
):
    cond = (
        ~kinderzuschlag_vorrang
        & ~wohngeld_m_kinderzuschlag_vorrang
        & (arbeitsl_geld_2_m_basis > 0)
    )
    return _kinderzuschlag_m_vermögens_check.where(~cond & (anz_rentner_per_hh == 0), 0)


def kinderzuschlag_ab_juli_2019(
    hh_id,
    _arbeitsl_geld_2_brutto_eink_hh,
    kinderzuschlag_eink_min,
    kinderzuschlag_kindereink_abzug,
    kinderzuschlag_eink_anrechn,
):
    """Creates "_kinderzuschlag_m_vorläufig" since 07/2019.

    Parameters
    ----------
    hh_id
    _arbeitsl_geld_2_brutto_eink_hh
    kinderzuschlag_eink_min
    kinderzuschlag_kindereink_abzug
    kinderzuschlag_eink_anrechn

    Returns
    -------

    """
    out = hh_id * 0
    condition = (
        hh_id.replace(_arbeitsl_geld_2_brutto_eink_hh) >= kinderzuschlag_eink_min
    )
    out.loc[condition] = (
        kinderzuschlag_kindereink_abzug.groupby(hh_id).transform("sum")
        - kinderzuschlag_eink_anrechn
    ).clip(lower=0)

    return out.groupby(hh_id).transform("max")


def kinderzuschlag_ab_2005_bis_juni_2019(
    hh_id,
    kinderzuschlag_eink_spanne,
    kinderzuschlag_kindereink_abzug,
    kinderzuschlag_eink_anrechn,
):
    """Creates "_kinderzuschlag_m_vorläufig" until 06/2019.

    Parameters
    ----------
    hh_id
    kinderzuschlag_eink_spanne
    kinderzuschlag_kindereink_abzug
    kinderzuschlag_eink_anrechn

    Returns
    -------

    """
    out = kinderzuschlag_eink_spanne * 0
    out.loc[kinderzuschlag_eink_spanne] = (
        kinderzuschlag_kindereink_abzug.groupby(hh_id).transform("sum")
        - kinderzuschlag_eink_anrechn
    ).clip(lower=0)

    return out.groupby(hh_id).transform("max")
