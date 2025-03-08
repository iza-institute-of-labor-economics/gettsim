"""Basic needs following SGB II."""

from _gettsim.functions.policy_function import policy_function


@policy_function
def regelbedarf_m(
    regelsatz_m: float,
    kosten_unterkunft_m: float,
) -> float:
    """Basic monthly subsistence level on individual level.

    This includes cost of dwelling.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.:

    Parameters
    ----------
    regelsatz_m
        See :func:`regelsatz_m`.
    kosten_unterkunft_m
        See :func:`kosten_unterkunft_m`.

    Returns
    -------
    float checks the minimum monthly needs of an household.

    """
    return regelsatz_m + kosten_unterkunft_m


@policy_function
def mehrbedarf_alleinerziehend_m(
    demographics__alleinerziehend: bool,
    demographic_vars__anzahl_kinder_fg: int,
    demographic_vars__anzahl_kinder_bis_6_fg: int,
    demographic_vars__anzahl_kinder_bis_15_fg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Compute additional SGB II need for single parents.

    Additional need for single parents. Maximum 60% of the standard amount on top if
    you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    demographics__alleinerziehend
        See :func:`demographics__alleinerziehend`.
    demographic_vars__anzahl_kinder_fg
        See :func:`demographic_vars__anzahl_kinder_fg`.
    demographic_vars__anzahl_kinder_bis_6_fg
        See :func:`demographic_vars__anzahl_kinder_bis_6_fg`.
    demographic_vars__anzahl_kinder_bis_15_fg
        See :func:`demographic_vars__anzahl_kinder_bis_15_fg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.


    Returns
    -------
    float checks how much more a single parent need.

    """
    if demographics__alleinerziehend:
        # Clip value at calculated minimal share and given upper share
        # Note that upper limit is applied last (for many children lower
        # could be greater than upper)
        out = min(
            max(
                # Minimal Mehrbedarf share. Minimal rate times number of children
                arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"]
                * demographic_vars__anzahl_kinder_fg,
                # Increased rated if children up to 6 and/or 2-3 up to 15 are present.
                (
                    arbeitsl_geld_2_params["mehrbedarf_anteil"][
                        "kind_bis_6_oder_mehrere_bis_15"
                    ]
                    if (demographic_vars__anzahl_kinder_bis_6_fg >= 1)
                    or (2 <= demographic_vars__anzahl_kinder_bis_15_fg <= 3)
                    else 0.0
                ),
            ),
            arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"],
        )
    else:
        out = 0.0
    return out


@policy_function(end_date="2010-12-31", leaf_name="kindersatz_m")
def kindersatz_m_bis_2010(
    demographics__alter: int,
    kindergeld__gleiche_fg_wie_empfänger: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs of children until 2010.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter`.
    kindergeld__gleiche_fg_wie_empfänger
        See :func:`kindergeld__gleiche_fg_wie_empfänger`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with SGB II needs of children until year 2010.

    """
    anteile = arbeitsl_geld_2_params["anteil_regelsatz_kinder"]
    regelsatz = arbeitsl_geld_2_params["regelsatz"]

    if (
        demographics__alter >= anteile["kind_zwischen_14_und_24"]["min_alter"]
        and demographics__alter <= anteile["kind_zwischen_14_und_24"]["max_alter"]
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = regelsatz * anteile["kind_zwischen_14_und_24"]["anteil"]
    elif (
        demographics__alter >= anteile["kind_zwischen_6_und_13"]["min_alter"]
        and demographics__alter <= anteile["kind_zwischen_6_und_13"]["max_alter"]
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = regelsatz * anteile["kind_zwischen_6_und_13"]["anteil"]
    elif (
        demographics__alter >= anteile["kind_bis_5"]["min_alter"]
        and demographics__alter <= anteile["kind_bis_5"]["max_alter"]
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out = regelsatz * anteile["kind_bis_5"]["anteil"]
    else:
        out = 0.0

    return float(out)


@policy_function(start_date="2011-01-01", leaf_name="kindersatz_m")
def kindersatz_m_ab_2011(
    demographics__alter: int,
    kindergeld__gleiche_fg_wie_empfänger: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs of children since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter`.
    kindergeld__gleiche_fg_wie_empfänger
        See :func:`kindergeld__gleiche_fg_wie_empfänger`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    SGB II needs of child

    """

    out = arbeitsl_geld_2_params.get("kindersofortzuschl", 0.0)

    if (
        demographics__alter >= arbeitsl_geld_2_params["regelsatz"][6]["min_alter"]
        and demographics__alter <= arbeitsl_geld_2_params["regelsatz"][6]["max_alter"]
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out += arbeitsl_geld_2_params["regelsatz"][6]["betrag"]
    elif (
        demographics__alter >= arbeitsl_geld_2_params["regelsatz"][5]["min_alter"]
        and demographics__alter <= arbeitsl_geld_2_params["regelsatz"][5]["max_alter"]
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out += arbeitsl_geld_2_params["regelsatz"][5]["betrag"]
    elif (
        demographics__alter >= arbeitsl_geld_2_params["regelsatz"][4]["min_alter"]
        and demographics__alter <= arbeitsl_geld_2_params["regelsatz"][4]["max_alter"]
        and kindergeld__gleiche_fg_wie_empfänger
    ):
        out += arbeitsl_geld_2_params["regelsatz"][4]["betrag"]
    elif kindergeld__gleiche_fg_wie_empfänger:  # adult children with parents in FG
        out += arbeitsl_geld_2_params["regelsatz"][3]
    else:
        out = 0.0

    return float(out)


@policy_function(end_date="2010-12-31", leaf_name="erwachsenensatz_m")
def arbeitsl_geld_2_erwachsenensatz_bis_2010_m(
    mehrbedarf_alleinerziehend_m: float,
    kindersatz_m: float,
    demograpics__p_id_einstandspartner: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs for adults without dwelling.

    Parameters
    ----------
    mehrbedarf_alleinerziehend_m
        See :func:`mehrbedarf_alleinerziehend_m`.
    kindersatz_m
        See :func:`kindersatz_m`.
    demograpics__p_id_einstandspartner
        See basic input variable :ref:`demograpics__p_id_einstandspartner`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # BG has 2 adults
    if demograpics__p_id_einstandspartner >= 0:
        out = (
            arbeitsl_geld_2_params["regelsatz"]
            * (arbeitsl_geld_2_params["anteil_regelsatz_erwachsene"]["zwei_erwachsene"])
        )
    # This observation is not a child, so BG has 1 adult
    elif kindersatz_m == 0.0:
        out = arbeitsl_geld_2_params["regelsatz"]
    else:
        out = 0.0

    return out * (1 + mehrbedarf_alleinerziehend_m)


@policy_function(start_date="2011-01-01", leaf_name="erwachsenensatz_m")
def arbeitsl_geld_2_erwachsenensatz_ab_2011_m(
    mehrbedarf_alleinerziehend_m: float,
    kindersatz_m: float,
    demograpics__p_id_einstandspartner: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Basic monthly subsistence / SGB II needs for adults without dwelling since 2011.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    mehrbedarf_alleinerziehend_m
        See :func:`mehrbedarf_alleinerziehend_m`.
    kindersatz_m
        See :func:`kindersatz_m`.
    demograpics__p_id_einstandspartner
        See basic input variable :ref:`demograpics__p_id_einstandspartner`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    float with the minimum needs of an household in Euro.

    """
    # BG has 2 adults
    if demograpics__p_id_einstandspartner >= 0:
        out = arbeitsl_geld_2_params["regelsatz"][2]
    # This observation is not a child, so BG has 1 adult
    elif kindersatz_m == 0.0:
        out = arbeitsl_geld_2_params["regelsatz"][1]
    else:
        out = 0.0

    return out * (1 + mehrbedarf_alleinerziehend_m)


@policy_function
def regelsatz_m(
    erwachsenensatz_m: float,
    kindersatz_m: float,
) -> float:
    """Calculate basic monthly subsistence without dwelling until 2010.

    Parameters
    ----------
    erwachsenensatz_m
        See :func:`erwachsenensatz_m`.
    kindersatz_m
        See :func:`kindersatz_m`.

    Returns
    -------


    """
    return erwachsenensatz_m + kindersatz_m


@policy_function(end_date="2022-12-31", name_in_dag="kosten_unterkunft_m")
def kosten_unterkunft_m_bis_2022(
    berechtigte_wohnfläche: float,
    warmmiete_je_qm_m: float,
) -> float:
    """Calculate costs of living eligible to claim until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    Parameters
    ----------
    berechtigte_wohnfläche
        See :func:`berechtigte_wohnfläche`.
    warmmiete_je_qm_m
        See :func:`warmmiete_je_qm_m`.

    Returns
    -------
    float with total monthly cost of rent.

    """
    return berechtigte_wohnfläche * warmmiete_je_qm_m


@policy_function(start_date="2023-01-01", name_in_dag="kosten_unterkunft_m")
def kosten_unterkunft_m_ab_2023(
    bruttokaltmiete_m: float,
    heizkosten_m: float,
    in_vorjahr_bezogen: bool,
    berechtigte_wohnfläche: float,
    warmmiete_je_qm_m: float,
) -> float:
    """Calculate costs of living eligible to claim since 2023. During the first year,
    the waiting period (Karenzzeit), only the appropriateness of the heating costs is
    tested, while the living costs are fully considered in Bürgergeld.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttokaltmiete_m
        See :func:`bruttokaltmiete_m`.
    heizkosten_m
        See :func:`heizkosten_m`.
    in_vorjahr_bezogen
        See basic input variable :ref:`in_vorjahr_bezogen <in_vorjahr_bezogen>`.
    berechtigte_wohnfläche
        See :func:`berechtigte_wohnfläche`.
    warmmiete_je_qm_m
        See :func:`warmmiete_je_qm_m`.

    Returns
    -------
    float with total monthly cost of rent.

    """
    if in_vorjahr_bezogen:
        out = berechtigte_wohnfläche * warmmiete_je_qm_m
    else:
        out = bruttokaltmiete_m + heizkosten_m

    return out


@policy_function
def warmmiete_je_qm_m(
    bruttokaltmiete_m: float,
    heizkosten_m: float,
    wohnfläche: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate rent per square meter.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttokaltmiete_m
        See :func:`bruttokaltmiete_m`.
    heizkosten_m
        See :func:`heizkosten_m`.
    wohnfläche
        See function :func:`wohnfläche`.

    Returns
    -------
    Integer with the total amount of rental costs per squaremeter.

    """
    out = (bruttokaltmiete_m + heizkosten_m) / wohnfläche

    # Consider maximum considered rent per square meter
    out = min(out, arbeitsl_geld_2_params["max_miete_pro_qm"]["max"])

    return out


@policy_function
def berechtigte_wohnfläche(
    wohnfläche: float,
    wohnen__bewohnt_eigentum_hh: bool,
    demographic_vars__anzahl_personen_hh: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate size of dwelling eligible to claim.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    wohnfläche
        See function :func:`wohnfläche`.
    wohnen__bewohnt_eigentum_hh
        See basic input variable :ref:`wohnen__bewohnt_eigentum_hh <wohnen__bewohnt_eigentum_hh>`.
    demographic_vars__anzahl_personen_hh
        See :func:`demographic_vars__anzahl_personen_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    Integer with the number of squaremeters.

    """  # noqa: E501

    params = arbeitsl_geld_2_params["berechtigte_wohnfläche_eigentum"]
    max_anzahl_direkt = params["max_anzahl_direkt"]
    if wohnen__bewohnt_eigentum_hh:
        if demographic_vars__anzahl_personen_hh <= max_anzahl_direkt:
            maximum = params[demographic_vars__anzahl_personen_hh]
        else:
            maximum = (
                params[max_anzahl_direkt]
                + (demographic_vars__anzahl_personen_hh - max_anzahl_direkt)
                * params["je_weitere_person"]
            )
    else:
        maximum = (
            arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"]["single"]
            + max(demographic_vars__anzahl_personen_hh - 1, 0)
            * arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"][
                "je_weitere_person"
            ]
        )
    return min(wohnfläche, maximum / demographic_vars__anzahl_personen_hh)


@policy_function
def bruttokaltmiete_m(
    bruttokaltmiete_m_hh: float,
    demographic_vars__anzahl_personen_hh: int,
) -> float:
    """Monthly rent attributed to a single person.

    Reference:
    BSG Urteil v. 09.03.2016 - B 14 KG 1/15 R.
    BSG Urteil vom 15.04.2008 - B 14/7b AS 58/06 R.

    Parameters
    ----------
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    demographic_vars__anzahl_personen_hh
        See :func:`demographic_vars__anzahl_personen_hh`.

    Returns
    -------

    """
    return bruttokaltmiete_m_hh / demographic_vars__anzahl_personen_hh


@policy_function
def heizkosten_m(
    heizkosten_m_hh: float,
    demographic_vars__anzahl_personen_hh: int,
) -> float:
    """Monthly heating expenses attributed to a single person.

    Reference:
    BSG Urteil v. 09.03.2016 - B 14 KG 1/15 R.
    BSG Urteil vom 15.04.2008 - B 14/7b AS 58/06 R.

    Parameters
    ----------
    heizkosten_m_hh
        See basic input variable :ref:`heizkosten_m_hh <heizkosten_m_hh>`.
    demographic_vars__anzahl_personen_hh
        See :func:`demographic_vars__anzahl_personen_hh`.

    Returns
    -------

    """
    return heizkosten_m_hh / demographic_vars__anzahl_personen_hh


@policy_function
def wohnfläche(
    wohnen__wohnfläche_hh: float,
    demographic_vars__anzahl_personen_hh: int,
) -> float:
    """Share of household's dwelling size attributed to a single person.

    Parameters
    ----------
    wohnen__wohnfläche_hh
        See basic input variable :ref:`wohnen__wohnfläche_hh <wohnen__wohnfläche_hh>`.
    demographic_vars__anzahl_personen_hh
        See :func:`demographic_vars__anzahl_personen_hh`.

    Returns
    -------

    """
    return wohnen__wohnfläche_hh / demographic_vars__anzahl_personen_hh
