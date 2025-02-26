"""Public pension benefits for retirement due to reduced earnings potential."""

from _gettsim.functions.policy_function import policy_function


@policy_function(start_date="2001-01-01")
def betrag_m(  # noqa: PLR0913
    zugangsfaktor: float,
    entgeltpunkte_west: float,
    entgeltpunkte_ost: float,
    rentenartfaktor: float,
    grundsätzlich_anspruchsberechtigt: bool,
    ges_rente_params: dict,
) -> float:
    """Erwerbsminderungsrente (amount paid by public disability insurance if claimed)

    Legal reference: SGB VI § 64: Rentenformel für Monatsbetrag der Rente


    Parameters
    ----------
    zugangsfaktor
        See :func:`zugangsfaktor`.
    entgeltpunkte_west
        See :func:`entgeltpunkte_west`.
    entgeltpunkte_ost
        See :func:`entgeltpunkte_ost`.
    rentenwert
        See :func:`rentenwert`.
    rentenartfaktor
        See :func:`rentenartfaktor`.
    grundsätzlich_anspruchsberechtigt
        See :func:`grundsätzlich_anspruchsberechtigt`.
    Returns
    -------
    Erwerbsminderungsrente (amount paid by public disability insurance if claimed)

    """

    if grundsätzlich_anspruchsberechtigt:
        out = (
            (
                entgeltpunkte_west * ges_rente_params["rentenwert"]["west"]
                + entgeltpunkte_ost * ges_rente_params["rentenwert"]["ost"]
            )
            * zugangsfaktor
            * rentenartfaktor
        )
    else:
        out = 0.0
    return out


@policy_function(start_date="2001-01-01")
def grundsätzlich_anspruchsberechtigt(
    voll_erwerbsgemind: bool,
    teilw_erwerbsgemind: bool,
    m_pflichtbeitrag: float,
    rente__altersrente__mindestwartezeit_erfüllt: bool,
) -> bool:
    """
    Eligibility for Erwerbsminderungsrente (public disability insurance claim).

    Legal reference: § 43 Abs. 1  SGB VI

    Parameters
    ----------
    voll_erwerbsgemind
        See basic input variable :ref:`voll_erwerbsgemind <voll_erwerbsgemind>.
    teilw_erwerbsgemind
        See basic input variable :ref:`teilw_erwerbsgemind <teilw_erwerbsgemind>.
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>.
    rente__altersrente__mindestwartezeit_erfüllt
        See :func:`rente__altersrente__mindestwartezeit_erfüllt`.
    Returns
    -------
    Eligibility for Erwerbsminderungsrente (public disability insurance claim) as a bool
    """

    anspruch_erwerbsm_rente = (
        (voll_erwerbsgemind or teilw_erwerbsgemind)
        and rente__altersrente__mindestwartezeit_erfüllt
        and m_pflichtbeitrag >= 36
    )

    return anspruch_erwerbsm_rente


@policy_function(start_date="2001-01-01")
def entgeltpunkte_west(
    entgeltp_west: float,
    zurechnungszeit: float,
    rente__altersrente__anteil_entgeltp_ost: float,
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
    zurechnungszeit
        See :func:`zurechnungszeit`.
    rente__altersrente__anteil_entgeltp_ost
        See :func:`rente__altersrente__anteil_entgeltp_ost`.

    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """

    out = entgeltp_west + (
        zurechnungszeit * (1 - rente__altersrente__anteil_entgeltp_ost)
    )

    return out


@policy_function(start_date="2001-01-01")
def entgeltpunkte_ost(
    entgeltp_ost: float,
    zurechnungszeit: float,
    rente__altersrente__anteil_entgeltp_ost: float,
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
    zurechnungszeit
        See :func:`zurechnungszeit`.
    rente__altersrente__anteil_entgeltp_ost
        See :func:`rente__altersrente__anteil_entgeltp_ost`.

    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """

    out = entgeltp_ost + (zurechnungszeit * rente__altersrente__anteil_entgeltp_ost)

    return out


@policy_function(start_date="2001-01-01")
def zurechnungszeit(
    durchschnittliche_entgeltpunkte: float,
    rente__alter_bei_renteneintritt: float,
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
    durchschnittliche_entgeltpunkte
        See :func:`durchschnittliche_entgeltpunkte`.
    rente__alter_bei_renteneintritt
        See :func:`rente__alter_bei_renteneintritt`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.


    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """
    zurechnungszeitgrenze = erwerbsm_rente_params["zurechnungszeitgrenze"]

    out = (
        zurechnungszeitgrenze - (rente__alter_bei_renteneintritt)
    ) * durchschnittliche_entgeltpunkte

    return out


@policy_function(start_date="2001-01-01")
def rentenartfaktor(
    teilw_erwerbsgemind: bool,
    erwerbsm_rente_params: dict,
) -> float:
    """rentenartfaktor for Erwerbsminderungsrente
    (public disability insurance)

    Legal reference: SGB VI § 67: rentenartfaktor

    Parameters
    ----------
    teilw_erwerbsgemind
        See basic input variable :ref:`teilw_erwerbsgemind <teilw_erwerbsgemind>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    rentenartfaktor

    """

    if teilw_erwerbsgemind:
        out = erwerbsm_rente_params["rentenartfaktor"]["teilw"]

    else:
        out = erwerbsm_rente_params["rentenartfaktor"]["voll"]

    return out


@policy_function(start_date="2001-01-01")
def zugangsfaktor(
    rente__alter_bei_renteneintritt: float,
    wartezeit_langjährig_versichert_erfüllt: bool,
    ges_rente_params: dict,
    erwerbsm_rente_params: dict,
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
    rente__alter_bei_renteneintritt
        See :func:`rente__alter_bei_renteneintritt`.
    wartezeit_langjährig_versichert_erfüllt
        See :func:`wartezeit_langjährig_versichert_erfüllt`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.


    Returns
    -------
    Zugangsfaktor for Erwerbsminderungsrente (public disability insurance)

    """

    if wartezeit_langjährig_versichert_erfüllt:
        altersgrenze_abschlagsfrei = erwerbsm_rente_params[
            "altersgrenze_langj_versicherte_abschlagsfrei"
        ]
    else:
        altersgrenze_abschlagsfrei = erwerbsm_rente_params["altersgrenze_abschlagsfrei"]

    zugangsfaktor = (
        1
        + (rente__alter_bei_renteneintritt - altersgrenze_abschlagsfrei)
        * (
            ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
                "vorzeitiger_renteneintritt"
            ]
        )
    )
    out = max(zugangsfaktor, erwerbsm_rente_params["min_zugangsfaktor"])

    return out


@policy_function(start_date="2001-01-01")
def wartezeit_langjährig_versichert_erfüllt(  # noqa: PLR0913
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    rente__altersrente__anrechnungszeit_45: float,
    m_ersatzzeit: float,
    m_kind_berücks_zeit: float,
    m_pfleg_berücks_zeit: float,
    ges_rente_params: dict,
    erwerbsm_rente_params: dict,
) -> bool:
    """Whether Wartezeit of 35 or 40 years according to § 51 Abs. 3a SGB VI is fulfilled

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    rente__altersrente__anrechnungszeit_45
        See :func:`rente__altersrente__anrechnungszeit_45`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    m_kind_berücks_zeit
        See basic input variable :ref:`m_kind_berücks_zeit <m_kind_berücks_zeit>`.
    m_pfleg_berücks_zeit
        See basic input variable :ref:`m_pfleg_berücks_zeit <m_pfleg_berücks_zeit>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>`.

    Returns
    -------
    Wartezeit of 35 or 40 years according to § 51 Abs. 3a SGB VI is fulfilled

    """
    if m_pflichtbeitrag >= ges_rente_params["wartezeit_45_pflichtbeitragsmonate"]:
        freiwilligbeitr = m_freiw_beitrag
    else:
        freiwilligbeitr = 0

    m_zeiten = (
        m_pflichtbeitrag
        + freiwilligbeitr
        + rente__altersrente__anrechnungszeit_45
        + m_ersatzzeit
        + m_pfleg_berücks_zeit
        + m_kind_berücks_zeit
    ) / 12

    out = (
        m_zeiten
        >= erwerbsm_rente_params["wartezeitgrenze_langj_versicherte_abschlagsfrei"]
    )

    return out


@policy_function
def durchschnittliche_entgeltpunkte(
    entgeltp_west: float,
    entgeltp_ost: float,
    rente__alter_bei_renteneintritt: float,
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
    rente__alter_bei_renteneintritt
        See :func:`rente__alter_bei_renteneintritt`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    average entgeltp
    """

    beleg_gesamtzeitr = (
        rente__alter_bei_renteneintritt
        - erwerbsm_rente_params["altersgrenze_grundbewertung"]
    )

    durchschnittliche_entgeltpunkte = (entgeltp_west + entgeltp_ost) / beleg_gesamtzeitr

    return durchschnittliche_entgeltpunkte
