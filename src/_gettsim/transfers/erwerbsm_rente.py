from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import dates_active


def durchschnittliche_entgeltp(
    entgeltp: float,
    m_gesamtbew: int,
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
        See basic input variable :ref:`m_gesamtbew <m_gesamtbew>.

    Returns
    -------
    Average Entgeldpunkte per year

    """
    out = entgeltp / (m_gesamtbew / 12)
    return out


@dates_active(start="2004-01-01")
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
    zurechnungszeitsgrenze_params = erwerbsm_rente_params["m_zurechnungszeitsgrenze"]

    m_zurechnungszeitsgrenze = piecewise_polynomial(
        x=jahr_renteneintr,
        thresholds=zurechnungszeitsgrenze_params["thresholds"],
        rates=zurechnungszeitsgrenze_params["rates"],
        intercepts_at_lower_thresholds=zurechnungszeitsgrenze_params[
            "intercepts_at_lower_thresholds"
        ],
    )

    out = entgeltp + (
        (m_zurechnungszeitsgrenze / 12 - (jahr_renteneintr - geburtsjahr))
        * durchschnittliche_entgeltp
    )
    return out


@dates_active(end="2003-12-01", change_name="entgeltp_erwerbsm_rente")
def entgeltp_erwerbsm_rente_sonderregel(
    entgeltp: float,
    durchschnittliche_entgeltp: float,
    erwerbsm_rente_params: dict,
    geburtsjahr: int,
    jahr_renteneintr: int,
) -> float:
    """Calculating Entgeltpunkte for Erwerbsminderungsrente
    (pension for reduced earning capacity) considering a special change in
    Zurechnungszeit from 2001-2003. Zurechnungszeitsgrenze is continually reduced
    by one month each month in this time period.

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
    date_list = erwerbsm_rente_params["datum"].astype(str).split("-")
    diff_zu_2001_in_m = (int(date_list[0]) - 2001) * 12 + (int(date_list[1]) - 1)

    zurechnungszeitsgrenze_params = erwerbsm_rente_params["m_zurechnungszeitsgrenze"]

    m_zurechnungszeitsgrenze = piecewise_polynomial(
        x=jahr_renteneintr,
        thresholds=zurechnungszeitsgrenze_params["thresholds"],
        rates=zurechnungszeitsgrenze_params["rates"],
        intercepts_at_lower_thresholds=zurechnungszeitsgrenze_params[
            "intercepts_at_lower_thresholds"
        ],
    )

    out = entgeltp + (
        (
            ((m_zurechnungszeitsgrenze - diff_zu_2001_in_m) / 12)
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


@dates_active(end="2020-12-31")
def erwerbsm_rente_m(erwerbsm_rente_vor_grundr_m: float) -> float:
    return erwerbsm_rente_vor_grundr_m


@dates_active(start="2021-01-01", change_name="erwerbsm_rente_m")
def erwerbsm_rente_nach_grundr_m(
    erwerbsm_rente_vor_grundr_m: float,
    grundr_zuschlag_m: float,
) -> float:
    """Calculate total individual Erwerbsminderunsrente including
    Grundrentenzuschlag. Is only active after 2021 when Grundrente
    is in place.

    Parameters
    ----------
    erwerbsm_rente_vor_grundr_m
        See :func:`erwerbsm_rente_vor_grundr_m`.
    grundr_zuschlag_m
        See :func:`grundr_zuschlag_m`.

    Returns
    -------

    """

    out = erwerbsm_rente_vor_grundr_m + grundr_zuschlag_m

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
    Altersgrenze for Erwerbsminderungsrente in month

    """

    out = erwerbsm_rente_params["m_altersgrenze_abschlagsfrei"]
    return out


def erwerbsm_rente_zugangsfaktor(  # noqa: PLR0913
    jahr_renteneintr: int,
    geburtsjahr: int,
    geburtsmonat: int,
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
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>.
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
    m_alter_renteneintr = (jahr_renteneintr - geburtsjahr) * 12 + geburtsmonat
    zugangsfaktor = 1 + (m_alter_renteneintr - erwerbsm_rente_altersgrenze) * (
        ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
            "vorzeitiger_renteneintritt"
        ]
        / 12
    )
    out = max(zugangsfaktor, erwerbsm_rente_params["min_zugangsfaktor_erwerbsm_rente"])

    return out


def anspruch_erwerbsm_rente(
    erwerbsm_rentner: bool,
) -> bool:
    """Function determining the elegibility for Erwerbsminderungsrente


    Not sure yet if the elegibility should come as an input variable or if it
    should be determined with other variables

    Parameters
    ----------
    erwerbsm_rentner
        See basic input variable :ref:`erwerbsm_rentner <erwerbsm_rentner>.

    Returns
    -------
    Eligibility for Erwerbsminderungsrente as bool.

    """
    if erwerbsm_rentner is True:
        out = True
    else:
        out = False

    return out
