"""Kinderzuschlag / Additional Child Benefit.

The purpose of Kinderzuschlag (Kiz) is to keep families out of ALG2. If they would
be eligible to ALG2 due to the fact that their claim rises because of their
children, they can claim Kiz.

A couple of criteria need to be met.

1. the household has to have some income

2. net income minus housing benefit needs has to be lower than total ALG2 need plus
   additional child benefit.

3. Over a certain income threshold (which depends on housing costs, and is
   therefore household-specific), parental income is deducted from child benefit
   claim.

In contrast to ALG2, Kiz considers only the rental costs that are attributed to the
parents. This is done by some fixed share which is updated on annual basis
('jährlicher Existenzminimumsbericht')

# ToDo: Reconsider current assumption: not payed out if a pensioneer lives in the
# ToDo: household.

"""


def kinderzuschl_m_hh(
    _kinderzuschl_nach_vermög_check_m_tu: float,
    kinderzuschl_vorrang_hh: bool,
    wohngeld_kinderzuschl_vorrang_hh: bool,
    anz_rentner_hh: int,
) -> float:
    """Aggregate child benefit on household level.

    Parameters
    ----------
    _kinderzuschl_nach_vermög_check_m_tu
        See :func:`_kinderzuschl_nach_vermög_check_m_tu`.
    kinderzuschl_vorrang_hh
        See :func:`kinderzuschl_vorrang_hh`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.

    Returns
    -------

    """
    if ((not kinderzuschl_vorrang_hh) and (not wohngeld_kinderzuschl_vorrang_hh)) or (
        anz_rentner_hh > 0
    ):
        out = 0.0
    else:
        out = _kinderzuschl_nach_vermög_check_m_tu

    return out


def _kinderzuschl_vor_vermög_check_m_tu_bis_06_2019(
    kinderzuschl_bruttoeink_eltern_m_tu: float,
    kinderzuschl_eink_eltern_m_tu: float,
    kinderzuschl_eink_min_m_tu: float,
    kinderzuschl_eink_max_m_tu: float,
    kinderzuschl_kindereink_abzug_m_tu: float,
    kinderzuschl_eink_anrechn_m_tu: float,
) -> float:
    """Calculate Kinderzuschlag since 2005 until 06/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold and net income needs to be below the maximum income
    threshold.

    Parameters
    ----------
    kinderzuschl_bruttoeink_eltern_m_tu
        See :func:`kinderzuschl_bruttoeink_eltern_m_tu`.
    kinderzuschl_eink_eltern_m_tu
        See :func:`kinderzuschl_eink_eltern_m_tu`.
    kinderzuschl_eink_min_m_tu
        See :func:`kinderzuschl_eink_min_m_tu`.
    kinderzuschl_eink_max_m_tu
        See :func:`kinderzuschl_eink_max_m_tu`.
    kinderzuschl_kindereink_abzug_m_tu
        See :func:`kinderzuschl_kindereink_abzug_m_tu`.
    kinderzuschl_eink_anrechn_m_tu
        See :func:`kinderzuschl_eink_anrechn_m_tu`.

    Returns
    -------

    """

    # Check if parental income is in income range for child benefit.
    if (kinderzuschl_bruttoeink_eltern_m_tu >= kinderzuschl_eink_min_m_tu) and (
        kinderzuschl_eink_eltern_m_tu <= kinderzuschl_eink_max_m_tu
    ):
        out = max(
            kinderzuschl_kindereink_abzug_m_tu - kinderzuschl_eink_anrechn_m_tu, 0.0
        )
    else:
        out = 0.0

    return out


def _kinderzuschl_vor_vermög_check_m_tu_ab_07_2019(
    kinderzuschl_bruttoeink_eltern_m_tu: float,
    kinderzuschl_eink_min_m_tu: float,
    kinderzuschl_kindereink_abzug_m_tu: float,
    kinderzuschl_eink_anrechn_m_tu: float,
) -> float:
    """Calculate Kinderzuschlag since 07/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kinderzuschl_bruttoeink_eltern_m_tu
        See :func:`kinderzuschl_bruttoeink_eltern_m_tu`.
    kinderzuschl_eink_min_m_tu
        See :func:`kinderzuschl_eink_min_m_tu`.
    kinderzuschl_kindereink_abzug_m_tu
        See :func:`kinderzuschl_kindereink_abzug_m_tu`.
    kinderzuschl_eink_anrechn_m_tu
        See :func:`kinderzuschl_eink_anrechn_m_tu`.

    Returns
    -------

    """
    if kinderzuschl_bruttoeink_eltern_m_tu >= kinderzuschl_eink_min_m_tu:
        out = max(
            kinderzuschl_kindereink_abzug_m_tu - kinderzuschl_eink_anrechn_m_tu, 0.0
        )
    else:
        out = 0.0

    return out
