"""Parental leave benefits."""

from _gettsim.aggregation import AggregateByGroupSpec, AggregateByPIDSpec
from _gettsim.function_types import policy_function

aggregation_specs = {
    "kind_grundsätzlich_anspruchsberechtigt_fg": AggregateByGroupSpec(
        source_col="kind_grundsätzlich_anspruchsberechtigt",
        aggr="any",
    ),
    "anzahl_anträge_fg": AggregateByGroupSpec(
        source_col="claimed",
        aggr="sum",
    ),
    "bezugsmonate_partner": AggregateByPIDSpec(
        p_id_to_aggregate_by="arbeitslosengeld_2__p_id_einstandspartner",
        source_col="bisherige_bezugsmonate",
        aggr="sum",
    ),
    "alter_monate_jüngstes_mitglied_fg": AggregateByGroupSpec(
        source_col="demographics__alter_monate",
        aggr="min",
    ),
    "anzahl_kinder_bis_2_fg": AggregateByGroupSpec(
        source_col="demographics__kind_bis_2",
        aggr="sum",
    ),
    "anzahl_kinder_bis_5_fg": AggregateByGroupSpec(
        source_col="demographics__kind_bis_5",
        aggr="sum",
    ),
    "anzahl_mehrlinge_jüngstes_kind_fg": AggregateByGroupSpec(
        source_col="jüngstes_kind_oder_mehrling",
        aggr="sum",
    ),
}


@policy_function(start_date="2011-01-01", params_key_for_rounding="elterngeld")
def betrag_m(
    grundsätzlich_anspruchsberechtigt: bool,
    anspruchshöhe_m: float,
) -> float:
    """Parental leave benefit (Elterngeld) received by the parent.

    Parameters
    ----------
    grundsätzlich_anspruchsberechtigt
        See :func:`grundsätzlich_anspruchsberechtigt`.
    anspruchshöhe_m
        See :func:`anspruchshöhe_m`.

    Returns
    -------

    """
    if grundsätzlich_anspruchsberechtigt:
        out = anspruchshöhe_m
    else:
        out = 0.0
    return out


@policy_function(start_date="2007-01-01")
def basisbetrag_m(
    nettoeinkommen_vorjahr_m: float,
    lohnersatzanteil: float,
    anzurechnendes_nettoeinkommen_m: float,
    elterngeld_params: dict,
) -> float:
    """Base parental leave benefit without accounting for floor and ceiling.

    Basisbetrag is calculated on the parental level.

    Parameters
    ----------
    nettoeinkommen_vorjahr_m
        See basic input variable :ref:`nettoeinkommen_vorjahr_m
        <nettoeinkommen_vorjahr_m>`.
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
        nettoeinkommen_vorjahr_m,
        elterngeld_params["max_zu_berücksichtigendes_einkommen"],
    )
    return (
        berücksichtigtes_einkommen - anzurechnendes_nettoeinkommen_m
    ) * lohnersatzanteil


@policy_function(
    start_date="2007-01-01",
    end_date="2010-12-31",
    leaf_name="betrag_m",
    params_key_for_rounding="elterngeld",
)
def elterngeld_not_implemented() -> float:
    raise NotImplementedError("Elterngeld is not implemented prior to 2011.")


@policy_function(start_date="2007-01-01")
def anspruchshöhe_m(
    basisbetrag_m: float,
    geschwisterbonus_m: float,
    mehrlingsbonus_m: float,
    elterngeld_params: dict,
) -> float:
    """Elterngeld before checking eligibility.

    Anspruchshöhe is calculated on the parental level.

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


@policy_function(start_date="2007-01-01")
def grundsätzlich_anspruchsberechtigt(  # noqa: PLR0913
    claimed: bool,
    demographics__arbeitsstunden_w: float,
    kind_grundsätzlich_anspruchsberechtigt_fg: bool,
    einkommen_vorjahr_unter_bezugsgrenze: bool,
    bezugsmonate_unter_grenze_fg: bool,
    elterngeld_params: dict,
) -> bool:
    """Parent is eligible to receive Elterngeld.

    Parameters
    ----------
    claimed
        See basic input variable :ref:`claimed <claimed>`.
    demographics__arbeitsstunden_w
        See basic input variable :ref:`demographics__arbeitsstunden_w <demographics__arbeitsstunden_w>`.
    kind_grundsätzlich_anspruchsberechtigt_fg
        See :func:`kind_grundsätzlich_anspruchsberechtigt_fg`.
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
        claimed
        and demographics__arbeitsstunden_w <= elterngeld_params["max_arbeitsstunden_w"]
        and einkommen_vorjahr_unter_bezugsgrenze
        and kind_grundsätzlich_anspruchsberechtigt_fg
        and bezugsmonate_unter_grenze_fg
    )


@policy_function(start_date="2007-01-01")
def bezugsmonate_unter_grenze_fg(
    bisherige_bezugsmonate_fg: int,
    bezugsmonate_partner: int,
    demographics__alleinerziehend: bool,
    anzahl_anträge_fg: int,
    elterngeld_params: dict,
) -> bool:
    """Elterngeld claimed for less than the maximum number of months in the past by the
    parent.

    Parameters
    ----------
    bisherige_bezugsmonate_fg
        See :func:`bisherige_bezugsmonate_fg`.
    bezugsmonate_partner
        See function :func:`bezugsmonate_partner`.
    demographics__alleinerziehend
        See basic input variable :ref:`demographics__alleinerziehend<demographics__alleinerziehend>`.
    anzahl_anträge_fg
        See :func:`anzahl_anträge_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if demographics__alleinerziehend or bezugsmonate_partner >= 2:
        out = (
            bisherige_bezugsmonate_fg
            < elterngeld_params["max_monate_mit_partnermonate"]
        )
    elif anzahl_anträge_fg > 1:
        out = (
            bisherige_bezugsmonate_fg + 1
            < elterngeld_params["max_monate_mit_partnermonate"]
        )
    else:
        out = (
            bisherige_bezugsmonate_fg
            < elterngeld_params["max_monate_ohne_partnermonate"]
        )
    return out


@policy_function(start_date="2007-01-01")
def kind_grundsätzlich_anspruchsberechtigt(
    demographics__alter: int,
    elterngeld_params: dict,
) -> bool:
    """Child is young enough to give rise to Elterngeld claim.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return demographics__alter <= elterngeld_params["max_monate_mit_partnermonate"]


@policy_function(start_date="2011-01-01")
def lohnersatzanteil(
    nettoeinkommen_vorjahr_m: float,
    lohnersatzanteil_einkommen_untere_grenze: float,
    lohnersatzanteil_einkommen_obere_grenze: float,
    elterngeld_params: dict,
) -> float:
    """Replacement rate of Elterngeld (before applying floor and ceiling rules).

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until prozent_minimum.

    Parameters
    ----------
    nettoeinkommen_vorjahr_m
        See basic input variable
        :ref:`nettoeinkommen_vorjahr_m<nettoeinkommen_vorjahr_m>`.
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
        nettoeinkommen_vorjahr_m
        < elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
        and nettoeinkommen_vorjahr_m > 0
    ):
        out = elterngeld_params["faktor"] + (
            lohnersatzanteil_einkommen_untere_grenze
            / elterngeld_params["eink_schritt_korrektur"]
            * elterngeld_params["prozent_korrektur"]
        )
    # Lower replacement rate if considered income is above a threshold
    elif (
        nettoeinkommen_vorjahr_m
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


@policy_function(start_date="2007-01-01")
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


@policy_function()
def jüngstes_kind_oder_mehrling(
    demographics__alter_monate: float,
    alter_monate_jüngstes_mitglied_fg: float,
    demographics__kind: bool,
) -> bool:
    """Check if person is the youngest child in the household or a twin, triplet, etc.
    of the youngest child.

    # ToDo: replace kind by some age restriction
    # ToDo: Check definition as relevant for Elterngeld. Currently, it is calculated as
    # ToDo: age not being larger than 0.1 of a month

    Parameters
    ----------
    demographics__alter_monate
        See :func:`demographics__alter_monate`.
    alter_monate_jüngstes_mitglied_fg
        See :func:`alter_monate_jüngstes_mitglied_fg`.
    demographics__kind
        See basic input variable :ref:`demographics__kind <demographics__kind>`.

    Returns
    -------

    """
    out = (
        (demographics__alter_monate - alter_monate_jüngstes_mitglied_fg) < 0.1
    ) and demographics__kind
    return out
