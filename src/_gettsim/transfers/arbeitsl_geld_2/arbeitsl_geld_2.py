def arbeitsl_geld_2_m_bg(
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
    wohngeld_und_kiz_günstiger_als_sgb_ii: bool,
    erwachsene_alle_rentner_hh: bool,
) -> float:
    """Calculate final monthly subsistence payment on household level.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.
    wohngeld_und_kiz_günstiger_als_sgb_ii
        See basic input variable :ref:`wohngeld_und_kiz_günstiger_als_sgb_ii
        <wohngeld_und_kiz_günstiger_als_sgb_ii>`.
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
    if wohngeld_und_kiz_günstiger_als_sgb_ii or erwachsene_alle_rentner_hh:
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


def arbeitsl_geld_2_vor_vorrang_ohne_kindereinkommen_m_fg(
    arbeitsl_geld_2_regelbedarf_m_fg: float,
    arbeitsl_geld_2_eink_ohne_kindereinkommen_m_fg: float,
    vermögen_bedürft_fg: float,
    arbeitsl_geld_2_vermög_freib_fg: float,
) -> float:
    """Calculate potential basic subsistence (after income deduction and wealth check).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_fg
        See :func:`arbeitsl_geld_2_regelbedarf_m_fg`.
    arbeitsl_geld_2_eink_ohne_kindereinkommen_m_fg
        See :func:`arbeitsl_geld_2_eink_ohne_kindereinkommen_m_fg`.
    arbeitsl_geld_2_vermög_freib_fg
        See :func:`arbeitsl_geld_2_vermög_freib_fg`.
    vermögen_bedürft_fg
        See :func:`vermögen_bedürft_fg`.

    Returns
    -------

    """

    # Check wealth exemption
    if vermögen_bedürft_fg > arbeitsl_geld_2_vermög_freib_fg:
        out = 0.0
    else:
        # Deduct income from various sources
        out = max(
            0.0,
            arbeitsl_geld_2_regelbedarf_m_fg
            - arbeitsl_geld_2_eink_ohne_kindereinkommen_m_fg,
        )

    return out
