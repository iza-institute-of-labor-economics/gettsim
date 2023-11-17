from _gettsim.shared import dates_active


def arbeitsl_geld_2_m_bg(
    arbeitsl_geld_2_vor_vorrang_m_hh: float,
    wohngeld_vorrang_hh: bool,
    kinderzuschl_vorrang_hh: bool,
    wohngeld_kinderzuschl_vorrang_hh: bool,
    erwachsene_alle_rentner_hh: bool,
) -> float:
    """Calculate final monthly subsistence payment on household level.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_vor_vorrang_m_hh
        See :func:`arbeitsl_geld_2_vor_vorrang_m_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    kinderzuschl_vorrang_hh
        See :func:`kinderzuschl_vorrang_hh`.
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
        or kinderzuschl_vorrang_hh
        or wohngeld_kinderzuschl_vorrang_hh
        or erwachsene_alle_rentner_hh
    ):
        out = 0.0
    else:
        out = arbeitsl_geld_2_vor_vorrang_m_hh

    return out


def arbeitsl_geld_2_regelbedarf_m_hh(
    arbeitsl_geld_2_regelsatz_m_hh: float,
    arbeitsl_geld_2_kost_unterk_m_hh: float,
) -> float:
    """Basic monthly subsistence level on household level.

    This includes cost of dwelling.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.:

    Parameters
    ----------
    arbeitsl_geld_2_regelsatz_m_hh
        See :func:`arbeitsl_geld_2_regelsatz_m_hh`.
    arbeitsl_geld_2_kost_unterk_m_hh
        See :func:`arbeitsl_geld_2_kost_unterk_m_hh`.

    Returns
    -------
    float checks the minimum monthly needs of an household.

    """
    return arbeitsl_geld_2_regelsatz_m_hh + arbeitsl_geld_2_kost_unterk_m_hh


def _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh(
    alleinerz_hh: bool,
    anz_kinder_hh: int,
    anz_kinder_bis_6_hh: int,
    anz_kinder_bis_15_hh: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Compute additional need for single parents.

    Additional need for single parents. Maximum 60% of the standard amount on top if
    you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    alleinerz_hh
        See :func:`alleinerz_hh`.
    anz_kinder_hh
        See :func:`anz_kinder_hh`.
    anz_kinder_bis_6_hh
        See :func:`anz_kinder_bis_6_hh`.
    anz_kinder_bis_15_hh
        See :func:`anz_kinder_bis_15_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.


    Returns
    -------
    float checks how much more a single parent need.

    """
    if alleinerz_hh:
        # Clip value at calculated minimal share and given upper share
        # Note that upper limit is applied last (for many children lower
        # could be greater than upper)
        out = min(
            max(
                # Minimal Mehrbedarf share. Minimal rate times number of children
                arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"]
                * anz_kinder_hh,
                # Special case if 1 kid below 6 or 2,3 below 15.
                arbeitsl_geld_2_params["mehrbedarf_anteil"]["kind_unter_7_oder_mehr"]
                if (anz_kinder_bis_6_hh >= 1) or (2 <= anz_kinder_bis_15_hh <= 3)
                else 0.0,
            ),
            arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"],
        )
    else:
        out = 0.0
    return out


@dates_active(end="2010-12-31", change_name="arbeitsl_geld_2_kindersatz_m_hh")
def arbeitsl_geld_2_kindersatz_m_hh_bis_2010(
    anz_kinder_bis_5_hh: int,
    anz_kinder_ab_6_bis_13_hh: int,
    anz_kinder_ab_14_bis_24_hh: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence for children until 2010. Since 2010 children
    get additional shares instead of lump sum payments.

    Parameters
    ----------
    anz_kinder_bis_5_hh
        See :func:`anz_kinder_bis_5_hh`.
    anz_kinder_ab_6_bis_13_hh
        See :func:`anz_kinder_ab_6_bis_13_hh`.
    anz_kinder_ab_14_bis_24_hh
        See :func:`anz_kinder_ab_14_bis_24_hh`.
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
        anteile["kinder_bis_5"] * anz_kinder_bis_5_hh
        + anteile["kinder_ab_6_bis_13"] * anz_kinder_ab_6_bis_13_hh
        + anteile["kinder_ab_14_bis_24"] * anz_kinder_ab_14_bis_24_hh
    )

    return float(out)


@dates_active(start="2011-01-01", change_name="arbeitsl_geld_2_kindersatz_m_hh")
def arbeitsl_geld_2_kindersatz_m_hh_ab_2011(
    anz_kinder_bis_5_hh: int,
    anz_kinder_ab_6_bis_13_hh: int,
    anz_kinder_ab_14_bis_17_hh: int,
    anz_kinder_ab_18_bis_24_hh: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence for children since 2011. Here the sum in euro
    is directly in the law.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    anz_kinder_bis_5_hh
        See :func:`anz_kinder_bis_5_hh`.
    anz_kinder_ab_6_bis_13_hh
        See :func:`anz_kinder_ab_6_bis_13_hh`.
    anz_kinder_ab_14_bis_17_hh
        See :func:`anz_kinder_ab_14_bis_17_hh`.
    anz_kinder_ab_18_bis_24_hh
        See :func:`anz_kinder_ab_18_bis_24_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the support of children since year 2011

    """

    # Sum payments for each age group
    out = (
        arbeitsl_geld_2_params["regelsatz"][6] * anz_kinder_bis_5_hh
        + arbeitsl_geld_2_params["regelsatz"][5] * anz_kinder_ab_6_bis_13_hh
        + arbeitsl_geld_2_params["regelsatz"][4] * anz_kinder_ab_14_bis_17_hh
        + arbeitsl_geld_2_params["regelsatz"][3] * anz_kinder_ab_18_bis_24_hh
    )

    kindersofortzuschl = arbeitsl_geld_2_params.get("kindersofortzuschl", 0.0)
    out += kindersofortzuschl * (
        anz_kinder_bis_5_hh
        + anz_kinder_ab_6_bis_13_hh
        + anz_kinder_ab_14_bis_17_hh
        + anz_kinder_ab_18_bis_24_hh
    )

    return float(out)


@dates_active(end="2010-12-31", change_name="arbeitsl_geld_2_regelsatz_m_hh")
def arbeitsl_geld_2_regelsatz_m_hh_bis_2010(
    anz_erwachsene_hh: int,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: float,
    arbeitsl_geld_2_kindersatz_m_hh: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence without dwelling until 2010.

    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    arbeitsl_geld_2_kindersatz_m_hh
        See :func:`arbeitsl_geld_2_kindersatz_m_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the sum in Euro.

    """
    # Note that we, currently, do not support households with more than 2 adults.
    weitere_erwachsene = max(anz_erwachsene_hh - 2, 0)
    if anz_erwachsene_hh == 1:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            2 * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + weitere_erwachsene
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        )

    return out + arbeitsl_geld_2_kindersatz_m_hh


@dates_active(start="2011-01-01", change_name="arbeitsl_geld_2_regelsatz_m_hh")
def arbeitsl_geld_2_regelsatz_m_hh_ab_2011(
    anz_erwachsene_hh: int,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: float,
    arbeitsl_geld_2_kindersatz_m_hh: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence without dwelling since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    arbeitsl_geld_2_kindersatz_m_hh
        See :func:`arbeitsl_geld_2_kindersatz_m_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the minimum needs of an household in Euro.

    """
    zuschlag = arbeitsl_geld_2_params.get("kindersofortzuschl", 0)

    weitere_erwachsene = max(anz_erwachsene_hh - 2, 0)
    if anz_erwachsene_hh == 1:
        out = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"][2] * (
            2 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        ) + ((arbeitsl_geld_2_params["regelsatz"][3] + zuschlag) * weitere_erwachsene)

    return out + arbeitsl_geld_2_kindersatz_m_hh


def arbeitsl_geld_2_vor_vorrang_m_hh(  # noqa: PLR0913
    arbeitsl_geld_2_regelbedarf_m_hh: float,
    kindergeld_m_hh: float,
    kind_unterh_erhalt_m_hh: float,
    unterhaltsvors_m_hh: float,
    arbeitsl_geld_2_eink_m_hh: float,
    vermögen_bedürft_hh: float,
    arbeitsl_geld_2_vermög_freib_hh: float,
) -> float:
    """Calculate potential basic subsistence (after income deduction and wealth check).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_hh
        See :func:`arbeitsl_geld_2_regelbedarf_m_hh`.
    kindergeld_m_hh
        See :func:`kindergeld_m_hh`.
    kind_unterh_erhalt_m_hh
        See basic input variable
        :ref:`kind_unterh_erhalt_m_hh <kind_unterh_erhalt_m_hh>`.
    unterhaltsvors_m_hh
        See :func:`unterhaltsvors_m_hh`.
    arbeitsl_geld_2_eink_m_hh
        See :func:`arbeitsl_geld_2_eink_m_hh`.
    arbeitsl_geld_2_vermög_freib_hh
        See :func:`arbeitsl_geld_2_vermög_freib_hh`.
    vermögen_bedürft_hh
        See basic input variable :ref:`vermögen_bedürft_hh <vermögen_bedürft_hh>`.

    Returns
    -------

    """

    # Check wealth exemption
    if vermögen_bedürft_hh > arbeitsl_geld_2_vermög_freib_hh:
        out = 0.0
    else:
        # Deduct income from various sources
        out = max(
            0.0,
            arbeitsl_geld_2_regelbedarf_m_hh
            - arbeitsl_geld_2_eink_m_hh
            - kind_unterh_erhalt_m_hh
            - unterhaltsvors_m_hh
            - kindergeld_m_hh,
        )

    return out
