def durchschnittliche_entgeltp(
    entgeltp: float,
    m_pflichtbeitrag: float,
) -> float:
    """Calculating average Entgeltpunkte earned since starting to contribute
        to pensioninsurance per year
    Summe aus allen Beitrags und Berücksichtigungszeiten oder Input
    Anmerkung wie es berechnet wird
        Parameters
        ----------
        entgeltp

        m_pflichtbeitrag

        Returns
        -------
        Average Entgeldpunkte per year

    """
    out = entgeltp / (m_pflichtbeitrag / 12)

    return out


def entgeltp_fuer_erwerbsm_rente(
    entgeltp: float,
    durchschnittliche_entgeltp: float,
    erwerbsm_rente_params: dict,
    geburtsjahr: int,
    jahr_renteneintr: int,
) -> float:
    """Calculating Entgeltpunkte for Erwerbsminderungsrente

    Parameters
    ----------
    entgeltp

    durchschnittliche_entgeltp

    erwerbsm_rente_params

    geburtsjahr

    jahr_renteneintr

    Returns
    -------
    Average Entgeldpunkte per year

    """

    out = entgeltp + (
        (
            erwerbsm_rente_params["zurechnungszeitsgrenze_in_m"] / 12
            - (jahr_renteneintr - geburtsjahr)
        )
        * durchschnittliche_entgeltp
    )

    return out


def rentenfaktor_fuer_erwerbsm_rente(
    arbeitsstunden_w: float,
) -> float:
    """Calculating Rentenfaktor for Erwerbsminderungsrente
    based on the weekly working hours

    Als Input Variable
    Parameters
    ----------
    rentner

    arbeitsstunden_w

    Returns
    -------
    Rentenfaktor

    """

    if arbeitsstunden_w < 15:
        out = 1

    else:
        out = 0.5

    return out


def erwerbsm_rente_vor_grundr_m(
    ges_rente_zugangsfaktor: float,
    entgeltp_fuer_erwerbsm_rente: float,
    rentenwert: float,
    rentenfaktor_fuer_erwerbsm_rente: float,
    anspruch_erwerbsm_rente: bool,
) -> float:
    """Calculating the Erwerbsminderungsrente pension claim

    Parameters
    ----------
    ges_rente_zugangsfaktor

    entgeltp_fuer_erwerbsm_rente

    rentenwert

    rentenfaktor_fuer_erwerbsm_rente

    rentner

    Returns
    -------
    Erwerbsminderungsrente claim

    """

    if anspruch_erwerbsm_rente:
        out = (
            entgeltp_fuer_erwerbsm_rente
            * ges_rente_zugangsfaktor
            * rentenwert
            * rentenfaktor_fuer_erwerbsm_rente
        )
    else:
        out = 0.0

    return out


def erwerbsm_rente_altersgrenze(
    erwerbsm_rente_params: dict,
) -> float:
    """Calculating Altersgrenze for Erwerbsminderungsrente

    Parameters
    ----------
    erwerbsm_rente_params


    Returns
    -------
    Altersgrenze for Erwerbsminderungsrente

    """

    out = erwerbsm_rente_params["altersgrenze_abschlagsfrei_in_m"] / 12

    return out


def erwerbsm_rente_zugangsfaktor(
    jahr_renteneintr: int,
    geburtsjahr: int,
    erwerbsm_rente_altersgrenze: float,
    ges_rente_params: dict,
    erwerbsm_rente_params: dict,
) -> float:
    """ """
    zugangsfaktor = (
        1
        + ((jahr_renteneintr - geburtsjahr) - erwerbsm_rente_altersgrenze)
        * ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
            "vorzeitiger_renteneintritt"
        ]
    )
    out = min(zugangsfaktor, erwerbsm_rente_params["min_zugangsfaktor_erwerbsm_rente"])

    return out


def anspruch_erwerbsm_rente(
    alter: int,
    ges_rente_params: dict,
    rentner: bool,
) -> bool:
    """Function determining the elegibility for Erwerbsminderungsrente
    altersgrenze_langj_versicherte_vorzeitig =
    mindestalter für altersrente = 63

    Parameters
    ----------
    alter
    altersgrenze_langj_versicherte_vorzeitig

    Returns
    -------
    Eligibility as bool.

    """
    if rentner and alter < ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"]:
        out = True
    else:
        out = False

    return out
