"""Pension-relevant periods."""

from _gettsim.function_types import policy_function


@policy_function()
def mindestwartezeit_erfüllt(
    pflichtbeitragszeiten_y: float,
    freiwillige_beitragszeiten_y: float,
    ersatzzeiten_y: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Allgemeine Wartezeit has been completed. Aggregates time
    periods that are relevant for the general eligibility of the
    regular pension (regelaltersrente). "Allgemeine Wartezeit".

    Parameters
    ----------
    pflichtbeitragszeiten_y
        See :func:`pflichtbeitragszeiten_y`.
    freiwillige_beitragszeiten_y
        See :func:`freiwillige_beitragszeiten_y`.
    ersatzzeiten_y
        See :func:`ersatzzeiten_y`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 5 Jahren.

    """
    return (
        pflichtbeitragszeiten_y + freiwillige_beitragszeiten_y + ersatzzeiten_y
    ) >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_5"]


@policy_function()
def wartezeit_15_jahre_erfüllt(
    pflichtbeitragszeiten_y: float,
    freiwillige_beitragszeiten_y: float,
    ersatzzeiten_y: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 15 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the Altersrente für Frauen
    and Leistungen zur Teilhabe. Wartezeit von 15 Jahren.

    Parameters
    ----------
    pflichtbeitragszeiten_y
        See :func:`pflichtbeitragszeiten_y`.
    freiwillige_beitragszeiten_y
        See :func:`freiwillige_beitragszeiten_y`.
    ersatzzeiten_y
        See :func:`ersatzzeiten_y`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 15 Jahren

    """
    return (
        pflichtbeitragszeiten_y + freiwillige_beitragszeiten_y + ersatzzeiten_y
    ) >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_15"]


@policy_function()
def wartezeit_35_jahre_erfüllt(  # noqa: PLR0913
    pflichtbeitragszeiten_y: float,
    freiwillige_beitragszeiten_y: float,
    anrechnungszeit_35_y: float,
    ersatzzeiten_y: float,
    kinderberücksichtigungszeiten_y: float,
    pflegeberücksichtigungszeiten_y: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 35 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    langjährig Versicherte (pension for long-term insured). Wartezeit von 35 Jahren. All
    "rentenrechtliche Zeiten" are considered.

    Parameters
    ----------
    pflichtbeitragszeiten_y
        See :func:`pflichtbeitragszeiten_y`.
    freiwillige_beitragszeiten_y
        See :func:`freiwillige_beitragszeiten_y`.
    ersatzzeiten_y
        See :func:`ersatzzeiten_y`.
    anrechnungszeit_35_y
        See :func:`anrechnungszeit_35_y`.
    kinderberücksichtigungszeiten_y
        See :func:`kinderberücksichtigungszeiten_y`.
    pflegeberücksichtigungszeiten_y
        See :func:`pflegeberücksichtigungszeiten_y`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 35 Jahren

    """
    return (
        pflichtbeitragszeiten_y
        + freiwillige_beitragszeiten_y
        + anrechnungszeit_35_y
        + ersatzzeiten_y
        + kinderberücksichtigungszeiten_y
        + pflegeberücksichtigungszeiten_y
    ) >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_35"]


@policy_function(start_date="2012-01-01")
def wartezeit_45_jahre_erfüllt(  # noqa: PLR0913
    pflichtbeitragszeiten_y: float,
    freiwillige_beitragszeiten_y: float,
    anrechnungszeit_45_y: float,
    ersatzzeiten_y: float,
    kinderberücksichtigungszeiten_y: float,
    pflegeberücksichtigungszeiten_y: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 45 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    besonders langjährig Versicherte (pension for very long-term insured). Wartezeit von
    45 Jahren. Not all "rentenrechtliche Zeiten" are considered. Years with voluntary
    contributions are only considered if at least 18 years of mandatory contributions
    (pflichtbeitragszeiten_y). Not all anrechnungszeiten are considered, but only
    specific ones (e.g. ALG I, Kurzarbeit but not ALG II).

    Parameters
    ----------
    pflichtbeitragszeiten_y
        See basic input variable :ref:`pflichtbeitragszeiten_y <pflichtbeitragszeiten_y>`.
    freiwillige_beitragszeiten_y
        See basic input variable :ref:`freiwillige_beitragszeiten_y <freiwillige_beitragszeiten_y>`.
    anrechnungszeit_45_y
        See :func:`anrechnungszeit_45_y`.
    ersatzzeiten_y
        See basic input variable :ref:`ersatzzeiten_y <ersatzzeiten_y>`.
    kinderberücksichtigungszeiten_y
        See basic input variable :ref:`kinderberücksichtigungszeiten_y <kinderberücksichtigungszeiten_y>`.
    pflegeberücksichtigungszeiten_y
        See basic input variable :ref:`pflegeberücksichtigungszeiten_y <pflegeberücksichtigungszeiten_y>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 45 Jahren

    """
    if (
        pflichtbeitragszeiten_y
        >= ges_rente_params[
            "mindestpflichtbeitragsjahre_für_anrechnbarkeit_freiwilliger_beiträge"
        ]
    ):
        freiwilligbeitr = freiwillige_beitragszeiten_y
    else:
        freiwilligbeitr = 0

    return (
        pflichtbeitragszeiten_y
        + freiwilligbeitr
        + anrechnungszeit_45_y
        + ersatzzeiten_y
        + pflegeberücksichtigungszeiten_y
        + kinderberücksichtigungszeiten_y
    ) >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_45"]


@policy_function()
def anrechnungszeit_35_y(  # noqa: PLR0913
    arbeitsunfähigkeitszeiten_y: float,
    krankheitszeiten_ab_16_bis_24_y: float,
    mutterschutzzeiten_y: float,
    arbeitslosigkeitszeiten_y: float,
    ausbildungssuche_y: float,
    schulausbildung_y: float,
) -> float:
    """Adds up all times that are accounted for in "Anrechnungszeiten"
    relevant for "Wartezeit von 35 Jahren" i.e. for Altersrente für
    langjährig Versicherte (pension for long term insured).
    (Ref: Studientext der Deutschen Rentenversicherung, Nr. 19,
    Wartezeiten, Ausgabe 2021, S. 24.)


    Parameters
    ----------
    arbeitsunfähigkeitszeiten_y
        See :func:`arbeitsunfähigkeitszeiten_y`.
    krankheitszeiten_ab_16_bis_24_y
        See :func:`krankheitszeiten_ab_16_bis_24_y`.
    mutterschutzzeiten_y
        See :func:`mutterschutzzeiten_y`.
    arbeitslosigkeitszeiten_y
        See :func:`arbeitslosigkeitszeiten_y`.
    ausbildungssuche_y
        See :func:`ausbildungssuche_y`.
    schulausbildung_y
        See :func:`schulausbildung_y`.

    Returns
    -------
    Anrechnungszeit in months
    """
    return (
        arbeitsunfähigkeitszeiten_y
        + krankheitszeiten_ab_16_bis_24_y
        + mutterschutzzeiten_y
        + arbeitslosigkeitszeiten_y
        + ausbildungssuche_y
        + schulausbildung_y
    )


@policy_function(start_date="2012-01-01")
def anrechnungszeit_45_y(
    arbeitsunfähigkeitszeiten_y: float,
    entgeltersatzleistungen_arbeitslosigkeit_y: float,
    zeiten_geringfügiger_beschäftigung_y: float,
) -> float:
    """Adds up all times NOT included in Beitragszeiten, Berücksichtigungszeiten,
    Ersatzzeiten (a variant of Anrechnungszeiten) that are accounted for in "Wartezeit
    von 45 Jahren" i.e. for Altersrente für besonders langjährig Versicherte (pension
    for very long term insured). "nur Anrechnungszeiten mit Bezug von
    Entgeltersatzleistungen der Arbeitsförderung, Leistungen bei Krankheit und
    Übergangsgeld". (Ref: Studientext der Deutschen Rentenversicherung, Nr. 19,
    Wartezeiten, Ausgabe 2021, S. 24)

    Parameters
    ----------
    arbeitsunfähigkeitszeiten_y
        See :func:`arbeitsunfähigkeitszeiten_y`.
    entgeltersatzleistungen_arbeitslosigkeit_y
        See :func:`entgeltersatzleistungen_arbeitslosigkeit_y`.
    zeiten_geringfügiger_beschäftigung_y
        See :func:`zeiten_geringfügiger_beschäftigung_y`.
    Returns
    -------
    Anrechnungszeit in months.

    """
    return (
        arbeitsunfähigkeitszeiten_y
        + entgeltersatzleistungen_arbeitslosigkeit_y
        + zeiten_geringfügiger_beschäftigung_y
    )
