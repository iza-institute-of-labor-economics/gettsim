"""Subsistence transfer for the elderly (Grundsicherung im Alter)."""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_m_eg(  # noqa: PLR0913
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    mehrbedarf_schwerbehinderung_g_m_eg: float,
    kindergeld__betrag_m_eg: float,
    unterhalt__tatsächlich_erhaltener_betrag_m_eg: float,
    unterhaltsvorschuss__betrag_m_eg: float,
    einkommen_m_eg: float,
    demographics__erwachsene_alle_rentner_hh: bool,
    demographics__vermögen_eg: float,
    vermögensfreibetrag_eg: float,
    arbeitslosengeld_2__anzahl_kinder_eg: int,
    arbeitslosengeld_2__anzahl_personen_eg: int,
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
    unterhalt__tatsächlich_erhaltener_betrag_m_eg
        See basic input variable
        :ref:`unterhalt__tatsächlich_erhaltener_betrag_m_eg <unterhalt__tatsächlich_erhaltener_betrag_m_eg>`.
    unterhaltsvorschuss__betrag_m_eg
        See :func:`unterhaltsvorschuss__betrag_m_eg`.
    einkommen_m_eg
        See :func:`einkommen_m_eg`.
    demographics__erwachsene_alle_rentner_hh
        See :func:`demographics__erwachsene_alle_rentner_hh`.
    demographics__vermögen_eg
        See basic input variable :ref:`demographics__vermögen_eg`.
    vermögensfreibetrag_eg
        See :func:`vermögensfreibetrag_eg`.
    arbeitslosengeld_2__anzahl_kinder_eg
        See :func:`arbeitslosengeld_2__anzahl_kinder_eg`.
    arbeitslosengeld_2__anzahl_personen_eg
        See :func:`arbeitslosengeld_2__anzahl_personen_eg`.
    Returns
    -------

    """

    # TODO(@ChristianZimpelmann): Treatment of Bedarfsgemeinschaften with both retirees
    # and unemployed job seekers probably incorrect
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/703

    # TODO(@MImmesberger): Check which variable is the correct Regelbedarf in place of
    # `arbeitslosengeld_2__regelbedarf_m_bg`
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/702

    # TODO (@MImmesberger): Remove `arbeitslosengeld_2__anzahl_kinder_eg ==
    # arbeitslosengeld_2__anzahl_personen_eg` condition once
    # `demographics__erwachsene_alle_rentner_hh`` is replaced by a more accurate
    # variable.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/696

    # Wealth check
    # Only pay Grundsicherung im Alter if all adults are retired (see docstring)
    if (
        (demographics__vermögen_eg >= vermögensfreibetrag_eg)
        or (not demographics__erwachsene_alle_rentner_hh)
        or (
            arbeitslosengeld_2__anzahl_kinder_eg
            == arbeitslosengeld_2__anzahl_personen_eg
        )
    ):
        out = 0.0
    else:
        # Subtract income
        out = (
            arbeitslosengeld_2__regelbedarf_m_bg
            + mehrbedarf_schwerbehinderung_g_m_eg
            - einkommen_m_eg
            - unterhalt__tatsächlich_erhaltener_betrag_m_eg
            - unterhaltsvorschuss__betrag_m_eg
            - kindergeld__betrag_m_eg
        )

    return max(out, 0.0)


@policy_function()
def mehrbedarf_schwerbehinderung_g_m(
    demographics__schwerbehindert_grad_g: bool,
    arbeitslosengeld_2__anzahl_erwachsene_eg: int,
    grunds_im_alter_params: dict,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate additional allowance for individuals with disabled person's pass G.

    Parameters
    ----------
    demographics__schwerbehindert_grad_g
        See basic input variable :ref:`demographics__behinderungsgrad <demographics__schwerbehindert_grad_g>`.
    arbeitslosengeld_2__anzahl_erwachsene_eg
        See :func:`arbeitslosengeld_2__anzahl_erwachsene_eg`.
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
        * (grunds_im_alter_params["mehrbedarf_bei_schwerbehinderungsgrad_g"])
    )
    mehrbedarf_in_couple = (
        (arbeitsl_geld_2_params["regelsatz"][2])
        * (grunds_im_alter_params["mehrbedarf_bei_schwerbehinderungsgrad_g"])
    )

    if (demographics__schwerbehindert_grad_g) and (
        arbeitslosengeld_2__anzahl_erwachsene_eg == 1
    ):
        out = mehrbedarf_single
    elif (demographics__schwerbehindert_grad_g) and (
        arbeitslosengeld_2__anzahl_erwachsene_eg > 1
    ):
        out = mehrbedarf_in_couple
    else:
        out = 0.0

    return out


@policy_function()
def vermögensfreibetrag_eg(
    arbeitslosengeld_2__anzahl_erwachsene_fg: int,
    arbeitslosengeld_2__anzahl_kinder_fg: int,
    grunds_im_alter_params: dict,
) -> float:
    """Calculate wealth not considered for Grundsicherung im Alter on household level.

    Parameters
    ----------
    arbeitslosengeld_2__anzahl_erwachsene_fg
        See :func:`arbeitslosengeld_2__anzahl_erwachsene_fg`.
    arbeitslosengeld_2__anzahl_kinder_fg
        See :func:`arbeitslosengeld_2__anzahl_kinder_fg`.
    grunds_im_alter_params
        See params documentation :ref:`grunds_im_alter_params <grunds_im_alter_params>`.

    Returns
    -------

    """
    out = (
        grunds_im_alter_params["vermögensfreibetrag"]["adult"]
        * arbeitslosengeld_2__anzahl_erwachsene_fg
        + grunds_im_alter_params["vermögensfreibetrag"]["child"]
        * arbeitslosengeld_2__anzahl_kinder_fg
    )
    return out
