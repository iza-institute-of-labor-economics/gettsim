"""Functions to calculate basic needs according to SGB II
(i.e., where Arbeitslosengeld 2 is defined)."""

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
                # Increased rated if children up to 6 and/or 2-3 up to 15 are present.
                (
                    arbeitsl_geld_2_params["mehrbedarf_anteil"][
                        "kind_bis_6_oder_mehrere_bis_15"
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
    same_fg_as_kindergeldempfänger: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs of children until 2010.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter`.
    same_fg_as_kindergeldempfänger
        See :func:`same_fg_as_kindergeldempfänger`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with SGB II needs of children until year 2010.

    """
    anteile = arbeitsl_geld_2_params["anteil_regelsatz_kinder"]
    regelsatz = arbeitsl_geld_2_params["regelsatz"]

    if (
        alter >= anteile["kind_zwischen_14_und_24"]["min_alter"]
        and alter <= anteile["kind_zwischen_14_und_24"]["max_alter"]
        and same_fg_as_kindergeldempfänger
    ):
        out = regelsatz * anteile["kind_zwischen_14_und_24"]["anteil"]
    elif (
        alter >= anteile["kind_zwischen_6_und_13"]["min_alter"]
        and alter <= anteile["kind_zwischen_6_und_13"]["max_alter"]
        and same_fg_as_kindergeldempfänger
    ):
        out = regelsatz * anteile["kind_zwischen_6_und_13"]["anteil"]
    elif (
        alter >= anteile["kind_bis_5"]["min_alter"]
        and alter <= anteile["kind_bis_5"]["max_alter"]
        and same_fg_as_kindergeldempfänger
    ):
        out = regelsatz * anteile["kind_bis_5"]["anteil"]
    else:
        out = 0.0

    return float(out)


@policy_info(start_date="2011-01-01", name_in_dag="arbeitsl_geld_2_kindersatz_m")
def arbeitsl_geld_2_kindersatz_m_ab_2011(
    alter: int,
    same_fg_as_kindergeldempfänger: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs of children since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter`.
    same_fg_as_kindergeldempfänger
        See :func:`same_fg_as_kindergeldempfänger`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    SGB II needs of child

    """

    out = arbeitsl_geld_2_params.get("kindersofortzuschl", 0.0)

    if (
        alter >= arbeitsl_geld_2_params["regelsatz"][6]["min_alter"]
        and alter <= arbeitsl_geld_2_params["regelsatz"][6]["max_alter"]
        and same_fg_as_kindergeldempfänger
    ):
        out += arbeitsl_geld_2_params["regelsatz"][6]["betrag"]
    elif (
        alter >= arbeitsl_geld_2_params["regelsatz"][5]["min_alter"]
        and alter <= arbeitsl_geld_2_params["regelsatz"][5]["max_alter"]
        and same_fg_as_kindergeldempfänger
    ):
        out += arbeitsl_geld_2_params["regelsatz"][5]["betrag"]
    elif (
        alter >= arbeitsl_geld_2_params["regelsatz"][4]["min_alter"]
        and alter <= arbeitsl_geld_2_params["regelsatz"][4]["max_alter"]
        and same_fg_as_kindergeldempfänger
    ):
        out += arbeitsl_geld_2_params["regelsatz"][4]["betrag"]
    elif same_fg_as_kindergeldempfänger:  # adult children with parents in FG
        out += arbeitsl_geld_2_params["regelsatz"][3]
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
    # BG has 2 adults
    if p_id_einstandspartner >= 0:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            arbeitsl_geld_2_params["anteil_regelsatz_erwachsene"]["zwei_erwachsene"]
        )
    # This observation is not a child, so BG has 1 adult
    elif arbeitsl_geld_2_kindersatz_m == 0.0:
        out = arbeitsl_geld_2_params["regelsatz"]
    else:
        out = 0.0

    return out * (1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m)


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
    # BG has 2 adults
    if p_id_einstandspartner >= 0:
        out = arbeitsl_geld_2_params["regelsatz"][2]
    # This observation is not a child, so BG has 1 adult
    elif arbeitsl_geld_2_kindersatz_m == 0.0:
        out = arbeitsl_geld_2_params["regelsatz"][1]
    else:
        out = 0.0

    return out * (1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m)


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
