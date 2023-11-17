"""Kinderzuschlag / Additional Child Benefit.

"""
from _gettsim.shared import dates_active


def kinderzuschl_m_hh(
    _kinderzuschl_nach_vermög_check_m_tu: float,
    kinderzuschl_vorrang_bg: bool,
    wohngeld_kinderzuschl_vorrang_vg: bool,
    anz_rentner_hh: int,
) -> float:
    """Aggregate child benefit on household level.

    Parameters
    ----------
    _kinderzuschl_nach_vermög_check_m_tu
        See :func:`_kinderzuschl_nach_vermög_check_m_tu`.
    kinderzuschl_vorrang_bg
        See :func:`kinderzuschl_vorrang_bg`.
    wohngeld_kinderzuschl_vorrang_vg
        See :func:`wohngeld_kinderzuschl_vorrang_vg`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.

    Returns
    -------

    """
    if ((not kinderzuschl_vorrang_bg) and (not wohngeld_kinderzuschl_vorrang_vg)) or (
        anz_rentner_hh > 0
    ):
        out = 0.0
    else:
        out = _kinderzuschl_nach_vermög_check_m_tu

    return out


@dates_active(
    end="2019-06-30",
    change_name="_kinderzuschl_vor_vermög_check_m_tu",
)
def _kinderzuschl_vor_vermög_check_m_tu_check_eink_max(  # noqa: PLR0913
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


@dates_active(start="2019-07-01")
def _kinderzuschl_vor_vermög_check_m_tu(
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
