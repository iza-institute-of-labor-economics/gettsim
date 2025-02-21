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

from _gettsim.shared import policy_info


def wohngeld_m_wthh(
    wohngeld_anspruchshöhe_m_wthh: float,
    erwachsene_alle_rentner_hh: bool,
    wohngeld_kinderzuschl_vorrang_wthh: bool,
    wohngeld_vorrang_wthh: bool,
) -> float:
    """Housing benefit after wealth and priority checks.

    Parameters
    ----------
    wohngeld_anspruchshöhe_m_wthh
        See :func:`wohngeld_anspruchshöhe_m_wthh`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh <erwachsene_alle_rentner_hh>`.
    wohngeld_kinderzuschl_vorrang_wthh
        See :func:`wohngeld_kinderzuschl_vorrang_wthh`.
    wohngeld_vorrang_wthh
        See :func:`wohngeld_vorrang_wthh`.

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
    # resolved, remove the `erwachsene_alle_rentner_hh` condition.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/703

    if not erwachsene_alle_rentner_hh and (
        wohngeld_vorrang_wthh or wohngeld_kinderzuschl_vorrang_wthh
    ):
        out = wohngeld_anspruchshöhe_m_wthh
    else:
        out = 0.0

    return out


@policy_info(params_key_for_rounding="wohngeld")
def wohngeld_anspruchshöhe_m_wthh(
    anz_personen_wthh: int,
    wohngeld_eink_m_wthh: float,
    wohngeld_miete_m_wthh: float,
    wohngeld_anspruchsbedingungen_erfüllt_wthh: bool,
    wohngeld_params: dict,
) -> float:
    """Housing benefit after wealth and income check.

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften in
    the household that passed the priority check against Arbeitslosengeld 2. Returns
    zero if not eligible.

    Parameters
    ----------
    anz_personen_wthh
        See :func:`anz_personen_wthh`.
    wohngeld_eink_m_wthh
        See :func:`wohngeld_eink_m_wthh`.
    wohngeld_miete_m_wthh
        See :func:`wohngeld_miete_m_wthh`.
    wohngeld_anspruchsbedingungen_erfüllt_wthh
        See :func:`wohngeld_anspruchsbedingungen_erfüllt_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    if wohngeld_anspruchsbedingungen_erfüllt_wthh:
        out = _wohngeld_basisformel(
            anz_personen=anz_personen_wthh,
            einkommen_m=wohngeld_eink_m_wthh,
            miete_m=wohngeld_miete_m_wthh,
            params=wohngeld_params,
        )
    else:
        out = 0.0

    return out


@policy_info(params_key_for_rounding="wohngeld")
def wohngeld_anspruchshöhe_m_bg(
    anz_personen_bg: int,
    wohngeld_eink_m_bg: float,
    wohngeld_miete_m_bg: float,
    wohngeld_anspruchsbedingungen_erfüllt_bg: bool,
    wohngeld_params: dict,
) -> float:
    """Housing benefit after wealth and income check.

    This target is used for the priority check calculation against Arbeitslosengeld 2.

    Parameters
    ----------
    anz_personen_bg
        See :func:`anz_personen_bg`.
    wohngeld_eink_m_bg
        See :func:`wohngeld_eink_m_bg`.
    wohngeld_miete_m_bg
        See :func:`wohngeld_miete_m_bg`.
    wohngeld_anspruchsbedingungen_erfüllt_bg
        See :func:`wohngeld_anspruchsbedingungen_erfüllt_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    if wohngeld_anspruchsbedingungen_erfüllt_bg:
        out = _wohngeld_basisformel(
            anz_personen=anz_personen_bg,
            einkommen_m=wohngeld_eink_m_bg,
            miete_m=wohngeld_miete_m_bg,
            params=wohngeld_params,
        )
    else:
        out = 0.0

    return out


def _wohngeld_basisformel(
    anz_personen: int,
    einkommen_m: float,
    miete_m: float,
    params: dict,
) -> float:
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
