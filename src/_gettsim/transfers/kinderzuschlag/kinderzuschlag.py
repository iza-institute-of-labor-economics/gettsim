"""Kinderzuschlag."""

from _gettsim.functions.policy_function import policy_function


@policy_function
def betrag_m_bg(
    anspruchshöhe_m_bg: float,
    vorrangpruefungen__kinderzuschlag_vorrang_bg: bool,
    vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg: bool,
    anz_rentner_hh: int,
) -> float:
    """Aggregate child benefit on household level.

    Parameters
    ----------
    anspruchshöhe_m_bg
        See :func:`anspruchshöhe_m_bg`.
    vorrangpruefungen__kinderzuschlag_vorrang_bg
        See :func:`vorrangpruefungen__kinderzuschlag_vorrang_bg`.
    vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg
        See :func:`vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.

    Returns
    -------

    """
    if (
        (not vorrangpruefungen__kinderzuschlag_vorrang_bg)
        and (not vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg)
    ) or (anz_rentner_hh > 0):
        out = 0.0
    else:
        out = anspruchshöhe_m_bg

    return out


@policy_function
def anspruchshöhe_m(
    anspruchshöhe_m_bg: float,
    anz_personen_bg: int,
) -> float:
    """Kinderzuschlag on individual level.

    Target necessary for aggregation to wthh level.

    Parameters
    ----------
    anspruchshöhe_m_bg
        See :func:`anspruchshöhe_m_bg`.
    anz_personen_bg
        See :func:`anz_personen_bg`.

    Returns
    -------

    """
    return anspruchshöhe_m_bg / anz_personen_bg


@policy_function
def anspruchshöhe_m_bg(
    basisbetrag_m_bg: float,
    vermögen_bedürft_bg: float,
    vermögen_freibetrag_bg: float,
) -> float:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    basisbetrag_m_bg
        See :func:`basisbetrag_m_bg`.
    vermögen_bedürft_bg
        See basic input variable :ref:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.
    vermögen_freibetrag_bg
        See :func:`vermögen_freibetrag_bg`.

    Returns
    -------

    """

    if vermögen_bedürft_bg > vermögen_freibetrag_bg:
        out = max(
            basisbetrag_m_bg - (vermögen_bedürft_bg - vermögen_freibetrag_bg),
            0.0,
        )
    else:
        out = basisbetrag_m_bg
    return out


@policy_function(end_date="2022-12-31", name_in_dag="vermögen_freibetrag_bg")
def vermögen_freibetrag_bg_bis_2022(
    arbeitslosengeld_2__freibetrag_vermögen_bg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag until 2022.

    Parameters
    ----------
    arbeitslosengeld_2__freibetrag_vermögen_bg
        See :func:`arbeitslosengeld_2__freibetrag_vermögen_bg`.

    Returns
    -------

    """

    return arbeitslosengeld_2__freibetrag_vermögen_bg


@policy_function(start_date="2023-01-01", name_in_dag="vermögen_freibetrag_bg")
def vermögen_freibetrag_bg_ab_2023(
    arbeitslosengeld_2__freibetrag_vermögen_in_karenzzeit_bg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag since 2023.

    Parameters
    ----------
    arbeitslosengeld_2__freibetrag_vermögen_in_karenzzeit_bg
        See :func:`arbeitslosengeld_2__freibetrag_vermögen_in_karenzzeit_bg`.

    Returns
    -------

    """

    return arbeitslosengeld_2__freibetrag_vermögen_in_karenzzeit_bg


@policy_function(
    end_date="2019-06-30",
    leaf_name="basisbetrag_m_bg",
)
def basisbetrag_m_bg_check_eink_max(  # noqa: PLR0913
    bruttoeinkommen_eltern_m_bg: float,
    nettoeinkommen_eltern_m_bg: float,
    mindestbruttoeinkommen_m_bg: float,
    maximales_nettoeinkommen_m_bg: float,
    basisbetrag_kind_m_bg: float,
    anzurechnendes_einkommen_eltern_m_bg: float,
    anz_personen_bg: int,
) -> float:
    """Calculate Kinderzuschlag since 2005 until 06/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold and net income needs to be below the maximum income
    threshold.

    Kinderzuschlag is only paid out if parents are part of the BG (anz_personen_bg > 1).

    Parameters
    ----------
    bruttoeinkommen_eltern_m_bg
        See :func:`bruttoeinkommen_eltern_m_bg`.
    nettoeinkommen_eltern_m_bg
        See :func:`nettoeinkommen_eltern_m_bg`.
    mindestbruttoeinkommen_m_bg
        See :func:`mindestbruttoeinkommen_m_bg`.
    maximales_nettoeinkommen_m_bg
        See :func:`maximales_nettoeinkommen_m_bg`.
    basisbetrag_kind_m_bg
        See :func:`basisbetrag_kind_m_bg`.
    anzurechnendes_einkommen_eltern_m_bg
        See :func:`anzurechnendes_einkommen_eltern_m_bg`.
    anz_personen_bg
        See :func:`anz_personen_bg`.

    Returns
    -------

    """

    # Check if parental income is in income range for child benefit.
    if (
        (bruttoeinkommen_eltern_m_bg >= mindestbruttoeinkommen_m_bg)
        and (nettoeinkommen_eltern_m_bg <= maximales_nettoeinkommen_m_bg)
        and anz_personen_bg > 1
    ):
        out = max(basisbetrag_kind_m_bg - anzurechnendes_einkommen_eltern_m_bg, 0.0)
    else:
        out = 0.0

    return out


@policy_function(start_date="2019-07-01")
def basisbetrag_m_bg(
    bruttoeinkommen_eltern_m_bg: float,
    mindestbruttoeinkommen_m_bg: float,
    basisbetrag_kind_m_bg: float,
    anzurechnendes_einkommen_eltern_m_bg: float,
    anz_personen_bg: int,
) -> float:
    """Calculate Kinderzuschlag since 07/2019. Whether Kinderzuschlag or
    Arbeitslosengeld 2 applies will be checked later.

    To be eligible for Kinderzuschlag, gross income of parents needs to exceed the
    minimum income threshold.

    Kinderzuschlag is only paid out if parents are part of the BG (anz_personen_bg > 1).


    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    bruttoeinkommen_eltern_m_bg
        See :func:`bruttoeinkommen_eltern_m_bg`.
    mindestbruttoeinkommen_m_bg
        See :func:`mindestbruttoeinkommen_m_bg`.
    basisbetrag_kind_m_bg
        See :func:`basisbetrag_kind_m_bg`.
    anzurechnendes_einkommen_eltern_m_bg
        See :func:`anzurechnendes_einkommen_eltern_m_bg`.
    anz_personen_bg
        See :func:`anz_personen_bg`.

    Returns
    -------

    """
    if (
        bruttoeinkommen_eltern_m_bg >= mindestbruttoeinkommen_m_bg
    ) and anz_personen_bg > 1:
        out = max(basisbetrag_kind_m_bg - anzurechnendes_einkommen_eltern_m_bg, 0.0)
    else:
        out = 0.0

    return out
