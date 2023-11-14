from _gettsim.shared import dates_active


@dates_active(start="2001-01-01")
def erwerbsm_rente_m(
    erwerbsm_rente_zugangsfaktor: float,
    entgeltp_erwerbsm_rente: float,
    rentenwert: float,
    rentenartfaktor: float,
    ges_rente_vorauss_erwerbsm: bool,
) -> float:
    """Erwerbsminderungsrente (public disability insurance claim)

    Legal reference: SGB VI § 64: Rentenformel für Monatsbetrag der Rente


    Parameters
    ----------
    erwerbsm_rente_zugangsfaktor
        See :func:`erwerbsm_rente_zugangsfaktor`.
    entgeltp_erwerbsm_rente
        See :func:`entgeltp_erwerbsm_rente`.
    rentenwert
        See :func:`rentenwert`.
    rentenartfaktor
        See :func:`rentenartfaktor`.
    ges_rente_vorauss_erwerbsm
        See :func:`ges_rente_vorauss_erwerbsm`.
    Returns
    -------
    Erwerbsminderungsrente (public disability insurance claim)

    """

    if ges_rente_vorauss_erwerbsm:
        out = (
            entgeltp_erwerbsm_rente
            * erwerbsm_rente_zugangsfaktor
            * rentenwert
            * rentenartfaktor
        )
    else:
        out = 0.0
    return out


def ges_rente_vorauss_erwerbsm(
    erwerbsgemindert: bool,
    m_pflichtbeitrag: float,
    ges_rente_wartezeit_5: bool,
) -> bool:
    """
    Eligibility for Erwerbsminderungsrente (public disability insurance claim).

    Legal reference: § 43 Abs. 1  SGB VI

    Parameters
    ----------
    erwerbsgemindert
        See basic input variable :ref:`erwerbsgemindert <erwerbsgemindert>.
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>.
    ges_rente_wartezeit_5
        See :func:`ges_rente_wartezeit_5`.
    Returns
    -------
    Eligibility for Erwerbsminderungsrente (public disability insurance claim) as a bool
    """

    anspruch_erwerbsm_rente = (
        erwerbsgemindert and ges_rente_wartezeit_5 and m_pflichtbeitrag >= 36
    )

    return anspruch_erwerbsm_rente


def entgeltp_erwerbsm_rente(
    entgeltp: float,
    durchschn_entgeltp: float,
    erwerbsm_rente_params: dict,
    age_of_retirement: float,
) -> float:
    """Entgeltpunkte which Erwerbsminderungsrente is based on
    (public disability insurance)
    In the case of the public disability insurance,
    pensioners are credited with additional earning points.
    They receive their average earned income points for
    each year between their age of retirement and the "zurechnungszeitsgrenze".

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>
    durchschn_entgeltp
        See :func:`durchschn_entgeltp`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.
    age_of_retirement
        See :func:`age_of_retirement`.

    Returns
    -------
    Final pension points for Erwerbsminderungsrente (public disability insurance)

    """
    zurechnungszeitsgrenze = erwerbsm_rente_params["zurechnungszeitsgrenze"]

    out = entgeltp + (
        (zurechnungszeitsgrenze - (age_of_retirement)) * durchschn_entgeltp
    )

    return out


def durchschn_entgeltp(
    entgeltp: float,
    age_of_retirement: float,
    erwerbsm_rente_params: dict,
) -> float:
    """Average earning points as part of the "Grundbewertung".
    Earnings points are divided by "belegungsfähige Gesamtzeitraum" which is
    the period from the age of 17 until the start of the pension.

    Legal reference: SGB VI § 72: Grundbewertung

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>
    age_of_retirement
        See :func:`age_of_retirement`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    average entgeltp
    """

    beleg_gesamtzeitr = (
        age_of_retirement - erwerbsm_rente_params["altersgrenze_grundbew"]
    )
    durchschn_entgeltp = entgeltp / beleg_gesamtzeitr

    return durchschn_entgeltp


def rentenartfaktor(
    teilw_erwerbsm_rente: bool,
    erwerbsm_rente_params: dict,
) -> float:
    """Rentenartfaktor for Erwerbsminderungsrente
    (public disability insurance)

    Legal reference: SGB VI § 67: Rentenartfaktor

    Parameters
    ----------
    teilw_erwerbsm_rente
        See basic input variable :ref:`teilw_erwerbsm_rente <teilw_erwerbsm_rente>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    Rentenartfaktor

    """

    if teilw_erwerbsm_rente:
        out = erwerbsm_rente_params["rentenartfaktor"]["teilw"]

    else:
        out = erwerbsm_rente_params["rentenartfaktor"]["voll"]

    return out


def erwerbsm_rente_zugangsfaktor(
    ges_rente_params: dict,
    erwerbsm_rente_params: dict,
    age_of_retirement: float,
    erwerbsm_rente_mit_63: bool,
) -> float:
    """Zugangsfaktor for Erwerbsminderungsrente
    (public disability insurance)
    For each month that a pensioner retires before the age limit, a fraction of
    the pension is deducted. The maximum deduction is capped.
    This max deduction is the norm for the public disability insurance.

    Legal reference: § 77 Abs. 2-4  SGB VI

    Paragraph 4 regulates an exceptional case in which pensioners can already
    retire at 63 without deductions if they can prove 35 or 40 years of
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
    erwerbsm_rente_mit_63
        See basic input variable :ref:`erwerbsm_rente_mit_63 <erwerbsm_rente_mit_63>.


    Returns
    -------
    Zugangsfaktor for Erwerbsminderungsrente (public disability insurance)

    """

    if erwerbsm_rente_mit_63:
        altersgrenze_abschlagsfrei = erwerbsm_rente_params[
            "altersgrenze_abschlagsfrei_63"
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
