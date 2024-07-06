def arbeitsl_geld_2_m_bg(
    arbeitsl_geld_2_anspruchshöhe_m_bg: float,
    wohngeld_kinderzuschl_statt_arbeitsl_geld_2: bool,
    erwachsene_alle_rentner_hh: bool,
) -> float:
    """Calculate final monthly subsistence payment on household level.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_anspruchshöhe_m_bg
        See :func:`arbeitsl_geld_2_anspruchshöhe_m_bg`.
    wohngeld_kinderzuschl_statt_arbeitsl_geld_2
        See :func:`wohngeld_kinderzuschl_statt_arbeitsl_geld_2`.
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
    if (not wohngeld_kinderzuschl_statt_arbeitsl_geld_2) and (
        not erwachsene_alle_rentner_hh
    ):
        out = arbeitsl_geld_2_anspruchshöhe_m_bg
    else:
        out = 0.0

    return out


def arbeitsl_geld_2_anspruchshöhe_m_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_eink_m_bg: float,
    arbeitsl_geld_2_vermögensgrenze_unterschritten_m_bg: bool,
) -> float:
    """Calculate potential basic subsistence (after income deduction and wealth check).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_eink_m_bg
        See :func:`arbeitsl_geld_2_eink_m_bg`.
    arbeitsl_geld_2_vermögensgrenze_unterschritten_m_bg
        See :func:`arbeitsl_geld_2_vermögensgrenze_unterschritten_m_bg`.

    Returns
    -------

    """

    if arbeitsl_geld_2_vermögensgrenze_unterschritten_m_bg:
        # Deduct income from various sources
        out = max(
            0.0,
            arbeitsl_geld_2_regelbedarf_m_bg - arbeitsl_geld_2_eink_m_bg,
        )
    else:
        out = 0.0

    return out


def arbeitsl_geld_2_anspruchshöhe_m_fg(
    arbeitsl_geld_2_regelbedarf_m_fg: float,
    arbeitsl_geld_2_eink_m_fg: float,
    arbeitsl_geld_2_vermögensgrenze_unterschritten_m_fg: bool,
) -> float:
    """Calculate potential basic subsistence (after income deduction and wealth check).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_fg
        See :func:`arbeitsl_geld_2_regelbedarf_m_fg`.
    arbeitsl_geld_2_eink_m_fg
        See :func:`arbeitsl_geld_2_eink_m_fg`.
    arbeitsl_geld_2_vermögensgrenze_unterschritten_m_fg
        See :func:`arbeitsl_geld_2_vermögensgrenze_unterschritten_m_fg`.

    Returns
    -------

    """

    if arbeitsl_geld_2_vermögensgrenze_unterschritten_m_fg:
        # Deduct income from various sources
        out = max(
            0.0,
            arbeitsl_geld_2_regelbedarf_m_fg - arbeitsl_geld_2_eink_m_fg,
        )
    else:
        out = 0.0

    return out


def arbeitsl_geld_2_vermögensgrenze_unterschritten_m_bg(
    vermögen_bedürft_bg: float,
    arbeitsl_geld_2_vermög_freib_bg: float,
) -> bool:
    """Wealth is below the exemption limit for Arbeitslosengeld 2.

    Parameters
    ----------
    vermögen_bedürft_bg
        See basic input variable :ref:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.
    arbeitsl_geld_2_vermög_freib_bg
        See :func:`arbeitsl_geld_2_vermög_freib_bg`.

    Returns
    -------

    """
    return vermögen_bedürft_bg <= arbeitsl_geld_2_vermög_freib_bg


def arbeitsl_geld_2_vermögensgrenze_unterschritten_m_fg(
    vermögen_bedürft_fg: float,
    arbeitsl_geld_2_vermög_freib_fg: float,
) -> bool:
    """Wealth is below the exemption limit for Arbeitslosengeld 2.

    Parameters
    ----------
    vermögen_bedürft_fg
        See basic input variable :ref:`vermögen_bedürft_fg <vermögen_bedürft_fg>`.
    arbeitsl_geld_2_vermög_freib_fg
        See :func:`arbeitsl_geld_2_vermög_freib_fg`.

    Returns
    -------

    """
    return vermögen_bedürft_fg <= arbeitsl_geld_2_vermög_freib_fg
