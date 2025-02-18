"""Parental leave benefits."""

from _gettsim.functions.policy_function import policy_function

aggregate_by_group_elterngeld = {
    "kind_anspruchsberechtigt_fg": {
        "source_col": "kind_anspruchsberechtigt",
        "aggr": "any",
    },
    "elterngeld_anzahl_claims_fg": {
        "source_col": "elterngeld_claimed",
        "aggr": "sum",
    },
}
aggregate_by_p_id_elterngeld = {
    "monate_elterngeld_partner": {
        "p_id_to_aggregate_by": "p_id_einstandspartner",
        "source_col": "monate_elterngeldbezug",
        "aggr": "sum",
    },
}


@policy_function(start_date="2011-01-01", params_key_for_rounding="elterngeld")
def elterngeld_m(
    elterngeld_anspruchsbedingungen_erfüllt: bool,
    elterngeld_anspruchshöhe_m: float,
) -> float:
    """Parental leave benefit (Elterngeld).

    Parameters
    ----------
    elterngeld_anspruchsbedingungen_erfüllt
        See :func:`elterngeld_anspruchsbedingungen_erfüllt`.
    elterngeld_anspruchshöhe_m
        See :func:`elterngeld_anspruchshöhe_m`.

    Returns
    -------

    """
    if elterngeld_anspruchsbedingungen_erfüllt:
        out = elterngeld_anspruchshöhe_m
    else:
        out = 0.0
    return out


def elterngeld_basisbetrag_m(
    elterngeld_nettoeinkommen_vorjahr_m: float,
    elterngeld_lohnersatzanteil: float,
    elterngeld_anrechenbares_nettoeinkommen_m: float,
    elterngeld_params: dict,
) -> float:
    """Base parental leave benefit without accounting for floor and ceiling.

    Parameters
    ----------
    elterngeld_nettoeinkommen_vorjahr_m
        See basic input variable :ref:`elterngeld_nettoeinkommen_vorjahr_m
        <elterngeld_nettoeinkommen_vorjahr_m>`.
    elterngeld_lohnersatzanteil
        See :func:`elterngeld_lohnersatzanteil`.
    elterngeld_anrechenbares_nettoeinkommen_m
        See :func:`elterngeld_anrechenbares_nettoeinkommen_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    berücksichtigtes_einkommen = min(
        elterngeld_nettoeinkommen_vorjahr_m,
        elterngeld_params["max_zu_berücksichtigendes_einkommen"],
    )
    return (
        berücksichtigtes_einkommen - elterngeld_anrechenbares_nettoeinkommen_m
    ) * elterngeld_lohnersatzanteil


@policy_info(
    end_date="2010-12-31",
    leaf_name="elterngeld_m",
    params_key_for_rounding="elterngeld",
)
def eltergeld_not_implemented() -> float:
    raise NotImplementedError("Elterngeld is not implemented prior to 2011.")


def elterngeld_anspruchshöhe_m(
    elterngeld_basisbetrag_m: float,
    elterngeld_geschwisterbonus_m: float,
    elterngeld_mehrlingsbonus_m: float,
    elterngeld_params: dict,
) -> float:
    """Elterngeld before checking eligibility.

    Parameters
    ----------
    elterngeld_basisbetrag_m
        See :func:`elterngeld_basisbetrag_m`.
    elterngeld_geschwisterbonus_m
        See :func:`elterngeld_geschwisterbonus_m`.
    elterngeld_mehrlingsbonus_m
        See :func:`elterngeld_mehrlingsbonus_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        min(
            max(
                elterngeld_basisbetrag_m,
                elterngeld_params["mindestbetrag"],
            ),
            elterngeld_params["höchstbetrag"],
        )
        + elterngeld_geschwisterbonus_m
        + elterngeld_mehrlingsbonus_m
    )


def elterngeld_anspruchsbedingungen_erfüllt(  # noqa: PLR0913
    elterngeld_claimed: bool,
    arbeitsstunden_w: float,
    kind_anspruchsberechtigt_fg: bool,
    vorjahr_einkommen_unter_bezugsgrenze: bool,
    monate_elterngeldbezug_unter_grenze_fg: bool,
    elterngeld_params: dict,
) -> bool:
    """Individual is eligible to receive Elterngeld.

    Parameters
    ----------
    elterngeld_claimed
        See basic input variable :ref:`elterngeld_claimed <elterngeld_claimed>`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    kind_anspruchsberechtigt_fg
        See :func:`kind_anspruchsberechtigt_fg`.
    vorjahr_einkommen_unter_bezugsgrenze
        See :func:`vorjahr_einkommen_unter_bezugsgrenze`.
    monate_elterngeldbezug_unter_grenze_fg
        See :func:`monate_elterngeldbezug_unter_grenze_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        elterngeld_claimed
        and arbeitsstunden_w <= elterngeld_params["max_arbeitsstunden_w"]
        and vorjahr_einkommen_unter_bezugsgrenze
        and kind_anspruchsberechtigt_fg
        and monate_elterngeldbezug_unter_grenze_fg
    )


def monate_elterngeldbezug_unter_grenze_fg(
    monate_elterngeldbezug_fg: int,
    monate_elterngeld_partner: int,
    alleinerz: bool,
    elterngeld_anzahl_claims_fg: int,
    elterngeld_params: dict,
) -> bool:
    """Elterngeld has been claimed for less than the maximum number of months in the
    past.

    Parameters
    ----------
    monate_elterngeldbezug_fg
        See :func:`monate_elterngeldbezug_fg`.
    monate_elterngeld_partner
        See function :func:`monate_elterngeld_partner`.
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    elterngeld_anzahl_claims_fg
        See :func:`elterngeld_anzahl_claims_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if alleinerz or monate_elterngeld_partner >= 2:
        out = (
            monate_elterngeldbezug_fg
            < elterngeld_params["max_monate_mit_partnermonate"]
        )
    elif elterngeld_anzahl_claims_fg > 1:
        out = (
            monate_elterngeldbezug_fg + 1
            < elterngeld_params["max_monate_mit_partnermonate"]
        )
    else:
        out = (
            monate_elterngeldbezug_fg
            < elterngeld_params["max_monate_ohne_partnermonate"]
        )
    return out


def kind_anspruchsberechtigt(
    alter: int,
    elterngeld_params: dict,
) -> bool:
    """Child is young enough to give rise to Elterngeld claim.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return alter <= elterngeld_params["max_monate_mit_partnermonate"]


@policy_info(start_date="2011-01-01")
def elterngeld_lohnersatzanteil(
    elterngeld_nettoeinkommen_vorjahr_m: float,
    _untere_lohnersatzanteil_grenze_minus_nettoeinkommen: float,
    _nettoeinkommen_minus_obere_lohnersatzanteil_grenze: float,
    elterngeld_params: dict,
) -> float:
    """Replacement rate of Elterngeld (before applying floor and ceiling rules).

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until prozent_minimum.

    Parameters
    ----------
    elterngeld_nettoeinkommen_vorjahr_m
        See basic input variable
        :ref:`elterngeld_nettoeinkommen_vorjahr_m<elterngeld_nettoeinkommen_vorjahr_m>`.
    _untere_lohnersatzanteil_grenze_minus_nettoeinkommen
        See :func:`_untere_lohnersatzanteil_grenze_minus_nettoeinkommen`.
    _nettoeinkommen_minus_obere_lohnersatzanteil_grenze
        See :func:`_nettoeinkommen_minus_obere_lohnersatzanteil_grenze`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """

    # Higher replacement rate if considered income is below a threshold
    if (
        elterngeld_nettoeinkommen_vorjahr_m
        < elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
        and elterngeld_nettoeinkommen_vorjahr_m > 0
    ):
        out = elterngeld_params["faktor"] + (
            _untere_lohnersatzanteil_grenze_minus_nettoeinkommen
            / elterngeld_params["eink_schritt_korrektur"]
            * elterngeld_params["prozent_korrektur"]
        )
    # Lower replacement rate if considered income is above a threshold
    elif (
        elterngeld_nettoeinkommen_vorjahr_m
        > elterngeld_params["nettoeinkommen_stufen"]["upper_threshold"]
    ):
        # Replacement rate is only lowered up to a specific value
        out = max(
            elterngeld_params["faktor"]
            - (
                _nettoeinkommen_minus_obere_lohnersatzanteil_grenze
                / elterngeld_params["eink_schritt_korrektur"]
                * elterngeld_params["prozent_korrektur"]
            ),
            elterngeld_params["prozent_minimum"],
        )
    else:
        out = elterngeld_params["faktor"]

    return out


def anrechenbares_elterngeld_m(
    elterngeld_m: float,
    _elterngeld_anz_mehrlinge_fg: int,
    elterngeld_params: dict,
) -> float:
    """Elterngeld that can be considered as income for other transfers.

    Relevant for Wohngeld and Grundsicherung im Alter.

    For Arbeitslosengeld II / Bürgergeld as well as Kinderzuschlag the whole amount of
    Elterngeld is considered as income, except for the case in which the parents still
    worked right before they had children. See:
    https://www.kindergeld.org/elterngeld-einkommen/

    Parameters
    ----------
    elterngeld_m
        See :func:`elterngeld_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    _elterngeld_anz_mehrlinge_fg
        See :func:`_elterngeld_anz_mehrlinge_fg`.

    Returns
    -------

    """
    out = max(
        elterngeld_m
        - ((1 + _elterngeld_anz_mehrlinge_fg) * elterngeld_params["mindestbetrag"]),
        0,
    )
    return out
