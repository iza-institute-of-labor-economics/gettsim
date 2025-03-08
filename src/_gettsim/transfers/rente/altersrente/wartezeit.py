"""Pension-relevant periods."""

from _gettsim.functions.policy_function import policy_function


@policy_function
def mindestwartezeit_erfüllt(
    pflichtbeitragszeiten_m: float,
    freiwillige_beitragszeiten_m: float,
    ersatzzeiten_m: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Allgemeine Wartezeit has been completed. Aggregates time
    periods that are relevant for the general eligibility of the
    regular pension (regelaltersrente). "Allgemeine Wartezeit".

    Parameters
    ----------
    pflichtbeitragszeiten_m
        See basic input variable :ref:`pflichtbeitragszeiten_m <pflichtbeitragszeiten_m>`.
    freiwillige_beitragszeiten_m
        See basic input variable :ref:`freiwillige_beitragszeiten_m <freiwillige_beitragszeiten_m>`.
    ersatzzeiten_m
        See basic input variable :ref:`ersatzzeiten_m <ersatzzeiten_m>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 5 Jahren.

    """
    m_zeiten = (
        pflichtbeitragszeiten_m + freiwillige_beitragszeiten_m + ersatzzeiten_m
    ) / 12

    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_5"]

    return out


@policy_function
def wartezeit_15_jahre_erfüllt(
    pflichtbeitragszeiten_m: float,
    freiwillige_beitragszeiten_m: float,
    ersatzzeiten_m: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 15 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the Altersrente für Frauen
    and Leistungen zur Teilhabe. Wartezeit von 15 Jahren.

    Parameters
    ----------
    pflichtbeitragszeiten_m
        See basic input variable :ref:`pflichtbeitragszeiten_m <pflichtbeitragszeiten_m>`.
    freiwillige_beitragszeiten_m
        See basic input variable :ref:`freiwillige_beitragszeiten_m <freiwillige_beitragszeiten_m>`.
    ersatzzeiten_m
        See basic input variable :ref:`ersatzzeiten_m <ersatzzeiten_m>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 15 Jahren

    """
    m_zeiten = (
        pflichtbeitragszeiten_m + freiwillige_beitragszeiten_m + ersatzzeiten_m
    ) / 12

    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_15"]

    return out


@policy_function
def wartezeit_35_jahre_erfüllt(  # noqa: PLR0913
    pflichtbeitragszeiten_m: float,
    freiwillige_beitragszeiten_m: float,
    anrechnungszeit: float,
    ersatzzeiten_m: float,
    kinderberücksichtigungszeiten_m: float,
    pflegeberücksichtigungszeiten_m: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 35 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    langjährig Versicherte (pension for long-term insured). Wartezeit von 35 Jahren. All
    "rentenrechtliche Zeiten" are considered.

    Parameters
    ----------
    pflichtbeitragszeiten_m
        See basic input variable :ref:`pflichtbeitragszeiten_m <pflichtbeitragszeiten_m>`.
    freiwillige_beitragszeiten_m
        See basic input variable :ref:`freiwillige_beitragszeiten_m <freiwillige_beitragszeiten_m>`.
    ersatzzeiten_m
        See basic input variable :ref:`ersatzzeiten_m <ersatzzeiten_m>`.
    anrechnungszeit
        See :func:`anrechnungszeit`
    kinderberücksichtigungszeiten_m
        See basic input variable :ref:`kinderberücksichtigungszeiten_m <kinderberücksichtigungszeiten_m>`.
    pflegeberücksichtigungszeiten_m
        See basic input variable :ref:`pflegeberücksichtigungszeiten_m <pflegeberücksichtigungszeiten_m>`
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 35 Jahren

    """
    m_zeiten = (
        pflichtbeitragszeiten_m
        + freiwillige_beitragszeiten_m
        + anrechnungszeit
        + ersatzzeiten_m
        + pflegeberücksichtigungszeiten_m
        + kinderberücksichtigungszeiten_m
    ) / 12
    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_35"]

    return out


@policy_function(start_date="2012-01-01")
def wartezeit_45_jahre_erfüllt(  # noqa: PLR0913
    pflichtbeitragszeiten_m: float,
    freiwillige_beitragszeiten_m: float,
    anrechnungszeit_45: float,
    ersatzzeiten_m: float,
    kinderberücksichtigungszeiten_m: float,
    pflegeberücksichtigungszeiten_m: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 45 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    besonders langjährig Versicherte (pension for very long-term insured). Wartezeit von
    45 Jahren. Not all "rentenrechtliche Zeiten" are considered. Years with voluntary
    contributions are only considered if at least 18 years of mandatory contributions
    (pflichtbeitragszeiten_m). Not all anrechnungszeiten are considered, but only
    specific ones (e.g. ALG I, Kurzarbeit but not ALG II).

    Parameters
    ----------
    pflichtbeitragszeiten_m
        See basic input variable :ref:`pflichtbeitragszeiten_m <pflichtbeitragszeiten_m>`.
    freiwillige_beitragszeiten_m
        See basic input variable :ref:`freiwillige_beitragszeiten_m <freiwillige_beitragszeiten_m>`.
    anrechnungszeit_45
        See :func:`anrechnungszeit_45`.
    ersatzzeiten_m
        See basic input variable :ref:`ersatzzeiten_m <ersatzzeiten_m>`.
    kinderberücksichtigungszeiten_m
        See basic input variable :ref:`kinderberücksichtigungszeiten_m <kinderberücksichtigungszeiten_m>`.
    pflegeberücksichtigungszeiten_m
        See basic input variable :ref:`pflegeberücksichtigungszeiten_m <pflegeberücksichtigungszeiten_m>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 45 Jahren

    """
    if (
        pflichtbeitragszeiten_m
        >= ges_rente_params["wartezeit_45_pflichtbeitragsmonate"]
    ):
        freiwilligbeitr = freiwillige_beitragszeiten_m
    else:
        freiwilligbeitr = 0

    m_zeiten = (
        pflichtbeitragszeiten_m
        + freiwilligbeitr
        + anrechnungszeit_45
        + ersatzzeiten_m
        + pflegeberücksichtigungszeiten_m
        + kinderberücksichtigungszeiten_m
    ) / 12
    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_45"]

    return out


@policy_function
def anrechnungszeit(  # noqa: PLR0913
    arbeitsunfähigkeitszeiten_m: float,
    krankheitszeiten_ab_16_bis_24_m: float,
    mutterschutzzeiten_m: float,
    arbeitslosigkeitszeiten_m: float,
    ausbildungssuche_m: float,
    schulausbildung_m: float,
) -> float:
    """Adds up all times that are accounted for in "Anrechnungszeiten"
    relevant for "Wartezeit von 35 Jahren" i.e. for Altersrente für
    langjährig Versicherte (pension for long term insured).
    (Ref: Studientext der Deutschen Rentenversicherung, Nr. 19,
    Wartezeiten, Ausgabe 2021, S. 24.)


    Parameters
    ----------
    arbeitsunfähigkeitszeiten_m
        See basic input variable :ref:`arbeitsunfähigkeitszeiten_m <arbeitsunfähigkeitszeiten_m>`.
    krankheitszeiten_ab_16_bis_24_m
        See basic input variable :ref:`krankheitszeiten_ab_16_bis_24_m <krankheitszeiten_ab_16_bis_24_m>`.
    mutterschutzzeiten_m
        See basic input variable :ref:`mutterschutzzeiten_m <mutterschutzzeiten_m>`.
    arbeitslosigkeitszeiten_m
        See basic input variable :ref:`arbeitslosigkeitszeiten_m <arbeitslosigkeitszeiten_m>`.
    ausbildungssuche_m
        See basic input variable :ref:`ausbildungssuche_m <ausbildungssuche_m>`.
    schulausbildung_m
        See basic input variable :ref:`schulausbildung_m <schulausbildung_m>`.

    Returns
    -------
    Anrechnungszeit in months
    """
    out = (
        arbeitsunfähigkeitszeiten_m
        + krankheitszeiten_ab_16_bis_24_m
        + mutterschutzzeiten_m
        + arbeitslosigkeitszeiten_m
        + ausbildungssuche_m
        + schulausbildung_m
    )
    return out


@policy_function(start_date="2012-01-01")
def anrechnungszeit_45(
    arbeitsunfähigkeitszeiten_m: float,
    entgeltersatzleistungen_arbeitslosigkeit_m: float,
    zeiten_geringfügiger_beschäftigung_m: float,
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
    arbeitsunfähigkeitszeiten_m
        See basic input variable :ref:`arbeitsunfähigkeitszeiten_m <arbeitsunfähigkeitszeiten_m>`.
    entgeltersatzleistungen_arbeitslosigkeit_m
        See basic input variable :ref:`entgeltersatzleistungen_arbeitslosigkeit_m <entgeltersatzleistungen_arbeitslosigkeit_m>`.
    zeiten_geringfügiger_beschäftigung_m
        See basic input variable :ref:`zeiten_geringfügiger_beschäftigung_m <zeiten_geringfügiger_beschäftigung_m>`.
    Returns
    -------
    Anrechnungszeit in months.

    """
    out = (
        arbeitsunfähigkeitszeiten_m
        + entgeltersatzleistungen_arbeitslosigkeit_m
        + zeiten_geringfügiger_beschäftigung_m
    )

    return out
