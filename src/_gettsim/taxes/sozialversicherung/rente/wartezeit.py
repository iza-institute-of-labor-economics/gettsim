"""Pension-relevant periods."""

from _gettsim.function_types import policy_function


@policy_function()
def mindestwartezeit_erfüllt(
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    ersatzzeiten_monate: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Allgemeine Wartezeit has been completed. Aggregates time
    periods that are relevant for the general eligibility of the
    regular pension (regelaltersrente). "Allgemeine Wartezeit".

    Parameters
    ----------
    pflichtbeitragsmonate
        See :func:`pflichtbeitragsmonate`.
    freiwillige_beitragsmonate
        See :func:`freiwillige_beitragsmonate`.
    ersatzzeiten_monate
        See :func:`ersatzzeiten_monate`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 5 Jahren.

    """
    return (
        pflichtbeitragsmonate + freiwillige_beitragsmonate + ersatzzeiten_monate
    ) / 12 >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_5"]


@policy_function()
def wartezeit_15_jahre_erfüllt(
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    ersatzzeiten_monate: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 15 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the Altersrente für Frauen
    and Leistungen zur Teilhabe. Wartezeit von 15 Jahren.

    Parameters
    ----------
    pflichtbeitragsmonate
        See :func:`pflichtbeitragsmonate`.
    freiwillige_beitragsmonate
        See :func:`freiwillige_beitragsmonate`.
    ersatzzeiten_monate
        See :func:`ersatzzeiten_monate`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 15 Jahren

    """
    return (
        pflichtbeitragsmonate + freiwillige_beitragsmonate + ersatzzeiten_monate
    ) / 12 >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_15"]


@policy_function()
def wartezeit_35_jahre_erfüllt(  # noqa: PLR0913
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    anrechnungsmonate_35_jahre_wartezeit: float,
    ersatzzeiten_monate: float,
    kinderberücksichtigungszeiten_monate: float,
    pflegeberücksichtigungszeiten_monate: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 35 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    langjährig Versicherte (pension for long-term insured). Wartezeit von 35 Jahren. All
    "rentenrechtliche Zeiten" are considered.

    Parameters
    ----------
    pflichtbeitragsmonate
        See :func:`pflichtbeitragsmonate`.
    freiwillige_beitragsmonate
        See :func:`freiwillige_beitragsmonate`.
    ersatzzeiten_monate
        See :func:`ersatzzeiten_monate`.
    anrechnungsmonate_35_jahre_wartezeit
        See :func:`anrechnungsmonate_35_jahre_wartezeit`.
    kinderberücksichtigungszeiten_monate
        See :func:`kinderberücksichtigungszeiten_monate`.
    pflegeberücksichtigungszeiten_monate
        See :func:`pflegeberücksichtigungszeiten_monate`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 35 Jahren

    """
    return (
        pflichtbeitragsmonate
        + freiwillige_beitragsmonate
        + anrechnungsmonate_35_jahre_wartezeit
        + ersatzzeiten_monate
        + kinderberücksichtigungszeiten_monate
        + pflegeberücksichtigungszeiten_monate
    ) / 12 >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_35"]


@policy_function(start_date="2012-01-01")
def wartezeit_45_jahre_erfüllt(  # noqa: PLR0913
    pflichtbeitragsmonate: float,
    freiwillige_beitragsmonate: float,
    anrechnungsmonate_45_jahre_wartezeit: float,
    ersatzzeiten_monate: float,
    kinderberücksichtigungszeiten_monate: float,
    pflegeberücksichtigungszeiten_monate: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 45 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    besonders langjährig Versicherte (pension for very long-term insured). Wartezeit von
    45 Jahren. Not all "rentenrechtliche Zeiten" are considered. Years with voluntary
    contributions are only considered if at least 18 years of mandatory contributions
    (pflichtbeitragsmonate). Not all anrechnungszeiten are considered, but only
    specific ones (e.g. ALG I, Kurzarbeit but not ALG II).

    Parameters
    ----------
    pflichtbeitragsmonate
        See basic input variable :ref:`pflichtbeitragsmonate <pflichtbeitragsmonate>`.
    freiwillige_beitragsmonate
        See basic input variable :ref:`freiwillige_beitragsmonate <freiwillige_beitragsmonate>`.
    anrechnungsmonate_45_jahre_wartezeit
        See :func:`anrechnungsmonate_45_jahre_wartezeit`.
    ersatzzeiten_monate
        See basic input variable :ref:`ersatzzeiten_monate <ersatzzeiten_monate>`.
    kinderberücksichtigungszeiten_monate
        See basic input variable :ref:`kinderberücksichtigungszeiten_monate <kinderberücksichtigungszeiten_monate>`.
    pflegeberücksichtigungszeiten_monate
        See basic input variable :ref:`pflegeberücksichtigungszeiten_monate <pflegeberücksichtigungszeiten_monate>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 45 Jahren

    """
    if (
        pflichtbeitragsmonate / 12
        >= ges_rente_params[
            "mindestpflichtbeitragsjahre_für_anrechnbarkeit_freiwilliger_beiträge"
        ]
    ):
        freiwillige_beitragszeiten = freiwillige_beitragsmonate
    else:
        freiwillige_beitragszeiten = 0

    return (
        pflichtbeitragsmonate
        + freiwillige_beitragszeiten
        + anrechnungsmonate_45_jahre_wartezeit
        + ersatzzeiten_monate
        + pflegeberücksichtigungszeiten_monate
        + kinderberücksichtigungszeiten_monate
    ) / 12 >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_45"]


@policy_function()
def anrechnungsmonate_35_jahre_wartezeit(  # noqa: PLR0913
    monate_in_arbeitsunfähigkeit: float,
    krankheitsmonate_ab_16_bis_24_monate: float,
    monate_in_mutterschutz: float,
    monate_in_arbeitslosigkeit: float,
    monate_in_ausbildungssuche: float,
    monate_der_schulausbildung: float,
) -> float:
    """Adds up all times that are accounted for in "Anrechnungszeiten"
    relevant for "Wartezeit von 35 Jahren" i.e. for Altersrente für
    langjährig Versicherte (pension for long term insured).
    (Ref: Studientext der Deutschen Rentenversicherung, Nr. 19,
    Wartezeiten, Ausgabe 2021, S. 24.)


    Parameters
    ----------
    monate_in_arbeitsunfähigkeit
        See :func:`monate_in_arbeitsunfähigkeit`.
    krankheitsmonate_ab_16_bis_24_monate
        See :func:`krankheitsmonate_ab_16_bis_24_monate`.
    monate_in_mutterschutz
        See :func:`monate_in_mutterschutz`.
    monate_in_arbeitslosigkeit
        See :func:`monate_in_arbeitslosigkeit`.
    monate_in_ausbildungssuche
        See :func:`monate_in_ausbildungssuche`.
    monate_der_schulausbildung
        See :func:`monate_der_schulausbildung`.

    Returns
    -------
    Anrechnungszeit in months
    """
    return (
        monate_in_arbeitsunfähigkeit
        + krankheitsmonate_ab_16_bis_24_monate
        + monate_in_mutterschutz
        + monate_in_arbeitslosigkeit
        + monate_in_ausbildungssuche
        + monate_der_schulausbildung
    )


@policy_function(start_date="2012-01-01")
def anrechnungsmonate_45_jahre_wartezeit(
    monate_in_arbeitsunfähigkeit: float,
    monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit: float,
    monate_geringfügiger_beschäftigung: float,
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
    monate_in_arbeitsunfähigkeit
        See :func:`monate_in_arbeitsunfähigkeit`.
    monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit
        See :func:`monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit`.
    monate_geringfügiger_beschäftigung
        See :func:`monate_geringfügiger_beschäftigung`.
    Returns
    -------
    Anrechnungszeit in months.

    """
    return (
        monate_in_arbeitsunfähigkeit
        + monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit
        + monate_geringfügiger_beschäftigung
    )
