"""Subsistence transfer for the elderly (Grundsicherung im Alter)."""

from _gettsim.functions.policy_function import policy_function


@policy_function
def betrag_m_eg(  # noqa: PLR0913
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    mehrbedarf_schwerbehinderung_g_m_eg: float,
    kindergeld__betrag_m_eg: float,
    kind_unterh_erhalt_m_eg: float,
    unterhaltsvorschuss__betrag_m_eg: float,
    einkommen_m_eg: float,
    erwachsene_alle_rentner_hh: bool,
    vermögen_bedürft_eg: float,
    vermögen_freibetrag_eg: float,
    anz_kinder_eg: int,
    anz_personen_eg: int,
) -> float:
    """Calculate Grundsicherung im Alter on household level.

    # ToDo: There is no check for Wohngeld included as Wohngeld is
    # ToDo: currently not implemented for retirees.

    Parameters
    ----------
    arbeitslosengeld_2__regelbedarf_m_bg
        See :func:`arbeitslosengeld_2__regelbedarf_m_bg`.
    mehrbedarf_schwerbehinderung_g_m_eg
        See :func:`mehrbedarf_schwerbehinderung_g_m_eg`.
    kindergeld__betrag_m_eg
        See :func:`kindergeld__betrag_m_eg`.
    kind_unterh_erhalt_m_eg
        See basic input variable
        :ref:`kind_unterh_erhalt_m_eg <kind_unterh_erhalt_m_eg>`.
    unterhaltsvorschuss__betrag_m_eg
        See :func:`unterhaltsvorschuss__betrag_m_eg`.
    einkommen_m_eg
        See :func:`einkommen_m_eg`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh`.
    vermögen_bedürft_eg
        See basic input variable :ref:`vermögen_bedürft_eg`.
    vermögen_freibetrag_eg
        See :func:`vermögen_freibetrag_eg`.
    anz_kinder_eg
        See :func:`anz_kinder_eg`.
    anz_personen_eg
        See :func:`anz_personen_eg`.
    Returns
    -------

    """

    # TODO(@ChristianZimpelmann): Treatment of Bedarfsgemeinschaften with both retirees
    # and unemployed job seekers probably incorrect
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/703

    # TODO(@MImmesberger): Check which variable is the correct Regelbedarf in place of
    # `arbeitslosengeld_2__regelbedarf_m_bg`
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/702

    # TODO (@MImmesberger): Remove `anz_kinder_eg == anz_personen_eg` condition once
    # `erwachsene_alle_rentner_hh`` is replaced by a more accurate variable.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/696

    # Wealth check
    # Only pay Grundsicherung im Alter if all adults are retired (see docstring)
    if (
        (vermögen_bedürft_eg >= vermögen_freibetrag_eg)
        or (not erwachsene_alle_rentner_hh)
        or (anz_kinder_eg == anz_personen_eg)
    ):
        out = 0.0
    else:
        # Subtract income
        out = (
            arbeitslosengeld_2__regelbedarf_m_bg
            + mehrbedarf_schwerbehinderung_g_m_eg
            - einkommen_m_eg
            - kind_unterh_erhalt_m_eg
            - unterhaltsvorschuss__betrag_m_eg
            - kindergeld__betrag_m_eg
        )

    return max(out, 0.0)


@policy_function
def mehrbedarf_schwerbehinderung_g_m(
    schwerbeh_g: bool,
    anz_erwachsene_eg: int,
    grunds_im_alter_params: dict,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate additional allowance for individuals with disabled person's pass G.

    Parameters
    ----------
    schwerbeh_g
        See basic input variable :ref:`behinderungsgrad <schwerbeh_g>`.
    anz_erwachsene_eg
        See :func:`anz_erwachsene_eg`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    Returns
    -------

    """
    # mehrbedarf for disabilities = % of regelsatz of the person getting the mehrbedarf
    mehrbedarf_single = (
        (arbeitsl_geld_2_params["regelsatz"][1])
        * (grunds_im_alter_params["mehrbedarf_schwerbeh_g"])
    )
    mehrbedarf_in_couple = (
        (arbeitsl_geld_2_params["regelsatz"][2])
        * (grunds_im_alter_params["mehrbedarf_schwerbeh_g"])
    )

    if (schwerbeh_g) and (anz_erwachsene_eg == 1):
        out = mehrbedarf_single
    elif (schwerbeh_g) and (anz_erwachsene_eg > 1):
        out = mehrbedarf_in_couple
    else:
        out = 0.0

    return out


@policy_function
def vermögen_freibetrag_eg(
    anz_erwachsene_fg: int,
    anz_kinder_fg: int,
    grunds_im_alter_params: dict,
) -> float:
    """Calculate wealth not considered for Grundsicherung im Alter on household level.

    Parameters
    ----------
    anz_erwachsene_fg
        See :func:`anz_erwachsene_fg`.
    anz_kinder_fg
        See :func:`anz_kinder_fg`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    out = (
        grunds_im_alter_params["vermögensfreibetrag"]["adult"] * anz_erwachsene_fg
        + grunds_im_alter_params["vermögensfreibetrag"]["child"] * anz_kinder_fg
    )
    return out
