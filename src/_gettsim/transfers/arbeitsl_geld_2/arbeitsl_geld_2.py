from _gettsim.shared import dates_active


def arbeitsl_geld_2_m_vg(
    arbeitsl_geld_2_vor_vorrang_m_vg: float,
    wohngeld_vorrang_vg: bool,
    kinderzuschl_vorrang_vg: bool,
    wohngeld_kinderzuschl_vorrang_vg: bool,
    erwachsene_alle_rentner_vg: bool,
) -> float:
    """Calculate final monthly subsistence payment on household level.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_vor_vorrang_m_vg
        See :func:`arbeitsl_geld_2_vor_vorrang_m_vg`.
    wohngeld_vorrang_vg
        See :func:`wohngeld_vorrang_vg`.
    kinderzuschl_vorrang_vg
        See :func:`kinderzuschl_vorrang_vg`.
    wohngeld_kinderzuschl_vorrang_vg
        See :func:`wohngeld_kinderzuschl_vorrang_vg`.
    erwachsene_alle_rentner_vg
        See :func:`erwachsene_alle_rentner_vg`.

    Returns
    -------
    float with the income by unemployment insurance on household level.

    """
    if (
        wohngeld_vorrang_vg
        or kinderzuschl_vorrang_vg
        or wohngeld_kinderzuschl_vorrang_vg
        or erwachsene_alle_rentner_vg
    ):
        out = 0.0
    else:
        out = arbeitsl_geld_2_vor_vorrang_m_vg

    return out


def arbeitsl_geld_2_regelbedarf_m_vg(
    arbeitsl_geld_2_regelsatz_m_vg: float,
    arbeitsl_geld_2_kost_unterk_m_vg: float,
) -> float:
    """Basic monthly subsistence level on household level.

    This includes cost of dwelling.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.:

    Parameters
    ----------
    arbeitsl_geld_2_regelsatz_m_vg
        See :func:`arbeitsl_geld_2_regelsatz_m_vg`.
    arbeitsl_geld_2_kost_unterk_m_vg
        See :func:`arbeitsl_geld_2_kost_unterk_m_vg`.

    Returns
    -------
    float checks the minimum monthly needs of an household.

    """
    return arbeitsl_geld_2_regelsatz_m_vg + arbeitsl_geld_2_kost_unterk_m_vg


def _arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg(
    alleinerz_vg: bool,
    anz_kinder_vg: int,
    anz_kinder_bis_6_vg: int,
    anz_kinder_bis_15_vg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Compute additional need for single parents.

    Additional need for single parents. Maximum 60% of the standard amount on top if
    you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    alleinerz_vg
        See :func:`alleinerz_vg`.
    anz_kinder_vg
        See :func:`anz_kinder_vg`.
    anz_kinder_bis_6_vg
        See :func:`anz_kinder_bis_6_vg`.
    anz_kinder_bis_15_vg
        See :func:`anz_kinder_bis_15_vg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.


    Returns
    -------
    float checks how much more a single parent need.

    """
    if alleinerz_vg:
        # Clip value at calculated minimal share and given upper share
        # Note that upper limit is applied last (for many children lower
        # could be greater than upper)
        out = min(
            max(
                # Minimal Mehrbedarf share. Minimal rate times number of children
                arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"]
                * anz_kinder_vg,
                # Special case if 1 kid below 6 or 2,3 below 15.
                arbeitsl_geld_2_params["mehrbedarf_anteil"]["kind_unter_7_oder_mehr"]
                if (anz_kinder_bis_6_vg >= 1) or (2 <= anz_kinder_bis_15_vg <= 3)
                else 0.0,
            ),
            arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"],
        )
    else:
        out = 0.0
    return out


@dates_active(end="2010-12-31", change_name="arbeitsl_geld_2_kindersatz_m_vg")
def arbeitsl_geld_2_kindersatz_m_vg_bis_2010(
    anz_kinder_bis_5_vg: int,
    anz_kinder_ab_6_bis_13_vg: int,
    anz_kinder_ab_14_bis_24_vg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence for children until 2010. Since 2010 children
    get additional shares instead of lump sum payments.

    Parameters
    ----------
    anz_kinder_bis_5_vg
        See :func:`anz_kinder_bis_5_vg`.
    anz_kinder_ab_6_bis_13_vg
        See :func:`anz_kinder_ab_6_bis_13_vg`.
    anz_kinder_ab_14_bis_24_vg
        See :func:`anz_kinder_ab_14_bis_24_vg`.
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
        anteile["kinder_bis_5"] * anz_kinder_bis_5_vg
        + anteile["kinder_ab_6_bis_13"] * anz_kinder_ab_6_bis_13_vg
        + anteile["kinder_ab_14_bis_24"] * anz_kinder_ab_14_bis_24_vg
    )

    return float(out)


@dates_active(start="2011-01-01", change_name="arbeitsl_geld_2_kindersatz_m_vg")
def arbeitsl_geld_2_kindersatz_m_vg_ab_2011(
    anz_kinder_bis_5_vg: int,
    anz_kinder_ab_6_bis_13_vg: int,
    anz_kinder_ab_14_bis_17_vg: int,
    anz_kinder_ab_18_bis_24_vg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence for children since 2011. Here the sum in euro
    is directly in the law.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    anz_kinder_bis_5_vg
        See :func:`anz_kinder_bis_5_vg`.
    anz_kinder_ab_6_bis_13_vg
        See :func:`anz_kinder_ab_6_bis_13_vg`.
    anz_kinder_ab_14_bis_17_vg
        See :func:`anz_kinder_ab_14_bis_17_vg`.
    anz_kinder_ab_18_bis_24_vg
        See :func:`anz_kinder_ab_18_bis_24_vg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the support of children since year 2011

    """

    # Sum payments for each age group
    out = (
        arbeitsl_geld_2_params["regelsatz"][6] * anz_kinder_bis_5_vg
        + arbeitsl_geld_2_params["regelsatz"][5] * anz_kinder_ab_6_bis_13_vg
        + arbeitsl_geld_2_params["regelsatz"][4] * anz_kinder_ab_14_bis_17_vg
        + arbeitsl_geld_2_params["regelsatz"][3] * anz_kinder_ab_18_bis_24_vg
    )

    kindersofortzuschl = arbeitsl_geld_2_params.get("kindersofortzuschl", 0.0)
    out += kindersofortzuschl * (
        anz_kinder_bis_5_vg
        + anz_kinder_ab_6_bis_13_vg
        + anz_kinder_ab_14_bis_17_vg
        + anz_kinder_ab_18_bis_24_vg
    )

    return float(out)


@dates_active(end="2010-12-31", change_name="arbeitsl_geld_2_regelsatz_m_vg")
def arbeitsl_geld_2_regelsatz_m_vg_bis_2010(
    anz_erwachsene_vg: int,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg: float,
    arbeitsl_geld_2_kindersatz_m_vg: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence without dwelling until 2010.

    Parameters
    ----------
    anz_erwachsene_vg
        See :func:`anz_erwachsene_vg`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg`.
    arbeitsl_geld_2_kindersatz_m_vg
        See :func:`arbeitsl_geld_2_kindersatz_m_vg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the sum in Euro.

    """
    # Note that we, currently, do not support households with more than 2 adults.
    weitere_erwachsene = max(anz_erwachsene_vg - 2, 0)
    if anz_erwachsene_vg == 1:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            2 * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + weitere_erwachsene
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        )

    return out + arbeitsl_geld_2_kindersatz_m_vg


@dates_active(start="2011-01-01", change_name="arbeitsl_geld_2_regelsatz_m_vg")
def arbeitsl_geld_2_regelsatz_m_vg_ab_2011(
    anz_erwachsene_vg: int,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg: float,
    arbeitsl_geld_2_kindersatz_m_vg: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate basic monthly subsistence without dwelling since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    anz_erwachsene_vg
        See :func:`anz_erwachsene_vg`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg`.
    arbeitsl_geld_2_kindersatz_m_vg
        See :func:`arbeitsl_geld_2_kindersatz_m_vg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the minimum needs of an household in Euro.

    """
    zuschlag = arbeitsl_geld_2_params.get("kindersofortzuschl", 0)

    weitere_erwachsene = max(anz_erwachsene_vg - 2, 0)
    if anz_erwachsene_vg == 1:
        out = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"][2] * (
            2 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_vg
        ) + ((arbeitsl_geld_2_params["regelsatz"][3] + zuschlag) * weitere_erwachsene)

    return out + arbeitsl_geld_2_kindersatz_m_vg


def arbeitsl_geld_2_vor_vorrang_m_vg(  # noqa: PLR0913
    arbeitsl_geld_2_regelbedarf_m_vg: float,
    kindergeld_m_vg: float,
    kind_unterh_erhalt_m_vg: float,
    unterhaltsvors_m_vg: float,
    arbeitsl_geld_2_eink_m_vg: float,
    vermögen_bedürft_vg: float,
    arbeitsl_geld_2_vermög_freib_vg: float,
) -> float:
    """Calculate potential basic subsistence (after income deduction and wealth check).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_vg
        See :func:`arbeitsl_geld_2_regelbedarf_m_vg`.
    kindergeld_m_vg
        See :func:`kindergeld_m_vg`.
    kind_unterh_erhalt_m_vg
        See basic input variable
        :ref:`kind_unterh_erhalt_m_vg <kind_unterh_erhalt_m_vg>`.
    unterhaltsvors_m_vg
        See :func:`unterhaltsvors_m_vg`.
    arbeitsl_geld_2_eink_m_vg
        See :func:`arbeitsl_geld_2_eink_m_vg`.
    arbeitsl_geld_2_vermög_freib_vg
        See :func:`arbeitsl_geld_2_vermög_freib_vg`.
    vermögen_bedürft_vg
        See basic input variable :ref:`vermögen_bedürft_vg <vermögen_bedürft_vg>`.

    Returns
    -------

    """

    # Check wealth exemption
    if vermögen_bedürft_vg > arbeitsl_geld_2_vermög_freib_vg:
        out = 0.0
    else:
        # Deduct income from various sources
        out = max(
            0.0,
            arbeitsl_geld_2_regelbedarf_m_vg
            - arbeitsl_geld_2_eink_m_vg
            - kind_unterh_erhalt_m_vg
            - unterhaltsvors_m_vg
            - kindergeld_m_vg,
        )

    return out
