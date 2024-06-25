"""Functions to calculate basic needs according to SGB II."""

from _gettsim.shared import policy_info


def arbeitsl_geld_2_regelbedarf_m(
    arbeitsl_geld_2_regelsatz_m: float,
    arbeitsl_geld_2_kost_unterk_m: float,
) -> float:
    """Basic monthly subsistence level on individual level.

    This includes cost of dwelling.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.:

    Parameters
    ----------
    arbeitsl_geld_2_regelsatz_m
        See :func:`arbeitsl_geld_2_regelsatz_m`.
    arbeitsl_geld_2_kost_unterk_m
        See :func:`arbeitsl_geld_2_kost_unterk_m`.

    Returns
    -------
    float checks the minimum monthly needs of an household.

    """
    return arbeitsl_geld_2_regelsatz_m + arbeitsl_geld_2_kost_unterk_m


def _arbeitsl_geld_2_alleinerz_mehrbedarf_m(
    alleinerz: bool,
    anz_kinder_fg: int,
    anz_kinder_bis_6_fg: int,
    anz_kinder_bis_15_fg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Compute additional SGB II need for single parents.

    Additional need for single parents. Maximum 60% of the standard amount on top if
    you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    alleinerz
        See :func:`alleinerz`.
    anz_kinder_fg
        See :func:`anz_kinder_fg`.
    anz_kinder_bis_6_fg
        See :func:`anz_kinder_bis_6_fg`.
    anz_kinder_bis_15_fg
        See :func:`anz_kinder_bis_15_fg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.


    Returns
    -------
    float checks how much more a single parent need.

    """
    if alleinerz:
        # Clip value at calculated minimal share and given upper share
        # Note that upper limit is applied last (for many children lower
        # could be greater than upper)
        out = min(
            max(
                # Minimal Mehrbedarf share. Minimal rate times number of children
                arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"]
                * anz_kinder_fg,
                # Special case if 1 kid below 6 or 2,3 below 15.
                (
                    arbeitsl_geld_2_params["mehrbedarf_anteil"][
                        "kind_unter_7_oder_mehr"
                    ]
                    if (anz_kinder_bis_6_fg >= 1) or (2 <= anz_kinder_bis_15_fg <= 3)
                    else 0.0
                ),
            ),
            arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"],
        )
    else:
        out = 0.0
    return out


@policy_info(end_date="2010-12-31", name_in_dag="arbeitsl_geld_2_kindersatz_m")
def arbeitsl_geld_2_kindersatz_m_bis_2010(
    alter: int,
    gleiche_fg_kindergeldempfänger_kind: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs of children until 2010.

    Since 2010 children get additional shares instead of lump sum payments.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter`.
    gleiche_fg_kindergeldempfänger_kind
        See :func:`gleiche_fg_kindergeldempfänger_kind`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with SGB II needs of children until year 2010.

    """
    anteile = arbeitsl_geld_2_params["anteil_regelsatz_kinder"]
    regelsatz = arbeitsl_geld_2_params["regelsatz"]

    if alter <= anteile[6]["max_alter"] and gleiche_fg_kindergeldempfänger_kind:
        out = regelsatz * anteile[6]["anteil"]
    elif alter <= anteile[5]["max_alter"] and gleiche_fg_kindergeldempfänger_kind:
        out = regelsatz * anteile[5]["anteil"]
    elif alter <= anteile[4]["max_alter"] and gleiche_fg_kindergeldempfänger_kind:
        out = regelsatz * anteile[4]["anteil"]

    return float(out)


@policy_info(start_date="2011-01-01", name_in_dag="arbeitsl_geld_2_kindersatz_m")
def arbeitsl_geld_2_kindersatz_m_ab_2011(
    alter: int,
    gleiche_fg_kindergeldempfänger_kind: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs of children since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter`.
    gleiche_fg_kindergeldempfänger_kind
        See :func:`gleiche_fg_kindergeldempfänger_kind`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    SGB II needs of child

    """

    if (
        alter <= arbeitsl_geld_2_params["regelsatz"][6]["max_alter"]
        and gleiche_fg_kindergeldempfänger_kind
    ):
        out = arbeitsl_geld_2_params["regelsatz"][6]["anteil"]
    elif (
        alter <= arbeitsl_geld_2_params["regelsatz"][5]["max_alter"]
        and gleiche_fg_kindergeldempfänger_kind
    ):
        out = arbeitsl_geld_2_params["regelsatz"][5]["anteil"]
    elif (
        alter <= arbeitsl_geld_2_params["regelsatz"][4]["max_alter"]
        and gleiche_fg_kindergeldempfänger_kind
    ):
        out = arbeitsl_geld_2_params["regelsatz"][4]["anteil"]
    elif gleiche_fg_kindergeldempfänger_kind:  # adult children with parents in FG
        out = arbeitsl_geld_2_params["regelsatz"][3]

    kindersofortzuschl = arbeitsl_geld_2_params.get("kindersofortzuschl", 0.0)
    out += kindersofortzuschl

    return float(out)


@policy_info(end_date="2010-12-31", name_in_dag="arbeitsl_geld_2_erwachsenensatz_m")
def arbeitsl_geld_2_erwachsenensatz_bis_2010_m(
    anz_erwachsene_bg: int,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m: float,
    arbeitsl_geld_2_kindersatz_m: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs for adults without dwelling.

    Parameters
    ----------
    anz_erwachsene_bg
        See :func:`anz_erwachsene_bg`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m`.
    arbeitsl_geld_2_kindersatz_m
        See :func:`arbeitsl_geld_2_kindersatz_m`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if alleinerz:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        )
    elif p_id_einstandspartner > 0:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
        )

    weitere_erwachsene = max(anz_erwachsene_bg - 2, 0)
    if anz_erwachsene_bg == 1:
        satz_erwachsene = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        )
    elif anz_erwachsene_bg >= 2:
        satz_erwachsene = arbeitsl_geld_2_params["regelsatz"] * (
            2 * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + weitere_erwachsene
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        )
    else:
        satz_erwachsene = 0
    return satz_erwachsene + arbeitsl_geld_2_kindersatz_m


@policy_info(start_date="2011-01-01", name_in_dag="arbeitsl_geld_2_erwachsenensatz_m")
def arbeitsl_geld_2_erwachsenensatz_ab_2011_m(
    anz_erwachsene_bg: int,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg: float,
    arbeitsl_geld_2_kindersatz_m_bg: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs for adults without dwelling since 2011.

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

    weitere_erwachsene = max(anz_erwachsene_bg - 2, 0)
    if anz_erwachsene_bg == 1:
        satz_erwachsene = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        )
    elif anz_erwachsene_bg >= 2:
        satz_erwachsene = arbeitsl_geld_2_params["regelsatz"][2] * (
            2 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        ) + ((arbeitsl_geld_2_params["regelsatz"][3] + zuschlag) * weitere_erwachsene)
    elif anz_erwachsene_bg == 0:
        satz_erwachsene = 0

    return satz_erwachsene + arbeitsl_geld_2_kindersatz_m_bg


def arbeitsl_geld_2_regelsatz_m(
    arbeitsl_geld_2_erwachsenensatz_m: float,
    arbeitsl_geld_2_kindersatz_m: float,
) -> float:
    """Calculate basic monthly subsistence without dwelling until 2010.

    Parameters
    ----------
    arbeitsl_geld_2_erwachsenensatz_m
        See :func:`arbeitsl_geld_2_erwachsenensatz_m`.
    arbeitsl_geld_2_kindersatz_m
        See :func:`arbeitsl_geld_2_kindersatz_m`.

    Returns
    -------


    """

    return arbeitsl_geld_2_erwachsenensatz_m + arbeitsl_geld_2_kindersatz_m
