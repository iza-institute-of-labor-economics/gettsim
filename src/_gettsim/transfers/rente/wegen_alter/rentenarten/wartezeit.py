"""Pension-relevant periods."""

from _gettsim.shared import policy_info


def ges_rente_wartezeit_5(
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    m_ersatzzeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Allgemeine Wartezeit has been completed. Aggregates time
    periods that are relevant for the general eligibility of the
    regular pension (regelaltersrente). "Allgemeine Wartezeit".

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 5 Jahren.

    """
    m_zeiten = (m_pflichtbeitrag + m_freiw_beitrag + m_ersatzzeit) / 12

    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_5"]

    return out


def ges_rente_wartezeit_15(
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    m_ersatzzeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 15 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the Altersrente für Frauen
    and Leistungen zur Teilhabe. Wartezeit von 15 Jahren.

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 15 Jahren

    """
    m_zeiten = (m_pflichtbeitrag + m_freiw_beitrag + m_ersatzzeit) / 12

    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_15"]

    return out


def ges_rente_wartezeit_35(  # noqa: PLR0913
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    ges_rente_anrechnungszeit: float,
    m_ersatzzeit: float,
    m_kind_berücks_zeit: float,
    m_pfleg_berücks_zeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 35 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    langjährig Versicherte (pension for long-term insured). Wartezeit von 35 Jahren. All
    "rentenrechtliche Zeiten" are considered.

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    ges_rente_anrechnungszeit
        See :func:`ges_rente_anrechnungszeit`
    m_kind_berücks_zeit
        See basic input variable :ref:`m_kind_berücks_zeit <m_kind_berücks_zeit>`.
    m_pfleg_berücks_zeit
        See basic input variable :ref:`m_pfleg_berücks_zeit <m_pfleg_berücks_zeit>`
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 35 Jahren

    """
    m_zeiten = (
        m_pflichtbeitrag
        + m_freiw_beitrag
        + ges_rente_anrechnungszeit
        + m_ersatzzeit
        + m_pfleg_berücks_zeit
        + m_kind_berücks_zeit
    ) / 12
    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_35"]

    return out


@policy_info(start_date="2012-01-01")
def ges_rente_wartezeit_45(  # noqa: PLR0913
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    ges_rente_anrechnungszeit_45: float,
    m_ersatzzeit: float,
    m_kind_berücks_zeit: float,
    m_pfleg_berücks_zeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 45 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    besonders langjährig Versicherte (pension for very long-term insured). Wartezeit von
    45 Jahren. Not all "rentenrechtliche Zeiten" are considered. Years with voluntary
    contributions are only considered if at least 18 years of mandatory contributions
    (m_pflichtbeitrag). Not all ges_rente_anrechnungszeiten are considered, but only
    specific ones (e.g. ALG I, Kurzarbeit but not ALG II).

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    ges_rente_anrechnungszeit_45
        See :func:`ges_rente_anrechnungszeit_45`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    m_kind_berücks_zeit
        See basic input variable :ref:`m_kind_berücks_zeit <m_kind_berücks_zeit>`.
    m_pfleg_berücks_zeit
        See basic input variable :ref:`m_pfleg_berücks_zeit <m_pfleg_berücks_zeit>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 45 Jahren

    """
    if m_pflichtbeitrag >= ges_rente_params["wartezeit_45_pflichtbeitragsmonate"]:
        freiwilligbeitr = m_freiw_beitrag
    else:
        freiwilligbeitr = 0

    m_zeiten = (
        m_pflichtbeitrag
        + freiwilligbeitr
        + ges_rente_anrechnungszeit_45
        + m_ersatzzeit
        + m_pfleg_berücks_zeit
        + m_kind_berücks_zeit
    ) / 12
    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_45"]

    return out


def ges_rente_anrechnungszeit(  # noqa: PLR0913
    m_arbeitsunfähig: float,
    m_krank_ab_16_bis_24: float,
    m_mutterschutz: float,
    m_arbeitsl: float,
    m_ausbild_suche: float,
    m_schul_ausbild: float,
) -> float:
    """Adds up all times that are accounted for in "Anrechnungszeiten"
    relevant for "Wartezeit von 35 Jahren" i.e. for Altersrente für
    langjährig Versicherte (pension for long term insured).
    (Ref: Studientext der Deutschen Rentenversicherung, Nr. 19,
    Wartezeiten, Ausgabe 2021, S. 24.)


    Parameters
    ----------
    m_arbeitsunfähig
        See basic input variable :ref:`m_arbeitsunfähig <m_arbeitsunfähig>`.
    m_krank_ab_16_bis_24
        See basic input variable :ref:`m_krank_ab_16_bis_24 <m_krank_ab_16_bis_24>`.
    m_mutterschutz
        See basic input variable :ref:`m_mutterschutz <m_mutterschutz>`.
    m_arbeitsl
        See basic input variable :ref:`m_arbeitsl <m_arbeitsl>`.
    m_ausbild_suche
        See basic input variable :ref:`m_ausbild_suche <m_ausbild_suche>`.
    m_schul_ausbild
        See basic input variable :ref:`m_schul_ausbild <m_schul_ausbild>`.

    Returns
    -------
    Anrechnungszeit in months
    """
    out = (
        m_arbeitsunfähig
        + m_krank_ab_16_bis_24
        + m_mutterschutz
        + m_arbeitsl
        + m_ausbild_suche
        + m_schul_ausbild
    )
    return out


@policy_info(start_date="2012-01-01")
def ges_rente_anrechnungszeit_45(
    m_arbeitsunfähig: float,
    m_alg1_übergang: float,
    m_geringf_beschäft: float,
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
    m_arbeitsunfähig
        See basic input variable :ref:`m_arbeitsunfähig <m_arbeitsunfähig>`.
    m_alg1_übergang
        See basic input variable :ref:`m_alg1_übergang <m_alg1_übergang>`.
    m_geringf_beschäft
        See basic input variable :ref:`m_geringf_beschäft <m_geringf_beschäft>`.
    Returns
    -------
    Anrechnungszeit in months.

    """
    out = m_arbeitsunfähig + m_alg1_übergang + m_geringf_beschäft

    return out
