"""Housing benefits (Wohngeld).

Wohngeld has priority over ALG2 if the recipients can cover their needs according to
SGB II when receiving Wohngeld. The priority check follows the following logic:

1. Calculate Wohngeld on the Bedarfsgemeinschaft level.
2. Check whether the Bedarfsgemeinschaft can cover its own needs (Regelbedarf) with
   Wohngeld. If not, the Bedarfsgemeinschaft is eligible for ALG2.
3. Compute Wohngeld again for all individuals in the household that can cover their
   own needs with Wohngeld. This is the final Wohngeld amount that is paid out to
   the wohngeldrechtlicher Teilhaushalt.

Note: Because Wohngeld is nonlinear in the number of people in the
wohngeldrechtlicher Teilhaushalt, there may be some individuals that pass the
priority check, but cannot cover their needs with the Wohngeld calculated in point
3. In this sense, this implementation is an approximation of the actual Wohngeld.
"""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_m_wthh(
    anspruchshöhe_m_wthh: float,
    demographics__erwachsene_alle_rentner_hh: bool,
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrang_wthh: bool,
    vorrangprüfungen__wohngeld_vorrang_wthh: bool,
) -> float:
    """Housing benefit after wealth and priority checks.

    Parameters
    ----------
    anspruchshöhe_m_wthh
        See :func:`anspruchshöhe_m_wthh`.
    demographics__erwachsene_alle_rentner_hh
        See :func:`demographics__erwachsene_alle_rentner_hh <demographics__erwachsene_alle_rentner_hh>`.
    vorrangprüfungen__wohngeld_kinderzuschlag_vorrang_wthh
        See :func:`vorrangprüfungen__wohngeld_kinderzuschlag_vorrang_wthh`.
    vorrangprüfungen__wohngeld_vorrang_wthh
        See :func:`vorrangprüfungen__wohngeld_vorrang_wthh`.

    Returns
    -------

    """
    # TODO (@MImmesberger): This implementation may be only an approximation of the
    # actual rules for individuals that are on the margin of the priority check.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/752

    # TODO (@MImmesberger): No interaction between Wohngeld/ALG2 and Grundsicherung im
    # Alter (SGB XII) is implemented yet. We assume for now that households with only
    # retirees are eligible for Grundsicherung im Alter but not for ALG2/Wohngeld. All
    # other households are not eligible for SGB XII, but SGB II / Wohngeld. Once this is
    # resolved, remove the `demographics__erwachsene_alle_rentner_hh` condition.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/703

    if not demographics__erwachsene_alle_rentner_hh and (
        vorrangprüfungen__wohngeld_vorrang_wthh
        or vorrangprüfungen__wohngeld_kinderzuschlag_vorrang_wthh
    ):
        out = anspruchshöhe_m_wthh
    else:
        out = 0.0

    return out


@policy_function(params_key_for_rounding="wohngeld")
def anspruchshöhe_m_wthh(
    anzahl_personen_wthh: int,
    einkommen_m_wthh: float,
    miete_m_wthh: float,
    grundsätzlich_anspruchsberechtigt_wthh: bool,
    wohngeld_params: dict,
) -> float:
    """Housing benefit after wealth and income check.

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften in
    the household that passed the priority check against Arbeitslosengeld 2. Returns
    zero if not eligible.

    Parameters
    ----------
    anzahl_personen_wthh
        See :func:`anzahl_personen_wthh`.
    einkommen_m_wthh
        See :func:`einkommen_m_wthh`.
    miete_m_wthh
        See :func:`miete_m_wthh`.
    grundsätzlich_anspruchsberechtigt_wthh
        See :func:`grundsätzlich_anspruchsberechtigt_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    if grundsätzlich_anspruchsberechtigt_wthh:
        out = basisformel(
            anzahl_personen=anzahl_personen_wthh,
            einkommen_m=einkommen_m_wthh,
            miete_m=miete_m_wthh,
            params=wohngeld_params,
        )
    else:
        out = 0.0

    return out


@policy_function(params_key_for_rounding="wohngeld")
def anspruchshöhe_m_bg(
    arbeitslosengeld_2__anzahl_personen_bg: int,
    einkommen_m_bg: float,
    miete_m_bg: float,
    grundsätzlich_anspruchsberechtigt_bg: bool,
    wohngeld_params: dict,
) -> float:
    """Housing benefit after wealth and income check.

    This target is used for the priority check calculation against Arbeitslosengeld 2.

    Parameters
    ----------
    arbeitslosengeld_2__anzahl_personen_bg
        See :func:`arbeitslosengeld_2__anzahl_personen_bg`.
    einkommen_m_bg
        See :func:`einkommen_m_bg`.
    miete_m_bg
        See :func:`miete_m_bg`.
    grundsätzlich_anspruchsberechtigt_bg
        See :func:`grundsätzlich_anspruchsberechtigt_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    if grundsätzlich_anspruchsberechtigt_bg:
        out = basisformel(
            anzahl_personen=arbeitslosengeld_2__anzahl_personen_bg,
            einkommen_m=einkommen_m_bg,
            miete_m=miete_m_bg,
            params=wohngeld_params,
        )
    else:
        out = 0.0

    return out


def basisformel(
    anzahl_personen: int,
    einkommen_m: float,
    miete_m: float,
    params: dict,
) -> float:
    """Basic formula for housing benefit calculation.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    anzahl_personen
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
        min(anzahl_personen, max_berücks_personen)
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

    if anzahl_personen > max_berücks_personen:
        # If more than 12 persons, there is a lump-sum on top.
        # The maximum is still capped at `miete_m`.
        out = min(
            out
            + params["bonus_sehr_große_haushalte"]["bonus_jede_weitere_person"]
            * (anzahl_personen - max_berücks_personen),
            miete_m,
        )

    return out
