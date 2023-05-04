def durchschnittliche_entgeltp(
    entgeltp: float,
    m_beitragszeit: int,
) -> float:
    """Calculating average Entgeltpunkte for Erwerbminderungsrente
    (pension for reduced earning capacity)
    m_beitragszeit = Summe aus vollwertigen Beitragszeiten,
    beitragsgeminderten Zeiten, Anrechnungszeiten, Zurechnungszeiten
    und Ersatzzeiten.

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>.
    m_beitragszeit
        See basic input variable :ref:`m_beitragszeit <m_beitragszeit>.

    Returns
    -------
    Average Entgeldpunkte per year

    """
    out = entgeltp / (m_beitragszeit / 12)
    return out


def entgeltp_erwerbsm_rente(
    entgeltp: float,
    durchschnittliche_entgeltp: float,
    erwerbsm_rente_params: dict,
    geburtsjahr: int,
    jahr_renteneintr: int,
) -> float:
    """Calculating Entgeltpunkte for Erwerbsminderungsrente
    (pension for reduced earning capacity)

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>
    durchschnittliche_entgeltp
        See :func:`durchschnittliche_entgeltp`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>.

    Returns
    -------
    Final Entgeltpunkte for Erwerbsminderungsrente

    """

    out = entgeltp + (
        (
            erwerbsm_rente_params["zurechnungszeitsgrenze_in_m"] / 12
            - (jahr_renteneintr - geburtsjahr)
        )
        * durchschnittliche_entgeltp
    )

    return out


def rentenfaktor_erwerbsm_rente(
    teilw_erwerbsm_rente: bool,
) -> float:
    """Checking Rentenfaktor for Erwerbsminderungsrente
    (pension for reduced earning capacity)
    based on input variable teilw_erwerbsm_rente

    Als Input Variable
    Parameters
    ----------
    teilw_erwerbsm_rente
        See basic input variable :ref:`teilw_erwerbsm_rente <teilw_erwerbsm_rente>.

    Returns
    -------
    Rentenfaktor

    """

    if teilw_erwerbsm_rente:
        out = 0.5

    else:
        out = 1

    return out


def erwerbsm_rente_vor_grundr_m(
    erwerbsm_rente_zugangsfaktor: float,
    entgeltp_erwerbsm_rente: float,
    rentenwert: float,
    rentenfaktor_erwerbsm_rente: float,
    anspruch_erwerbsm_rente: bool,
) -> float:
    """Calculating the Erwerbsminderungsrente pension claim

    Parameters
    ----------
    ges_rente_zugangsfaktor
        See :func:`ges_rente_zugangsfaktor`.
    entgeltp_fuer_erwerbsm_rente
        See :func:`entgeltp_fuer_erwerbsm_rente`.
    rentenwert
        See :func:`rentenwert`.
    rentenfaktor_fuer_erwerbsm_rente
        See :func:`rentenfaktor_fuer_erwerbsm_rente`.
    rentner
        See basic input variable :ref:`rentner <rentner>.
    Returns
    -------
    Erwerbsminderungsrente pension claim

    """

    if anspruch_erwerbsm_rente:
        out = (
            entgeltp_erwerbsm_rente
            * erwerbsm_rente_zugangsfaktor
            * rentenwert
            * rentenfaktor_erwerbsm_rente
        )
    else:
        out = 0.0

    return out


def erwerbsm_rente_altersgrenze(
    erwerbsm_rente_params: dict,
) -> float:
    """Calculating Altersgrenze for Erwerbsminderungsrente
    (pension for reduced earning capacity)

    Parameters
    ----------
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

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
    """Calculating Zugangsfaktor for Erwerbsminderungsrente
    (pension for reduced earning capacity)

    Parameters
    ----------
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>.
    erwerbsm_rente_altersgrenze
        See :func:`erwerbsm_rente_altersgrenze`
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    Zugangsfaktor for Erwerbsminderungsrente (pension for reduced earning capacity)

    """
    zugangsfaktor = (
        1
        + ((jahr_renteneintr - geburtsjahr) - erwerbsm_rente_altersgrenze)
        * ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
            "vorzeitiger_renteneintritt"
        ]
    )
    out = max(zugangsfaktor, erwerbsm_rente_params["min_zugangsfaktor_erwerbsm_rente"])

    return out


def anspruch_erwerbsm_rente(
    alter: int,
    ges_rente_params: dict,
    rentner: bool,
) -> bool:
    """Function determining the elegibility for Erwerbsminderungsrente
    altersgrenze_langj_versicherte_vorzeitig =
    mindestalter für altersrente = 63

    This function is not completely accurate yet as individuals above age 63
    can still claim reduced earnings capacity if they are below the
    (Regelaltersgrenze)

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>.
    rentner
        See basic input variable :ref:`rentner <rentner>.

    Returns
    -------
    Eligibility for Erwerbsminderungsrente as bool.

    """
    if rentner and alter < ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"]:
        out = True
    else:
        out = False

    return out
