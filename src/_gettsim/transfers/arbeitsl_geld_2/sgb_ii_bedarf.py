"""Functions to calculate basic needs according to SGB II."""

from _gettsim.shared import policy_info


def arbeitsl_geld_2_regelbedarf_m_bg(
    arbeitsl_geld_2_regelsatz_m_bg: float,
    arbeitsl_geld_2_kost_unterk_m_bg: float,
) -> float:
    """Basic monthly subsistence level on individual level.

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
    else:
        out = 0.0

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

    kindersofortzuschl = arbeitsl_geld_2_params.get("kindersofortzuschl", 0.0)

    if (
        alter <= arbeitsl_geld_2_params["regelsatz"][6]["max_alter"]
        and gleiche_fg_kindergeldempfänger_kind
    ):
        out = arbeitsl_geld_2_params["regelsatz"][6]["bedarf"] + kindersofortzuschl
    elif (
        alter <= arbeitsl_geld_2_params["regelsatz"][5]["max_alter"]
        and gleiche_fg_kindergeldempfänger_kind
    ):
        out = arbeitsl_geld_2_params["regelsatz"][5]["bedarf"] + kindersofortzuschl
    elif (
        alter <= arbeitsl_geld_2_params["regelsatz"][4]["max_alter"]
        and gleiche_fg_kindergeldempfänger_kind
    ):
        out = arbeitsl_geld_2_params["regelsatz"][4]["bedarf"] + kindersofortzuschl
    elif gleiche_fg_kindergeldempfänger_kind:  # adult children with parents in FG
        out = arbeitsl_geld_2_params["regelsatz"][3] + kindersofortzuschl
    else:
        out = 0.0

    return float(out)


@policy_info(end_date="2010-12-31", name_in_dag="arbeitsl_geld_2_erwachsenensatz_m")
def arbeitsl_geld_2_erwachsenensatz_bis_2010_m(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m: float,
    arbeitsl_geld_2_kindersatz_m: float,
    p_id_einstandspartner: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs for adults without dwelling.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m`.
    arbeitsl_geld_2_kindersatz_m
        See :func:`arbeitsl_geld_2_kindersatz_m`.
    p_id_einstandspartner
        See basic input variable :ref:`p_id_einstandspartner`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if p_id_einstandspartner > 0:  # BG with 2 adults
        out = arbeitsl_geld_2_params["regelsatz"] * (
            arbeitsl_geld_2_params["anteil_regelsatz_erwachsene"]["zwei_erwachsene"]
        )
    elif arbeitsl_geld_2_kindersatz_m == 0.0:  # BG with 1 adult
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m
        )
    else:
        out = 0.0

    return out


@policy_info(start_date="2011-01-01", name_in_dag="arbeitsl_geld_2_erwachsenensatz_m")
def arbeitsl_geld_2_erwachsenensatz_ab_2011_m(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m: float,
    arbeitsl_geld_2_kindersatz_m: float,
    p_id_einstandspartner: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs for adults without dwelling since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m`.
    arbeitsl_geld_2_kindersatz_m
        See :func:`arbeitsl_geld_2_kindersatz_m`.
    p_id_einstandspartner
        See basic input variable :ref:`p_id_einstandspartner`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the minimum needs of an household in Euro.

    """
    if p_id_einstandspartner > 0:  # BG with 2 adults
        out = arbeitsl_geld_2_params["regelsatz"][2]
    elif arbeitsl_geld_2_kindersatz_m == 0.0:  # BG with 1 adult
        out = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m
        )
    else:
        out = 0.0

    return out


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
