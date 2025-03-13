"""Monthly SGB II subsitence payment (Arbeitslosengeld II).

Note: Since 2023, Arbeitslosengeld II is referred to as Bürgergeld.
"""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_m_bg(
    anspruchshöhe_m_bg: float,
    vorrangpruefungen__wohngeld_vorrang_bg: bool,
    vorrangpruefungen__kinderzuschlag_vorrang_bg: bool,
    vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg: bool,
    demographics__erwachsene_alle_rentner_hh: bool,
) -> float:
    """Calculate final monthly subsistence payment on household level.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    anspruchshöhe_m_bg
        See :func:`anspruchshöhe_m_bg`.
    vorrangpruefungen__wohngeld_vorrang_bg
        See :func:`vorrangpruefungen__wohngeld_vorrang_bg`.
    vorrangpruefungen__kinderzuschlag_vorrang_bg
        See :func:`vorrangpruefungen__kinderzuschlag_vorrang_bg`.
    vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg
        See :func:`vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg`.
    demographics__erwachsene_alle_rentner_hh
        See :func:`demographics__erwachsene_alle_rentner_hh`.

    Returns
    -------
    float with the income by unemployment insurance on household level.

    """
    # TODO (@MImmesberger): No interaction between Wohngeld/ALG2 and Grundsicherung im
    # Alter (SGB XII) is implemented yet. We assume for now that households with only
    # retirees are eligible for Grundsicherung im Alter but not for ALG2/Wohngeld. All
    # other households are not eligible for SGB XII, but SGB II / Wohngeld. Once this is
    # resolved, remove the `demographics__erwachsene_alle_rentner_hh` condition.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/703
    if (
        vorrangpruefungen__wohngeld_vorrang_bg
        or vorrangpruefungen__kinderzuschlag_vorrang_bg
        or vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg
        or demographics__erwachsene_alle_rentner_hh
    ):
        out = 0.0
    else:
        out = anspruchshöhe_m_bg

    return out


@policy_function()
def anspruchshöhe_m_bg(
    regelbedarf_m_bg: float,
    anzurechnendes_einkommen_m_bg: float,
    demographics__vermögen_bg: float,
    freibetrag_vermögen_bg: float,
) -> float:
    """Calculate potential basic subsistence (after income deduction and wealth check).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    regelbedarf_m_bg
        See :func:`regelbedarf_m_bg`.
    anzurechnendes_einkommen_m_bg
        See :func:`anzurechnendes_einkommen_m_bg`.
    freibetrag_vermögen_bg
        See :func:`freibetrag_vermögen_bg`.
    demographics__vermögen_bg
        See basic input variable :ref:`demographics__vermögen_bg <demographics__vermögen_bg>`.

    Returns
    -------

    """
    # Check wealth exemption
    if demographics__vermögen_bg > freibetrag_vermögen_bg:
        out = 0.0
    else:
        # Deduct income from various sources
        out = max(
            0.0,
            regelbedarf_m_bg - anzurechnendes_einkommen_m_bg,
        )

    return out
