from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import dates_active


def erwerbsm_rente_m(
    erwerbsm_rente_zugangsfaktor: float,
    entgeltp_erwerbsm_rente: float,
    rentenwert: float,
    rentenartfaktor_erwerbsm_rente: float,
    ges_rente_vorauss_erwerbsm: bool,
) -> float:
    """Calculating the Erwerbsminderungsrente pension claim

    Legal reference: SGB VI § 64: Rentenformel für Monatsbetrag der Rente


    Parameters
    ----------
    erwerbsm_rente_zugangsfaktor
        See :func:`erwerbsm_rente_zugangsfaktor`.
    entgeltp_erwerbsm_rente
        See :func:`entgeltp_erwerbsm_rente`.
    rentenwert
        See :func:`rentenwert`.
    rentenartfaktor_erwerbsm_rente
        See :func:`rentenartfaktor_erwerbsm_rente`.
    ges_rente_vorauss_erwerbsm
        See :func:`ges_rente_vorauss_erwerbsm`.
    Returns
    -------
    Erwerbsminderungsrente pension claim

    """

    if ges_rente_vorauss_erwerbsm:
        out = (
            entgeltp_erwerbsm_rente
            * erwerbsm_rente_zugangsfaktor
            * rentenwert
            * rentenartfaktor_erwerbsm_rente
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
    Determine eligibility Erwerbsminderungsrente
    (pension for reduced earning capacity)

    Requirements are:
    1 - not beeing able to work more than 3 hours per day (erwerbsgemindert)
    2 - beeing insured for at least 5 years (allgemeine Wartezeit)
    3 - having at least 3 years of mandatory contributions within the
        last 5 years before retirement (the function below is just checking if
        the amount of mandatory contribution months is high enough, not
        if they took place within the last 5 years)

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
    Erwerbsminderungsrente pension claim
    """

    anspruch_erwerbsm_rente = (
        erwerbsgemindert and ges_rente_wartezeit_5 and m_pflichtbeitrag >= 36
    )

    return anspruch_erwerbsm_rente


@dates_active(start="2004-01-01")
def entgeltp_erwerbsm_rente(
    entgeltp: float,
    durchschn_entgelpt: float,
    erwerbsm_rente_params: dict,
    jahr_renteneintr: int,
    age_of_retirement: float,
) -> float:
    """Calculating Entgeltpunkte for Erwerbsminderungsrente
    (pension for reduced earning capacity)
    In the case of a pension for reduced earning capacity,
    pensioners are credited with additional earning points.
    They receive their average earned income points for
    each year between their age of retirement and the "zurechnungszeitsgrenze".

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>
    durchschn_entgeltp_y
        See basic input variable :ref:`durchschn_entgeltp_y <durchschn_entgeltp_y>
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>.
    age_of_retirement
        See :func:`age_of_retirement`.

    Returns
    -------
    Final Entgeltpunkte for Erwerbsminderungsrente

    """
    zurechnungszeitsgrenze_params = erwerbsm_rente_params["zurechnungszeitsgrenze"]

    zurechnungszeitsgrenze = piecewise_polynomial(
        x=jahr_renteneintr,
        thresholds=zurechnungszeitsgrenze_params["thresholds"],
        rates=zurechnungszeitsgrenze_params["rates"],
        intercepts_at_lower_thresholds=zurechnungszeitsgrenze_params[
            "intercepts_at_lower_thresholds"
        ],
    )

    out = entgeltp + (
        (zurechnungszeitsgrenze - (age_of_retirement)) * durchschn_entgelpt
    )

    return out


@dates_active(end="2003-12-01", change_name="entgeltp_erwerbsm_rente")
def entgeltp_erwerbsm_rente_sonderregel(
    entgeltp: float,
    durchschn_entgelpt: float,
    erwerbsm_rente_params: dict,
    jahr_renteneintr: int,
    age_of_retirement: float,
) -> float:
    """Calculating Entgeltpunkte for Erwerbsminderungsrente
    (pension for reduced earning capacity) considering a special change in
    Zurechnungszeit from 2001-2003. Zurechnungszeitsgrenze is continually reduced
    by one month each month in this time period.

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>
    durchschn_entgelpt
        See :func:`durchschn_entgelpt`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>.
    age_of_retirement
        See :func:`age_of_retirement`.

    Returns
    -------
    Final Entgeltpunkte for Erwerbsminderungsrente

    """
    date_list = erwerbsm_rente_params["datum"].astype(str).split("-")
    diff_zu_2001 = (int(date_list[0]) - 2001) + (int(date_list[1]) - 1) / 12

    zurechnungszeitsgrenze_params = erwerbsm_rente_params["zurechnungszeitsgrenze"]

    zurechnungszeitsgrenze = piecewise_polynomial(
        x=jahr_renteneintr,
        thresholds=zurechnungszeitsgrenze_params["thresholds"],
        rates=zurechnungszeitsgrenze_params["rates"],
        intercepts_at_lower_thresholds=zurechnungszeitsgrenze_params[
            "intercepts_at_lower_thresholds"
        ],
    )

    out = entgeltp + (
        ((zurechnungszeitsgrenze - diff_zu_2001) - (age_of_retirement))
        * durchschn_entgelpt
    )
    return out


def durchschn_entgelpt(
    entgeltp: float,
    age_of_retirement: float,
) -> float:
    """Calculation of average earning points as part of the "Grundbewertung".
    Earnings points are divided by "belegungsfähige Gesamtzeitraum" which is
    the period from the age of 17 until the start of the pension.

    Legal reference: SGB VI § 72: Grundbewertung

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>
    age_of_retirement
        See :func:`age_of_retirement`.

    Returns
    -------
    average entgeltp
    """

    beleg_gesamtzeitr = age_of_retirement - 16
    durchschn_entgelpt = entgeltp / beleg_gesamtzeitr

    return durchschn_entgelpt


def rentenartfaktor_erwerbsm_rente(
    teilw_erwerbsm_rente: bool,
    erwerbsm_rente_params: dict,
) -> float:
    """Checking Rentenartfaktor for Erwerbsminderungsrente
    (pension for reduced earning capacity)

    Partial pension - Rentenartfaktor = 0.5
    Full pension - Rentenartfaktor = 1.0

    Legal reference: SGB VI § 67: Rentenartfaktor

    Parameters
    ----------
    teilw_erwerbsm_rente
        See basic input variable :ref:`teilw_erwerbsm_rente <teilw_erwerbsm_rente>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    Rentenfaktor

    """

    if teilw_erwerbsm_rente:
        out = erwerbsm_rente_params["rentenartfaktor_erwerbsm_rente"]["teilw"]

    else:
        out = erwerbsm_rente_params["rentenartfaktor_erwerbsm_rente"]["voll"]

    return out


def erwerbsm_rente_zugangsfaktor(
    ges_rente_params: dict,
    erwerbsm_rente_params: dict,
    age_of_retirement: float,
    jahr_renteneintr: int,
    erwerbsm_rente_mit_63: bool,
) -> float:
    """Calculating Zugangsfaktor for Erwerbsminderungsrente
    (pension for reduced earning capacity)
    For each month that a pensioner retires before the age limit, 0.3% of
    the pension is deducted. The maximum deduction is capped at 10.8%.
    This deduction is the norm for the pension for reduced earning capacity.

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
    jahr_renteneintr
        See :func:`jahr_renteneintr`.
    erwerbsm_rente_mit_63
        See basic input variable :ref:`erwerbsm_rente_mit_63 <erwerbsm_rente_mit_63>.


    Returns
    -------
    Zugangsfaktor for Erwerbsminderungsrente (pension for reduced earning capacity)

    """
    altersgrenze_abschlagsfrei_params = erwerbsm_rente_params[
        "altersgrenze_abschlagsfrei"
    ]

    if erwerbsm_rente_mit_63:
        altersgrenze_abschlagsfrei = erwerbsm_rente_params[
            "altersgrenze_abschlagsfrei_63"
        ]
    else:
        altersgrenze_abschlagsfrei = piecewise_polynomial(
            x=jahr_renteneintr,
            thresholds=altersgrenze_abschlagsfrei_params["thresholds"],
            rates=altersgrenze_abschlagsfrei_params["rates"],
            intercepts_at_lower_thresholds=altersgrenze_abschlagsfrei_params[
                "intercepts_at_lower_thresholds"
            ],
        )

    zugangsfaktor = 1 + (age_of_retirement - altersgrenze_abschlagsfrei) * (
        ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
            "vorzeitiger_renteneintritt"
        ]
    )
    out = max(zugangsfaktor, erwerbsm_rente_params["min_zugangsfaktor_erwerbsm_rente"])

    return out
