from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import dates_active


@dates_active(start="2004-01-01")
def entgeltp_erwerbsm_rente(
    entgeltp: float,
    durchschn_entgeltp_y: float,
    erwerbsm_rente_params: dict,
    jahr_renteneintr: int,
    age_of_retirement: float,
) -> float:
    """Calculating Entgeltpunkte for Erwerbsminderungsrente
    (pension for reduced earning capacity)

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
        (m_zurechnungszeitsgrenze / 12 - (age_of_retirement)) * durchschn_entgeltp_y
    )

    return out


@dates_active(end="2003-12-01", change_name="entgeltp_erwerbsm_rente")
def entgeltp_erwerbsm_rente_sonderregel(
    entgeltp: float,
    durchschn_entgeltp_y: float,
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
    date_list = erwerbsm_rente_params["datum"].astype(str).split("-")
    m_diff_zu_2001 = (int(date_list[0]) - 2001) * 12 + (int(date_list[1]) - 1)

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
        (((m_zurechnungszeitsgrenze - m_diff_zu_2001) / 12) - (age_of_retirement))
        * durchschn_entgeltp_y
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
        out = 1.0

    return out


def erwerbsm_rente_m(
    erwerbsm_rente_zugangsfaktor: float,
    entgeltp_erwerbsm_rente: float,
    rentenwert: float,
    rentenfaktor_erwerbsm_rente: float,
    erwerbsm_rentner: bool,
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
    erwerbsm_rentner
        See basic input variable :ref:`erwerbsm_rentner <erwerbsm_rentner>.
    Returns
    -------
    Erwerbsminderungsrente pension claim

    """

    if erwerbsm_rentner:
        out = (
            entgeltp_erwerbsm_rente
            * erwerbsm_rente_zugangsfaktor
            * rentenwert
            * rentenfaktor_erwerbsm_rente
        )

    else:
        out = 0.0

    return out


def erwerbsm_rente_zugangsfaktor(
    erwerbsm_rente_params: dict,
    ges_rente_params: dict,
    age_of_retirement: float,
    jahr_renteneintr: int,
) -> float:
    """Calculating Zugangsfaktor for Erwerbsminderungsrente
    (pension for reduced earning capacity)

    Parameters
    ----------
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.
    age_of_retirement
        See :func:`age_of_retirement`.

    Returns
    -------
    Zugangsfaktor for Erwerbsminderungsrente (pension for reduced earning capacity)

    """
    altersgrenze_abschlagsfrei_params = erwerbsm_rente_params[
        "m_altersgrenze_abschlagsfrei"
    ]

    m_altersgrenze_abschlagsfrei = piecewise_polynomial(
        x=jahr_renteneintr,
        thresholds=altersgrenze_abschlagsfrei_params["thresholds"],
        rates=altersgrenze_abschlagsfrei_params["rates"],
        intercepts_at_lower_thresholds=altersgrenze_abschlagsfrei_params[
            "intercepts_at_lower_thresholds"
        ],
    )
    zugangsfaktor = 1 + (age_of_retirement - m_altersgrenze_abschlagsfrei / 12) * (
        ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
            "vorzeitiger_renteneintritt"
        ]
    )
    out = max(zugangsfaktor, erwerbsm_rente_params["min_zugangsfaktor_erwerbsm_rente"])

    return out
