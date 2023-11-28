from _gettsim.shared import dates_active


@dates_active(start="2001-01-01")
def erwerbsm_rente_m(  # noqa: PLR0913
    erwerbsm_rente_zugangsfaktor: float,
    entgeltp_west_erwerbsm_rente: float,
    entgeltp_ost_erwerbsm_rente: float,
    rentenartfaktor: float,
    ges_rente_vorauss_erwerbsm: bool,
    ges_rente_params: dict,
) -> float:
    """Erwerbsminderungsrente (amount paid by public disability insurance if claimed)

    Legal reference: SGB VI § 64: Rentenformel für Monatsbetrag der Rente


    Parameters
    ----------
    erwerbsm_rente_zugangsfaktor
        See :func:`erwerbsm_rente_zugangsfaktor`.
    entgeltp_west_erwerbsm_rente
        See :func:`entgeltp_west_erwerbsm_rente`.
    entgeltp_ost_erwerbsm_rente
        See :func:`entgeltp_ost_erwerbsm_rente`.
    rentenwert
        See :func:`rentenwert`.
    rentenartfaktor
        See :func:`rentenartfaktor`.
    ges_rente_vorauss_erwerbsm
        See :func:`ges_rente_vorauss_erwerbsm`.
    Returns
    -------
    Erwerbsminderungsrente (amount paid by public disability insurance if claimed)

    """

    if ges_rente_vorauss_erwerbsm:
        out = (
            (
                entgeltp_west_erwerbsm_rente * ges_rente_params["rentenwert"]["west"]
                + entgeltp_ost_erwerbsm_rente * ges_rente_params["rentenwert"]["ost"]
            )
            * erwerbsm_rente_zugangsfaktor
            * rentenartfaktor
        )
    else:
        out = 0.0
    return out


@dates_active(start="2001-01-01")
def ges_rente_vorauss_erwerbsm(
    voll_erwerbsgemindert: bool,
    teilw_erwerbsgemindert: bool,
    m_pflichtbeitrag: float,
    ges_rente_wartezeit_5: bool,
) -> bool:
    """
    Eligibility for Erwerbsminderungsrente (public disability insurance claim).

    Legal reference: § 43 Abs. 1  SGB VI

    Parameters
    ----------
    voll_erwerbsgemindert
        See basic input variable :ref:`voll_erwerbsgemindert <voll_erwerbsgemindert>.
    teilw_erwerbsgemindert
        See basic input variable :ref:`teilw_erwerbsgemindert <teilw_erwerbsgemindert>.
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>.
    ges_rente_wartezeit_5
        See :func:`ges_rente_wartezeit_5`.
    Returns
    -------
    Eligibility for Erwerbsminderungsrente (public disability insurance claim) as a bool
    """

    anspruch_erwerbsm_rente = (
        (voll_erwerbsgemindert or teilw_erwerbsgemindert)
        and ges_rente_wartezeit_5
        and m_pflichtbeitrag >= 36
    )

    return anspruch_erwerbsm_rente


@dates_active(start="2001-01-01")
def entgeltp_west_erwerbsm_rente(
    entgeltp_west: float,
    entgeltp_zurechnungszeit: float,
    anteil_entgeltp_ost: float,
) -> float:
    """Entgeltpunkte accumulated in Western Germany which Erwerbsminderungsrente
    is based on (public disability insurance)
    In the case of the public disability insurance,
    pensioners are credited with additional earning points.
    They receive their average earned income points for
    each year between their age of retirement and the "zurechnungszeitgrenze".

    Parameters
    ----------
    entgeltp_west
        See basic input variable :ref:`entgeltp_west <entgeltp_west>
    entgeltp_zurechnungszeit
        See :func:`entgeltp_zurechnungszeit`.
    anteil_entgeltp_ost
        See :func:`anteil_entgeltp_ost`.

    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """

    out = entgeltp_west + (entgeltp_zurechnungszeit * (1 - anteil_entgeltp_ost))

    return out


@dates_active(start="2001-01-01")
def entgeltp_ost_erwerbsm_rente(
    entgeltp_ost: float,
    entgeltp_zurechnungszeit: float,
    anteil_entgeltp_ost: float,
) -> float:
    """Entgeltpunkte accumulated in Eastern Germany which Erwerbsminderungsrente
    is based on (public disability insurance)
    In the case of the public disability insurance,
    pensioners are credited with additional earning points.
    They receive their average earned income points for
    each year between their age of retirement and the "zurechnungszeitgrenze".

    Parameters
    ----------
    entgeltp_ost
        See basic input variable :ref:`entgeltp_ost <entgeltp_ost>
    entgeltp_zurechnungszeit
        See :func:`entgeltp_zurechnungszeit`.
    anteil_entgeltp_ost
        See :func:`anteil_entgeltp_ost`.

    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """

    out = entgeltp_ost + (entgeltp_zurechnungszeit * anteil_entgeltp_ost)

    return out


def anteil_entgeltp_ost(
    entgeltp_west: float,
    entgeltp_ost: float,
) -> float:
    """Proportion of Entgeltpunkte accumulated in East Germany

    Parameters
    ----------
    entgeltp_west
        See basic input variable :ref:`entgeltp_west <entgeltp_west>
    entgeltp_ost
        See basic input variable :ref:`entgeltp_ost <entgeltp_ost>

    Returns
    -------
    Proportion of Entgeltpunkte accumulated in East Germany

    """

    out = entgeltp_ost / (entgeltp_west + entgeltp_ost)

    return out


@dates_active(start="2001-01-01")
def entgeltp_zurechnungszeit(
    durchschn_entgeltp: float,
    age_of_retirement: float,
    erwerbsm_rente_params: dict,
) -> float:
    """Additional Entgeltpunkte accumulated through "Zurechnungszeit" for
    Erwerbsminderungsrente (public disability insurance)
    In the case of the public disability insurance,
    pensioners are credited with additional earning points.
    They receive their average earned income points for
    each year between their age of retirement and the "zurechnungszeitgrenze".

    Parameters
    ----------
    durchschn_entgeltp
        See :func:`durchschn_entgeltp`.
    age_of_retirement
        See :func:`age_of_retirement`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.


    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """
    zurechnungszeitgrenze = erwerbsm_rente_params["zurechnungszeitgrenze"]

    out = (zurechnungszeitgrenze - (age_of_retirement)) * durchschn_entgeltp

    return out


def durchschn_entgeltp(
    entgeltp_west: float,
    entgeltp_ost: float,
    age_of_retirement: float,
    erwerbsm_rente_params: dict,
) -> float:
    """Average earning points as part of the "Grundbewertung".
    Earnings points are divided by "belegungsfähige Gesamtzeitraum" which is
    the period from the age of 17 until the start of the pension.

    Legal reference: SGB VI § 72: Grundbewertung

    Parameters
    ----------
    entgeltp_west
        See basic input variable :ref:`entgeltp_west <entgeltp_west>
    entgeltp_ost
        See basic input variable :ref:`entgeltp_ost <entgeltp_ost>
    age_of_retirement
        See :func:`age_of_retirement`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    average entgeltp
    """

    beleg_gesamtzeitr = (
        age_of_retirement - erwerbsm_rente_params["altersgrenze_grundbewertung"]
    )

    durchschn_entgeltp = (entgeltp_west + entgeltp_ost) / beleg_gesamtzeitr

    return durchschn_entgeltp


@dates_active(start="2001-01-01")
def rentenartfaktor(
    teilw_erwerbsgemindert: bool,
    erwerbsm_rente_params: dict,
) -> float:
    """Rentenartfaktor for Erwerbsminderungsrente
    (public disability insurance)

    Legal reference: SGB VI § 67: Rentenartfaktor

    Parameters
    ----------
    teilw_erwerbsgemindert
        See basic input variable :ref:`teilw_erwerbsgemindert <teilw_erwerbsgemindert>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    Rentenartfaktor

    """

    if teilw_erwerbsgemindert:
        out = erwerbsm_rente_params["rentenartfaktor"]["teilw"]

    else:
        out = erwerbsm_rente_params["rentenartfaktor"]["voll"]

    return out


@dates_active(start="2001-01-01")
def erwerbsm_rente_zugangsfaktor(
    ges_rente_params: dict,
    erwerbsm_rente_params: dict,
    age_of_retirement: float,
    langj_versicherte_wartezeit: bool,
) -> float:
    """Zugangsfaktor for Erwerbsminderungsrente
    (public disability insurance)
    For each month that a pensioner retires before the age limit, a fraction of
    the pension is deducted. The maximum deduction is capped.
    This max deduction is the norm for the public disability insurance.

    Legal reference: § 77 Abs. 2-4  SGB VI

    Paragraph 4 regulates an exceptional case in which pensioners can already
    retire at 63 without deductions if they can prove 40 years of
    (Pflichtbeiträge, Berücksichtigungszeiten and
    certain Anrechnungszeiten or Ersatzzeiten).

    Parameters
    ----------
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.
    age_of_retirement
        See :func:`age_of_retirement`.
    langj_versicherte_wartezeit
        See :func:`langj_versicherte_wartezeit`.


    Returns
    -------
    Zugangsfaktor for Erwerbsminderungsrente (public disability insurance)

    """

    if langj_versicherte_wartezeit:
        altersgrenze_abschlagsfrei = erwerbsm_rente_params[
            "altersgrenze_langj_versicherte_abschlagsfrei"
        ]
    else:
        altersgrenze_abschlagsfrei = erwerbsm_rente_params["altersgrenze_abschlagsfrei"]

    zugangsfaktor = 1 + (age_of_retirement - altersgrenze_abschlagsfrei) * (
        ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
            "vorzeitiger_renteneintritt"
        ]
    )
    out = max(zugangsfaktor, erwerbsm_rente_params["min_zugangsfaktor"])

    return out


@dates_active(start="2001-01-01")
def langj_versicherte_wartezeit(  # noqa: PLR0913
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    ges_rente_anrechnungszeit_45: float,
    m_ersatzzeit: float,
    m_kind_berücks_zeit: float,
    m_pfleg_berücks_zeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 40 Jahren Wartezeit (Vertrauensschutz) has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    besonders langjährig Versicherte (pension for very long-term insured).

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
    Fulfilled Wartezeit von 40 Jahren

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
    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_40"]

    return out
