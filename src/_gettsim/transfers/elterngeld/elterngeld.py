"""Parental leave benefits."""

from _gettsim.aggregation import AggregateByGroupSpec, AggregateByPIDSpec
from _gettsim.functions.policy_function import policy_function

aggregation_specs = {
    "kind_anspruchsberechtigt_fg": AggregateByGroupSpec(
        source_col="kind_anspruchsberechtigt",
        aggr="any",
    ),
    "anzahl_anträge_fg": AggregateByGroupSpec(
        source_col="elterngeld_claimed",
        aggr="sum",
    ),
    "bezugsmonate": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_einstandspartner",
        source_col="monate_elterngeldbezug",
        aggr="sum",
    ),
}


@policy_function(start_date="2011-01-01", params_key_for_rounding="elterngeld")
def betrag_m(
    anspruchsberechtigt: bool,
    anspruchshöhe_m: float,
) -> float:
    """Parental leave benefit (Elterngeld).

    Parameters
    ----------
    anspruchsberechtigt
        See :func:`anspruchsberechtigt`.
    anspruchshöhe_m
        See :func:`anspruchshöhe_m`.

    Returns
    -------

    """
    if anspruchsberechtigt:
        out = anspruchshöhe_m
    else:
        out = 0.0
    return out


@policy_function
def basisbetrag_m(
    elterngeld_nettoeinkommen_vorjahr_m: float,
    lohnersatzanteil: float,
    anzurechnendes_nettoeinkommen_m: float,
    elterngeld_params: dict,
) -> float:
    """Base parental leave benefit without accounting for floor and ceiling.

    Parameters
    ----------
    elterngeld_nettoeinkommen_vorjahr_m
        See basic input variable :ref:`elterngeld_nettoeinkommen_vorjahr_m
        <elterngeld_nettoeinkommen_vorjahr_m>`.
    lohnersatzanteil
        See :func:`lohnersatzanteil`.
    anzurechnendes_nettoeinkommen_m
        See :func:`anzurechnendes_nettoeinkommen_m`.
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
        berücksichtigtes_einkommen - anzurechnendes_nettoeinkommen_m
    ) * lohnersatzanteil


@policy_function(
    end_date="2010-12-31",
    leaf_name="betrag_m",
    params_key_for_rounding="elterngeld",
)
def eltergeld_not_implemented() -> float:
    raise NotImplementedError("Elterngeld is not implemented prior to 2011.")


@policy_function
def anspruchshöhe_m(
    basisbetrag_m: float,
    geschwisterbonus_m: float,
    mehrlingsbonus_m: float,
    elterngeld_params: dict,
) -> float:
    """Elterngeld before checking eligibility.

    Parameters
    ----------
    basisbetrag_m
        See :func:`basisbetrag_m`.
    geschwisterbonus_m
        See :func:`geschwisterbonus_m`.
    mehrlingsbonus_m
        See :func:`mehrlingsbonus_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        min(
            max(
                basisbetrag_m,
                elterngeld_params["mindestbetrag"],
            ),
            elterngeld_params["höchstbetrag"],
        )
        + geschwisterbonus_m
        + mehrlingsbonus_m
    )


@policy_function
def anspruchsberechtigt(  # noqa: PLR0913
    elterngeld_claimed: bool,
    arbeitsstunden_w: float,
    kind_anspruchsberechtigt_fg: bool,
    einkommen_vorjahr_unter_bezugsgrenze: bool,
    bezugsmonate_unter_grenze_fg: bool,
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
    einkommen_vorjahr_unter_bezugsgrenze
        See :func:`einkommen_vorjahr_unter_bezugsgrenze`.
    bezugsmonate_unter_grenze_fg
        See :func:`bezugsmonate_unter_grenze_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        elterngeld_claimed
        and arbeitsstunden_w <= elterngeld_params["max_arbeitsstunden_w"]
        and einkommen_vorjahr_unter_bezugsgrenze
        and kind_anspruchsberechtigt_fg
        and bezugsmonate_unter_grenze_fg
    )


@policy_function
def bezugsmonate_unter_grenze_fg(
    monate_elterngeldbezug_fg: int,
    bezugsmonate: int,
    alleinerz: bool,
    anzahl_anträge_fg: int,
    elterngeld_params: dict,
) -> bool:
    """Elterngeld has been claimed for less than the maximum number of months in the
    past.

    Parameters
    ----------
    monate_elterngeldbezug_fg
        See :func:`monate_elterngeldbezug_fg`.
    bezugsmonate
        See function :func:`bezugsmonate`.
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    anzahl_anträge_fg
        See :func:`anzahl_anträge_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if alleinerz or bezugsmonate >= 2:
        out = (
            monate_elterngeldbezug_fg
            < elterngeld_params["max_monate_mit_partnermonate"]
        )
    elif anzahl_anträge_fg > 1:
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


@policy_function
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


@policy_function(start_date="2011-01-01")
def lohnersatzanteil(
    elterngeld_nettoeinkommen_vorjahr_m: float,
    lohnersatzanteil_einkommen_untere_grenze: float,
    lohnersatzanteil_einkommen_obere_grenze: float,
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
    lohnersatzanteil_einkommen_untere_grenze
        See :func:`lohnersatzanteil_einkommen_untere_grenze`.
    lohnersatzanteil_einkommen_obere_grenze
        See :func:`lohnersatzanteil_einkommen_obere_grenze`.
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
            lohnersatzanteil_einkommen_untere_grenze
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
                lohnersatzanteil_einkommen_obere_grenze
                / elterngeld_params["eink_schritt_korrektur"]
                * elterngeld_params["prozent_korrektur"]
            ),
            elterngeld_params["prozent_minimum"],
        )
    else:
        out = elterngeld_params["faktor"]

    return out


@policy_function
def anrechenbarer_betrag_m(
    betrag_m: float,
    anzahl_mehrlinge_fg: int,
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
    betrag_m
        See :func:`betrag_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    anzahl_mehrlinge_fg
        See :func:`anzahl_mehrlinge_fg`.

    Returns
    -------

    """
    out = max(
        betrag_m - ((1 + anzahl_mehrlinge_fg) * elterngeld_params["mindestbetrag"]),
        0,
    )
    return out
