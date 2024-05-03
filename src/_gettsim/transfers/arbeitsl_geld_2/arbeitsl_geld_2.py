from _gettsim.shared import policy_info


def arbeitsl_geld_2_m_bg(
    arbeitsl_geld_2_vor_vorrang_m_bg: float,
    wohngeld_vorrang_hh: bool,
    kinderzuschl_vorrang_bg: bool,
    wohngeld_kinderzuschl_vorrang_hh: bool,
    erwachsene_alle_rentner_hh: bool,
) -> float:
    """Calculate final monthly subsistence payment on household level.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_vor_vorrang_m_bg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_bg`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    kinderzuschl_vorrang_bg
        See :func:`kinderzuschl_vorrang_bg`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh`.

    Returns
    -------
    float with the income by unemployment insurance on household level.

    """
    if (
        wohngeld_vorrang_hh
        or kinderzuschl_vorrang_bg
        or wohngeld_kinderzuschl_vorrang_hh
        or erwachsene_alle_rentner_hh
    ):
        out = 0.0
    else:
        out = arbeitsl_geld_2_vor_vorrang_m_bg

    return out


def arbeitsl_geld_2_regelbedarf_m_bg(
    arbeitsl_geld_2_regelsatz_m_bg: float,
    arbeitsl_geld_2_kost_unterk_m_bg: float,
) -> float:
    """Basic monthly subsistence level on household level.

    This includes cost of dwelling.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.:

    Parameters
    ----------
    arbeitsl_geld_2_regelsatz_m_bg
        See :func:`arbeitsl_geld_2_regelsatz_m_bg`.
    arbeitsl_geld_2_kost_unterk_m_bg
        See :func:`arbeitsl_geld_2_kost_unterk_m_bg`.

    Returns
    -------
    float checks the minimum monthly needs of an household.

    """
    return arbeitsl_geld_2_regelsatz_m_bg + arbeitsl_geld_2_kost_unterk_m_bg


def _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg(
    alleinerz_bg: bool,
    anz_kinder_bg: int,
    anz_kinder_bis_6_bg: int,
    anz_kinder_bis_15_bg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Compute additional need for single parents.

    Additional need for single parents. Maximum 60% of the standard amount on top if
    you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    alleinerz_bg
        See :func:`alleinerz_bg`.
    anz_kinder_bg
        See :func:`anz_kinder_bg`.
    anz_kinder_bis_6_bg
        See :func:`anz_kinder_bis_6_bg`.
    anz_kinder_bis_15_bg
        See :func:`anz_kinder_bis_15_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.


    Returns
    -------
    float checks how much more a single parent need.

    """
    if alleinerz_bg:
        # Clip value at calculated minimal share and given upper share
        # Note that upper limit is applied last (for many children lower
        # could be greater than upper)
        out = min(
            max(
                # Minimal Mehrbedarf share. Minimal rate times number of children
                arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"]
                * anz_kinder_bg,
                # Special case if 1 kid below 6 or 2,3 below 15.
                (
                    arbeitsl_geld_2_params["mehrbedarf_anteil"][
                        "kind_unter_7_oder_mehr"
                    ]
                    if (anz_kinder_bis_6_bg >= 1) or (2 <= anz_kinder_bis_15_bg <= 3)
                    else 0.0
                ),
            ),
            arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"],
        )
    else:
        out = 0.0
    return out


@policy_info(end_date="2010-12-31", name_in_dag="arbeitsl_geld_2_kindersatz_m_bg")
def arbeitsl_geld_2_kindersatz_m_bg_bis_2010(
    anz_kinder_bis_5_bg: int,
    anz_kinder_ab_6_bis_13_bg: int,
    anz_kinder_ab_14_bis_24_bg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence for children until 2010. Since 2010 children
    get additional shares instead of lump sum payments.

    Parameters
    ----------
    anz_kinder_bis_5_bg
        See :func:`anz_kinder_bis_5_bg`.
    anz_kinder_ab_6_bis_13_bg
        See :func:`anz_kinder_ab_6_bis_13_bg`.
    anz_kinder_ab_14_bis_24_bg
        See :func:`anz_kinder_ab_14_bis_24_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the support of children until year 2010.

    """
    # Dictionary of additional shares.
    anteile = arbeitsl_geld_2_params["anteil_regelsatz"]

    # Multiply number of kids in age range with corresponding additional share
    out = arbeitsl_geld_2_params["regelsatz"] * (
        anteile["kinder_bis_5"] * anz_kinder_bis_5_bg
        + anteile["kinder_ab_6_bis_13"] * anz_kinder_ab_6_bis_13_bg
        + anteile["kinder_ab_14_bis_24"] * anz_kinder_ab_14_bis_24_bg
    )

    return float(out)


@policy_info(start_date="2011-01-01", name_in_dag="arbeitsl_geld_2_kindersatz_m_bg")
def arbeitsl_geld_2_kindersatz_m_bg_ab_2011(
    anz_kinder_bis_5_bg: int,
    anz_kinder_ab_6_bis_13_bg: int,
    anz_kinder_ab_14_bis_17_bg: int,
    anz_kinder_ab_18_bis_24_bg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence for children since 2011. Here the sum in euro
    is directly in the law.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    anz_kinder_bis_5_bg
        See :func:`anz_kinder_bis_5_bg`.
    anz_kinder_ab_6_bis_13_bg
        See :func:`anz_kinder_ab_6_bis_13_bg`.
    anz_kinder_ab_14_bis_17_bg
        See :func:`anz_kinder_ab_14_bis_17_bg`.
    anz_kinder_ab_18_bis_24_bg
        See :func:`anz_kinder_ab_18_bis_24_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the support of children since year 2011

    """

    # Sum payments for each age group
    out = (
        arbeitsl_geld_2_params["regelsatz"][6] * anz_kinder_bis_5_bg
        + arbeitsl_geld_2_params["regelsatz"][5] * anz_kinder_ab_6_bis_13_bg
        + arbeitsl_geld_2_params["regelsatz"][4] * anz_kinder_ab_14_bis_17_bg
        + arbeitsl_geld_2_params["regelsatz"][3] * anz_kinder_ab_18_bis_24_bg
    )

    kindersofortzuschl = arbeitsl_geld_2_params.get("kindersofortzuschl", 0.0)
    out += kindersofortzuschl * (
        anz_kinder_bis_5_bg
        + anz_kinder_ab_6_bis_13_bg
        + anz_kinder_ab_14_bis_17_bg
        + anz_kinder_ab_18_bis_24_bg
    )

    return float(out)


@policy_info(end_date="2010-12-31", name_in_dag="arbeitsl_geld_2_regelsatz_m_bg")
def arbeitsl_geld_2_regelsatz_m_bg_bis_2010(
    anz_erwachsene_bg: int,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg: float,
    arbeitsl_geld_2_kindersatz_m_bg: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence without dwelling until 2010.

    Parameters
    ----------
    anz_erwachsene_bg
        See :func:`anz_erwachsene_bg`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg`.
    arbeitsl_geld_2_kindersatz_m_bg
        See :func:`arbeitsl_geld_2_kindersatz_m_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the sum in Euro.

    """
    weitere_erwachsene = max(anz_erwachsene_bg - 2, 0)
    if anz_erwachsene_bg == 1:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            2 * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + weitere_erwachsene
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        )

    return out + arbeitsl_geld_2_kindersatz_m_bg


@policy_info(start_date="2011-01-01", name_in_dag="arbeitsl_geld_2_regelsatz_m_bg")
def arbeitsl_geld_2_regelsatz_m_bg_ab_2011(
    anz_erwachsene_bg: int,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg: float,
    arbeitsl_geld_2_kindersatz_m_bg: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence without dwelling since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    anz_erwachsene_bg
        See :func:`anz_erwachsene_bg`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg`.
    arbeitsl_geld_2_kindersatz_m_bg
        See :func:`arbeitsl_geld_2_kindersatz_m_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the minimum needs of an household in Euro.

    """
    zuschlag = arbeitsl_geld_2_params.get("kindersofortzuschl", 0)

    if anz_erwachsene_bg == 1:
        satz_erwachsene = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        )
    elif anz_erwachsene_bg >= 2:
        weitere_erwachsene = max(anz_erwachsene_bg - 2, 0)
        satz_erwachsene = arbeitsl_geld_2_params["regelsatz"][2] * (
            2 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        ) + ((arbeitsl_geld_2_params["regelsatz"][3] + zuschlag) * weitere_erwachsene)
    else:
        satz_erwachsene = 0

    return satz_erwachsene + arbeitsl_geld_2_kindersatz_m_bg


def arbeitsl_geld_2_vor_vorrang_m_bg(  # noqa: PLR0913
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    kindergeld_m_bg: float,
    kind_unterh_erhalt_m_bg: float,
    unterhaltsvors_m_bg: float,
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
    kindergeld_m_bg
        See :func:`kindergeld_m_bg`.
    kind_unterh_erhalt_m_bg
        See basic input variable
        :ref:`kind_unterh_erhalt_m_bg <kind_unterh_erhalt_m_bg>`.
    unterhaltsvors_m_bg
        See :func:`unterhaltsvors_m_bg`.
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
            arbeitsl_geld_2_regelbedarf_m_bg
            - arbeitsl_geld_2_eink_m_bg
            - kind_unterh_erhalt_m_bg
            - unterhaltsvors_m_bg
            - kindergeld_m_bg,
        )

    return out
