from _gettsim.config import numpy_or_jax as np


def _wohngeld_basisformel(
    anz_personen: int,
    einkommen_m: float,
    miete_m: float,
    params: dict,
):
    """Basic formula for housing benefit calculation.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    anz_personen
        Number of people Wohngeld is being calculated for.
    einkommen_m
        Sum of income of people Wohngeld should be calculated for.
    miete_m
        Sum of rent.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """
    max_berücks_personen = params["bonus_sehr_große_haushalte"][
        "max_anz_personen_normale_berechnung"
    ]

    koeffizienten = params["koeffizienten_berechnungsformel"][
        min(anz_personen, max_berücks_personen)
    ]
    out = params["faktor_berechnungsformel"] * (
        miete_m
        - (
            (
                koeffizienten["a"]
                + (koeffizienten["b"] * miete_m)
                + (koeffizienten["c"] * einkommen_m)
            )
            * einkommen_m
        )
    )
    out = max(out, 0.0)

    if anz_personen > max_berücks_personen:
        # If more than 12 persons, there is a lump-sum on top.
        # The maximum is still capped at `miete_m`.
        out = min(
            out
            + params["bonus_sehr_große_haushalte"]["bonus_jede_weitere_person"]
            * (anz_personen - max_berücks_personen),
            miete_m,
        )

    return out


def _wohngeld_nach_vermög_check_formel(
    basisbetrag_m: float,
    vermögen: float,
    anz_personen: int,
    params: dict,
) -> float:
    """Set preliminary housing benefit to zero if it exceeds the wealth exemption.

    The payment depends on the wealth of the household and the number of household
    members.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    basisbetrag_m
        Wohngeld as calculated via the basic formula (`_wohngeld_basisformel`).
    vermögen
        Relevant wealth of the Wohngeld recipients.
    anz_personen
        Number of people Wohngeld is being calculated for.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """

    if vermögen <= (
        params["vermögensgrundfreibetrag"]
        + (params["vermögensfreibetrag_pers"] * (anz_personen - 1))
    ):
        out = basisbetrag_m
    else:
        out = 0.0

    return out


def _wohngeld_max_miete_formel_ab_2009(  # noqa: PLR0912 (see #516)
    mietstufe: int,
    anz_personen: int,
    bruttokaltmiete_m: float,
    min_miete_m: float,
    params: dict,
) -> float:
    """Formula for maximum rent considered in housing benefit since 2009.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    mietstufe
        Mietstufe.
    anz_personen
        Number of people Wohngeld is being calculated for.
    bruttokaltmiete_m
        Sum of monthly rent.
    min_miete_m
        Minimum monthly rent.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """
    params_max_miete = params["max_miete"]

    max_berücks_personen = params["bonus_sehr_große_haushalte"][
        "max_anz_personen_normale_berechnung"
    ]
    berücks_personen = min(anz_personen, max_berücks_personen)

    # Calc maximal considered rent
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if anz_personen <= max_definierte_hh_größe:
        max_miete_m = params_max_miete[anz_personen][mietstufe]
    else:
        max_miete_m = (
            params_max_miete[max_definierte_hh_größe][mietstufe]
            + (berücks_personen - max_definierte_hh_größe)
            * params_max_miete["jede_weitere_person"][mietstufe]
        )

    # Calc heating allowance. Until 2020, heating allowance was not
    # introduced yet. For this time frame, the respective parameter is
    # not part of params and heating allowance is set to 0.
    # TODO(@MImmesberger): Apply dates_active decorator.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/711
    if "heizkostenentlastung_m" in params:
        max_def_hh_größe_heating = max(
            i for i in params["heizkostenentlastung_m"] if isinstance(i, int)
        )
    if "heizkostenentlastung_m" in params:
        if anz_personen <= max_def_hh_größe_heating:
            heating_allowance_m = params["heizkostenentlastung_m"][anz_personen]
        else:
            heating_allowance_m = params["heizkostenentlastung_m"][
                max_def_hh_größe_heating
            ] + (berücks_personen - max_def_hh_größe_heating) * (
                params["heizkostenentlastung_m"]["jede_weitere_person"]
            )
    else:
        heating_allowance_m = 0

    # Calc heating cost component. Until 2022, heating cost component was not
    # introduced yet. For this time frame, the respective parameter is not part
    # of params and heating cost component is set to 0.
    if "dauerhafte_heizkostenkomponente_m" in params:
        max_def_hh_größe_heating = max(
            i for i in params["dauerhafte_heizkostenkomponente_m"] if isinstance(i, int)
        )
    if "dauerhafte_heizkostenkomponente_m" in params:
        if anz_personen <= max_def_hh_größe_heating:
            heating_component_m = params["dauerhafte_heizkostenkomponente_m"][
                anz_personen
            ]
        else:
            heating_component_m = params["dauerhafte_heizkostenkomponente_m"][
                max_def_hh_größe_heating
            ] + (berücks_personen - max_def_hh_größe_heating) * (
                params["dauerhafte_heizkostenkomponente_m"]["jede_weitere_person"]
            )
    else:
        heating_component_m = 0

    # Calc climate component. Until 2022, climate component was not
    # introduced yet. For this time frame, the respective parameter is not
    # part of params and climate component is set to 0.
    if "klimakomponente_m" in params:
        max_def_hh_größe_heating = max(
            i for i in params["klimakomponente_m"] if isinstance(i, int)
        )
    if "klimakomponente_m" in params:
        if anz_personen <= max_def_hh_größe_heating:
            climate_component_m = params["klimakomponente_m"][anz_personen]
        else:
            climate_component_m = params["klimakomponente_m"][
                max_def_hh_größe_heating
            ] + (berücks_personen - max_def_hh_größe_heating) * (
                params["klimakomponente_m"]["jede_weitere_person"]
            )
    else:
        climate_component_m = 0

    out = min(bruttokaltmiete_m, max_miete_m + climate_component_m)
    out = max(out, min_miete_m) + heating_allowance_m + heating_component_m

    return out


def _wohngeld_max_miete_formel_bis_2009(  # noqa: PLR0913
    mietstufe: int,
    immobilie_baujahr: int,
    anz_personen: int,
    bruttokaltmiete_m: float,
    min_miete_m: float,
    params: dict,
) -> float:
    """Formula for maximum rent considered in housing benefit until 2008.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    mietstufe
        Mietstufe.
    immobilie_baujahr
        Year of construction of the property.
    anz_personen
        Number of people Wohngeld is being calculated for.
    bruttokaltmiete_m
        Sum of monthly rent.
    min_miete_m
        Minimum monthly rent.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """
    max_berücks_personen = params["bonus_sehr_große_haushalte"][
        "max_anz_personen_normale_berechnung"
    ]
    berücks_personen = min(anz_personen, max_berücks_personen)

    # Get yearly cutoff in params which is closest and above the construction year
    # of the property. We assume that the same cutoffs exist for each household
    # size.
    params_max_miete = params["max_miete"]
    selected_bin_index = np.searchsorted(
        sorted(params_max_miete[1]), immobilie_baujahr, side="left"
    )

    constr_year = list(params_max_miete[1])[selected_bin_index]

    # Calc maximal considered rent
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if anz_personen <= max_definierte_hh_größe:
        max_miete_m = params_max_miete[anz_personen][constr_year][mietstufe]
    else:
        max_miete_m = params_max_miete[max_definierte_hh_größe][constr_year][
            mietstufe
        ] + params_max_miete["jede_weitere_person"][constr_year][mietstufe] * (
            berücks_personen - max_definierte_hh_größe
        )

    out = min(bruttokaltmiete_m, max_miete_m)
    out = max(out, min_miete_m)

    return out


def _wohngeld_min_miete_formel(anz_personen: int, params: dict) -> float:
    """Formula for minimal rent considered in housing benefi.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    anz_personen
        Number of people Wohngeld is being calculated for.
    params
        See params documentation :ref:`params <params>`.
    Returns
    -------

    """
    out = params["min_miete"][min(anz_personen, max(params["min_miete"]))]
    return float(out)


def _wohngeld_einkommen_formula(
    anz_personen: int,
    einkommen_freibetrag: float,
    einkommen_vor_freibetrag: float,
    params: dict,
) -> float:
    """Calculate final income relevant for calculation of housing benefit on household
    level.
    Reference: § 13 WoGG

    Parameters
    ----------
    anz_personen
        Number of people Wohngeld is being calculated for.
    einkommen_freibetrag
        Income that is not considered for Wohngeld calculation.
    einkommen_vor_freibetrag
        Sum of income.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """
    eink_nach_abzug_m_hh = einkommen_vor_freibetrag - einkommen_freibetrag
    unteres_eink = params["min_eink"][min(anz_personen, max(params["min_eink"]))]

    out = max(eink_nach_abzug_m_hh, unteres_eink)
    return float(out)
