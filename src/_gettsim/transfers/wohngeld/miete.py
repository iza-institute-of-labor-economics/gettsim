"""Renting costs relevant for housing benefit calculation."""

from _gettsim.config import numpy_or_jax as np
from _gettsim.functions.policy_function import policy_function


def miete_m_wthh(
    miete_m_hh: float,
    anz_personen_wthh: int,
    anz_personen_hh: int,
) -> float:
    """Rent considered in housing benefit calculation on wohngeldrechtlicher
    Teilhaushalt level.

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften
    that passed the priority check against Arbeitslosengeld II / Bürgergeld.

    Parameters
    ----------
    miete_m_hh
        See :func:`miete_m_hh`.
    anz_personen_wthh
        See :func:`anz_personen_wthh`.
    anz_personen_hh
        See :func:`anz_personen_hh`.

    Returns
    -------

    """
    return miete_m_hh * (anz_personen_wthh / anz_personen_hh)


def miete_m_bg(
    miete_m_hh: float,
    anz_personen_bg: int,
    anz_personen_hh: int,
) -> float:
    """Rent considered in housing benefit calculation on BG level.

    This target is used for the priority check calculation against Arbeitslosengeld II /
    Bürgergeld on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    miete_m_hh
        See :func:`miete_m_hh`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    anz_personen_hh
        See :func:`anz_personen_hh`.

    Returns
    -------

    """
    return miete_m_hh * (anz_personen_bg / anz_personen_hh)


def min_miete_m_hh(anz_personen_hh: int, wohngeld_params: dict) -> float:
    """Minimum rent considered in Wohngeld calculation.

    Parameters
    ----------
    anz_personen_hh
        See :func:`anz_personen_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    out = wohngeld_params["min_miete"][
        min(anz_personen_hh, max(wohngeld_params["min_miete"]))
    ]
    return float(out)


@policy_function(end_date="2008-12-31", name_in_dag="miete_m_hh")
def miete_bis_2008_m_hh(  # noqa: PLR0913
    mietstufe: int,
    immobilie_baujahr_hh: int,
    anz_personen_hh: int,
    bruttokaltmiete_m_hh: float,
    min_miete_m_hh: float,
    wohngeld_params: dict,
) -> float:
    """Rent considered in housing benefit calculation on household level until 2008.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    immobilie_baujahr_hh
        See basic input variable :ref:`immobilie_baujahr_hh <immobilie_baujahr_hh>`.
    anz_personen_hh
        See :func:`anz_personen_hh`.
    bruttokaltmiete_m_hh
        See :func:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    min_miete_m_hh
        See :func:`min_miete_m_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    max_berücks_personen = wohngeld_params["bonus_sehr_große_haushalte"][
        "max_anz_personen_normale_berechnung"
    ]
    berücks_personen = min(anz_personen_hh, max_berücks_personen)

    # Get yearly cutoff in params which is closest and above the construction year
    # of the property. We assume that the same cutoffs exist for each household
    # size.
    params_max_miete = wohngeld_params["max_miete"]
    selected_bin_index = np.searchsorted(
        np.asarray(sorted(params_max_miete[1])), immobilie_baujahr_hh, side="left"
    )

    constr_year = list(params_max_miete[1])[selected_bin_index]

    # Calc maximal considered rent
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if anz_personen_hh <= max_definierte_hh_größe:
        max_miete_m = params_max_miete[anz_personen_hh][constr_year][mietstufe]
    else:
        max_miete_m = params_max_miete[max_definierte_hh_größe][constr_year][
            mietstufe
        ] + params_max_miete["jede_weitere_person"][constr_year][mietstufe] * (
            berücks_personen - max_definierte_hh_größe
        )

    out = min(bruttokaltmiete_m_hh, max_miete_m)
    out = max(out, min_miete_m_hh)

    return out


@policy_function(start_date="2009-01-01", name_in_dag="miete_m_hh")
def miete_ab_2009_m_hh(  # noqa: PLR0912 (see #516)
    mietstufe: int,
    anz_personen_hh: int,
    bruttokaltmiete_m_hh: float,
    min_miete_m_hh: float,
    wohngeld_params: dict,
) -> float:
    """Rent considered in housing benefit since 2009.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    anz_personen_hh
        See :func:`anz_personen_hh`.
    bruttokaltmiete_m_hh
        See :func:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    min_miete_m_hh
        See :func:`min_miete_m_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    params_max_miete = wohngeld_params["max_miete"]

    max_berücks_personen = wohngeld_params["bonus_sehr_große_haushalte"][
        "max_anz_personen_normale_berechnung"
    ]
    berücks_personen = min(anz_personen_hh, max_berücks_personen)

    # Calc maximal considered rent
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if anz_personen_hh <= max_definierte_hh_größe:
        max_miete_m = params_max_miete[anz_personen_hh][mietstufe]
    else:
        max_miete_m = (
            params_max_miete[max_definierte_hh_größe][mietstufe]
            + (berücks_personen - max_definierte_hh_größe)
            * params_max_miete["jede_weitere_person"][mietstufe]
        )

    # Calc heating allowance. Until 2020, heating allowance was not
    # introduced yet. For this time frame, the respective parameter is
    # not part of wohngeld_params and heating allowance is set to 0.
    # TODO(@MImmesberger): Apply policy_function decorator.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/711
    if "heizkostenentlastung_m" in wohngeld_params:
        max_def_hh_größe_heating = max(
            i for i in wohngeld_params["heizkostenentlastung_m"] if isinstance(i, int)
        )
    if "heizkostenentlastung_m" in wohngeld_params:
        if anz_personen_hh <= max_def_hh_größe_heating:
            heating_allowance_m = wohngeld_params["heizkostenentlastung_m"][
                anz_personen_hh
            ]
        else:
            heating_allowance_m = (
                wohngeld_params["heizkostenentlastung_m"][max_def_hh_größe_heating]
                + (berücks_personen - max_def_hh_größe_heating)
                * (wohngeld_params["heizkostenentlastung_m"]["jede_weitere_person"])
            )
    else:
        heating_allowance_m = 0

    # Calc heating cost component. Until 2022, heating cost component was not
    # introduced yet. For this time frame, the respective parameter is not part
    # of params and heating cost component is set to 0.
    if "dauerhafte_heizkostenkomponente_m" in wohngeld_params:
        max_def_hh_größe_heating = max(
            i
            for i in wohngeld_params["dauerhafte_heizkostenkomponente_m"]
            if isinstance(i, int)
        )
    if "dauerhafte_heizkostenkomponente_m" in wohngeld_params:
        if anz_personen_hh <= max_def_hh_größe_heating:
            heating_component_m = wohngeld_params["dauerhafte_heizkostenkomponente_m"][
                anz_personen_hh
            ]
        else:
            heating_component_m = (
                wohngeld_params["dauerhafte_heizkostenkomponente_m"][
                    max_def_hh_größe_heating
                ]
                + (berücks_personen - max_def_hh_größe_heating)
                * (
                    wohngeld_params["dauerhafte_heizkostenkomponente_m"][
                        "jede_weitere_person"
                    ]
                )
            )
    else:
        heating_component_m = 0

    # Calc climate component. Until 2022, climate component was not
    # introduced yet. For this time frame, the respective parameter is not
    # part of params and climate component is set to 0.
    if "klimakomponente_m" in wohngeld_params:
        max_def_hh_größe_heating = max(
            i for i in wohngeld_params["klimakomponente_m"] if isinstance(i, int)
        )
    if "klimakomponente_m" in wohngeld_params:
        if anz_personen_hh <= max_def_hh_größe_heating:
            climate_component_m = wohngeld_params["klimakomponente_m"][anz_personen_hh]
        else:
            climate_component_m = (
                wohngeld_params["klimakomponente_m"][max_def_hh_größe_heating]
                + (berücks_personen - max_def_hh_größe_heating)
                * (wohngeld_params["klimakomponente_m"]["jede_weitere_person"])
            )
    else:
        climate_component_m = 0

    out = min(bruttokaltmiete_m_hh, max_miete_m + climate_component_m)
    out = max(out, min_miete_m_hh) + heating_allowance_m + heating_component_m

    return out
