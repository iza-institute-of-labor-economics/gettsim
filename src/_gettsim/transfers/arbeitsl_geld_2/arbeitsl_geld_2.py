

def arbeitsl_geld_2_m_bg(
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
    wohngeld_vorrang_bg: bool,
    kinderzuschl_vorrang_bg: bool,
    wohngeld_kinderzuschl_vorrang_bg: bool,
    erwachsene_alle_rentner_hh: bool,
) -> float:
    """Calculate final monthly subsistence payment on household level.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.
    wohngeld_vorrang_bg
        See :func:`wohngeld_vorrang_bg`.
    kinderzuschl_vorrang_bg
        See :func:`kinderzuschl_vorrang_bg`.
    wohngeld_kinderzuschl_vorrang_bg
        See :func:`wohngeld_kinderzuschl_vorrang_bg`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh`.

    Returns
    -------
    float with the income by unemployment insurance on household level.

    """
    # TODO (@MImmesberger): No interaction between Wohngeld/ALG2 and Grundsicherung im
    # Alter (SGB XII) is implemented yet. We assume for now that households with only
    # retirees are eligible for Grundsicherung im Alter but not for ALG2/Wohngeld. All
    # other households are not eligible for SGB XII, but SGB II / Wohngeld. Once this is
    # resolved, remove the `erwachsene_alle_rentner_hh` condition.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/703
    if (
        wohngeld_vorrang_bg
        or kinderzuschl_vorrang_bg
        or wohngeld_kinderzuschl_vorrang_bg
        or erwachsene_alle_rentner_hh
    ):
        out = 0.0
    else:
        out = arbeitsl_geld_2_vor_vorrang_m_bg

    return out


def arbeitsl_geld_2_vor_vorrang_m_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_eink_m_bg: float,
    vermögen_bedürft_bg: float,
    arbeitsl_geld_2_vermög_freib_bg: float,
) -> float:
    """Calculate potential basic subsistence (after income deduction and wealth check).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_eink_m_bg
        See :func:`arbeitsl_geld_2_eink_m_bg`.
    arbeitsl_geld_2_vermög_freib_bg
        See :func:`arbeitsl_geld_2_vermög_freib_bg`.
    vermögen_bedürft_bg
        See basic input variable :ref:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.

    Returns
    -------

    """

    # Check wealth exemption
    if vermögen_bedürft_bg > arbeitsl_geld_2_vermög_freib_bg:
        out = 0.0
    else:
        # Deduct income from various sources
        out = max(
            0.0,
            arbeitsl_geld_2_regelbedarf_m_bg - arbeitsl_geld_2_eink_m_bg,
        )

    return out
