"""Public pension benefits for retirement due to reduced earnings potential."""

from _gettsim.function_types import policy_function


@policy_function(start_date="2001-01-01")
def betrag_m(  # noqa: PLR0913
    zugangsfaktor: float,
    sozialversicherung__rente__entgeltpunkte_west: float,
    sozialversicherung__rente__entgeltpunkte_ost: float,
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
    sozialversicherung__rente__entgeltpunkte_west
        See :func:`sozialversicherung__rente__entgeltpunkte_west`.
    sozialversicherung__rente__entgeltpunkte_ost
        See :func:`sozialversicherung__rente__entgeltpunkte_ost`.
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
                sozialversicherung__rente__entgeltpunkte_west
                * ges_rente_params["rentenwert"]["west"]
                + sozialversicherung__rente__entgeltpunkte_ost
                * ges_rente_params["rentenwert"]["ost"]
            )
            * zugangsfaktor
            * rentenartfaktor
        )
    else:
        out = 0.0
    return out


@policy_function(start_date="2001-01-01")
def grundsätzlich_anspruchsberechtigt(
    voll_erwerbsgemindert: bool,
    teilweise_erwerbsgemindert: bool,
    sozialversicherung__rente__pflichtbeitragszeiten_m: float,
    sozialversicherung__rente__mindestwartezeit_erfüllt: bool,
) -> bool:
    """
    Eligibility for Erwerbsminderungsrente (public disability insurance claim).

    Legal reference: § 43 Abs. 1  SGB VI

    Parameters
    ----------
    voll_erwerbsgemindert
        See basic input variable :ref:`voll_erwerbsgemindert <voll_erwerbsgemindert>.
    teilweise_erwerbsgemindert
        See basic input variable :ref:`teilweise_erwerbsgemindert <teilweise_erwerbsgemindert>.
    sozialversicherung__rente__pflichtbeitragszeiten_m
        See basic input variable :ref:`sozialversicherung__rente__pflichtbeitragszeiten_m <sozialversicherung__rente__pflichtbeitragszeiten_m>.
    sozialversicherung__rente__mindestwartezeit_erfüllt
        See :func:`sozialversicherung__rente__mindestwartezeit_erfüllt`.
    Returns
    -------
    Eligibility for Erwerbsminderungsrente (public disability insurance claim) as a bool
    """

    anspruch_erwerbsm_rente = (
        (voll_erwerbsgemindert or teilweise_erwerbsgemindert)
        and sozialversicherung__rente__mindestwartezeit_erfüllt
        and sozialversicherung__rente__pflichtbeitragszeiten_m >= 36
    )

    return anspruch_erwerbsm_rente


@policy_function(start_date="2001-01-01")
def sozialversicherung__rente__entgeltpunkte_west(
    sozialversicherung__rente__entgeltpunkte_west: float,
    zurechnungszeit: float,
    sozialversicherung__rente__altersrente__anteil_entgeltpunkte_ost: float,
) -> float:
    """Entgeltpunkte accumulated in Western Germany which Erwerbsminderungsrente
    is based on (public disability insurance)
    In the case of the public disability insurance,
    pensioners are credited with additional earning points.
    They receive their average earned income points for
    each year between their age of retirement and the "zurechnungszeitgrenze".

    Parameters
    ----------
    sozialversicherung__rente__entgeltpunkte_west
        See basic input variable :ref:`sozialversicherung__rente__entgeltpunkte_west <sozialversicherung__rente__entgeltpunkte_west>
    zurechnungszeit
        See :func:`zurechnungszeit`.
    sozialversicherung__rente__altersrente__anteil_entgeltpunkte_ost
        See :func:`sozialversicherung__rente__altersrente__anteil_entgeltpunkte_ost`.

    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """

    out = sozialversicherung__rente__entgeltpunkte_west + (
        zurechnungszeit
        * (1 - sozialversicherung__rente__altersrente__anteil_entgeltpunkte_ost)
    )

    return out


@policy_function(start_date="2001-01-01")
def sozialversicherung__rente__entgeltpunkte_ost(
    sozialversicherung__rente__entgeltpunkte_ost: float,
    zurechnungszeit: float,
    sozialversicherung__rente__altersrente__anteil_entgeltpunkte_ost: float,
) -> float:
    """Entgeltpunkte accumulated in Eastern Germany which Erwerbsminderungsrente
    is based on (public disability insurance)
    In the case of the public disability insurance,
    pensioners are credited with additional earning points.
    They receive their average earned income points for
    each year between their age of retirement and the "zurechnungszeitgrenze".

    Parameters
    ----------
    sozialversicherung__rente__entgeltpunkte_ost
        See basic input variable :ref:`sozialversicherung__rente__entgeltpunkte_ost <sozialversicherung__rente__entgeltpunkte_ost>
    zurechnungszeit
        See :func:`zurechnungszeit`.
    sozialversicherung__rente__altersrente__anteil_entgeltpunkte_ost
        See :func:`sozialversicherung__rente__altersrente__anteil_entgeltpunkte_ost`.

    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """

    out = sozialversicherung__rente__entgeltpunkte_ost + (
        zurechnungszeit
        * sozialversicherung__rente__altersrente__anteil_entgeltpunkte_ost
    )

    return out


@policy_function(start_date="2001-01-01")
def zurechnungszeit(
    durchschnittliche_entgeltpunkte: float,
    sozialversicherung__rente__alter_bei_renteneintritt: float,
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
    sozialversicherung__rente__alter_bei_renteneintritt
        See :func:`sozialversicherung__rente__alter_bei_renteneintritt`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.


    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """
    zurechnungszeitgrenze = erwerbsm_rente_params["zurechnungszeitgrenze"]

    out = (
        zurechnungszeitgrenze - (sozialversicherung__rente__alter_bei_renteneintritt)
    ) * durchschnittliche_entgeltpunkte

    return out


@policy_function(start_date="2001-01-01")
def rentenartfaktor(
    teilweise_erwerbsgemindert: bool,
    erwerbsm_rente_params: dict,
) -> float:
    """rentenartfaktor for Erwerbsminderungsrente
    (public disability insurance)

    Legal reference: SGB VI § 67: rentenartfaktor

    Parameters
    ----------
    teilweise_erwerbsgemindert
        See basic input variable :ref:`teilweise_erwerbsgemindert <teilweise_erwerbsgemindert>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    rentenartfaktor

    """

    if teilweise_erwerbsgemindert:
        out = erwerbsm_rente_params["rentenartfaktor"]["teilw"]

    else:
        out = erwerbsm_rente_params["rentenartfaktor"]["voll"]

    return out


@policy_function(start_date="2001-01-01")
def zugangsfaktor(
    sozialversicherung__rente__alter_bei_renteneintritt: float,
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
    sozialversicherung__rente__alter_bei_renteneintritt
        See :func:`sozialversicherung__rente__alter_bei_renteneintritt`.
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
        + (
            sozialversicherung__rente__alter_bei_renteneintritt
            - altersgrenze_abschlagsfrei
        )
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
    sozialversicherung__rente__pflichtbeitragszeiten_m: float,
    sozialversicherung__rente__freiwillige_beitragszeiten_m: float,
    sozialversicherung__rente__anrechnungszeit_45_y: float,
    sozialversicherung__rente__ersatzzeiten_m: float,
    sozialversicherung__rente__kinderberücksichtigungszeiten_m: float,
    sozialversicherung__rente__pflegeberücksichtigungszeiten_m: float,
    ges_rente_params: dict,
    erwerbsm_rente_params: dict,
) -> bool:
    """Whether Wartezeit of 35 or 40 years according to § 51 Abs. 3a SGB VI is fulfilled

    Parameters
    ----------
    sozialversicherung__rente__pflichtbeitragszeiten_m
        See basic input variable :ref:<sozialversicherung__rente__pflichtbeitragszeiten_m>`.
    sozialversicherung__rente__freiwillige_beitragszeiten_m
        See basic input variable :ref:<sozialversicherung__rente__freiwillige_beitragszeiten_m>`.
    sozialversicherung__rente__anrechnungszeit_45_y
        See :func:`sozialversicherung__rente__anrechnungszeit_45_y`.
    sozialversicherung__rente__ersatzzeiten_m
        See basic input variable :ref:<sozialversicherung__rente__ersatzzeiten_m>`.
    sozialversicherung__rente__kinderberücksichtigungszeiten_m
        See basic input variable :ref:<sozialversicherung__rente__kinderberücksichtigungszeiten_m>`.
    sozialversicherung__rente__pflegeberücksichtigungszeiten_m
        See basic input variable :ref:<sozialversicherung__rente__pflegeberücksichtigungszeiten_m>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>`.

    Returns
    -------
    Wartezeit of 35 or 40 years according to § 51 Abs. 3a SGB VI is fulfilled

    """
    if (
        sozialversicherung__rente__pflichtbeitragszeiten_m
        >= ges_rente_params["wartezeit_45_pflichtbeitragsjahre"]
    ):
        freiwilligbeitr = sozialversicherung__rente__freiwillige_beitragszeiten_m
    else:
        freiwilligbeitr = 0

    m_zeiten = (
        sozialversicherung__rente__pflichtbeitragszeiten_m
        + freiwilligbeitr
        + sozialversicherung__rente__anrechnungszeit_45_y
        + sozialversicherung__rente__ersatzzeiten_m
        + sozialversicherung__rente__pflegeberücksichtigungszeiten_m
        + sozialversicherung__rente__kinderberücksichtigungszeiten_m
    ) / 12

    out = (
        m_zeiten
        >= erwerbsm_rente_params["wartezeitgrenze_langj_versicherte_abschlagsfrei"]
    )

    return out


@policy_function()
def durchschnittliche_entgeltpunkte(
    sozialversicherung__rente__entgeltpunkte_west: float,
    sozialversicherung__rente__entgeltpunkte_ost: float,
    sozialversicherung__rente__alter_bei_renteneintritt: float,
    erwerbsm_rente_params: dict,
) -> float:
    """Average earning points as part of the "Grundbewertung".
    Earnings points are divided by "belegungsfähige Gesamtzeitraum" which is
    the period from the age of 17 until the start of the pension.

    Legal reference: SGB VI § 72: Grundbewertung

    Parameters
    ----------
    sozialversicherung__rente__entgeltpunkte_west
        See basic input variable :ref:<sozialversicherung__rente__entgeltpunkte_west>
    sozialversicherung__rente__entgeltpunkte_ost
        See basic input variable :ref:<sozialversicherung__rente__entgeltpunkte_ost>
    sozialversicherung__rente__alter_bei_renteneintritt
        See :func:`sozialversicherung__rente__alter_bei_renteneintritt`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    average entgeltp
    """

    belegungsfähiger_gesamtzeitraum = (
        sozialversicherung__rente__alter_bei_renteneintritt
        - erwerbsm_rente_params["altersgrenze_grundbewertung"]
    )

    durchschnittliche_entgeltpunkte = (
        sozialversicherung__rente__entgeltpunkte_west
        + sozialversicherung__rente__entgeltpunkte_ost
    ) / belegungsfähiger_gesamtzeitraum

    return durchschnittliche_entgeltpunkte
