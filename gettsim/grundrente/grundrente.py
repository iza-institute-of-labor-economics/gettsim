import numpy as np

from gettsim.typing import FloatSeries


def durchschnittl_entgeltpunkte_grundrente(
    entgeltpunkte_grundrente, grundrentenbewertungszeiten
):
    """ Compute average number of Entgeltpunkte earned per month of Grundrentenzeiten.
    necessary that Grundrentenbewertungszeiten > 0

    Parameters
    ----------
    entgeltpunkte_grundrente
    grundrentenbewertungszeiten

    Returns
    -------

    """
    return entgeltpunkte_grundrente / grundrentenbewertungszeiten


def höchstwert(grundrentenzeiten, ges_renten_vers_params: dict):
    """ Maximum  number of average Entgeltpunkte (per month)
    after adding bonus of Entgeltpunkte, only values > 33*12
    lead to useful results, lower values will still lead to
    correct final result, but höchstwert cannot be interpreted

    Parameters
    ----------
    grundrentenzeiten

    Returns
    -------

    """
    return ges_renten_vers_params["höchstwert_base"] + ges_renten_vers_params[
        "höchstwert_increment"
    ] * (
        grundrentenzeiten.clip(upper=ges_renten_vers_params["grundrentenzeiten_upper"])
        - ges_renten_vers_params["grundrentenzeiten_lower"]
    ).round(
        4
    )


def bonus_entgeltpunkte(
    durchschnittl_entgeltpunkte_grundrente,
    höchstwert,
    grundrentenzeiten,
    ges_renten_vers_params: dict,
):
    """ Calculate additional Entgeltpunkte for person.

    Parameters
    ----------
    _kat1
    _kat2
    _kat3
    _kat4
    durchschnittl_entgeltpunkte_grundrente
    höchstwert

    Returns
    -------

    """
    _cat1 = grundrentenzeiten < ges_renten_vers_params["grundrentenzeiten_lower"]
    _cat2 = (grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten_lower"]) & (
        durchschnittl_entgeltpunkte_grundrente <= (0.5 * höchstwert)
    )
    _cat3 = (
        (grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten_lower"])
        & (durchschnittl_entgeltpunkte_grundrente >= (0.5 * höchstwert))
        & (durchschnittl_entgeltpunkte_grundrente < höchstwert)
    )
    _cat4 = (grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten_lower"]) & (
        durchschnittl_entgeltpunkte_grundrente > höchstwert
    )

    out = _cat1.astype(float) * np.nan
    out.loc[_cat1] = 0
    out.loc[_cat2] = durchschnittl_entgeltpunkte_grundrente * (1 - 0.125)
    out.loc[_cat3] = (höchstwert - durchschnittl_entgeltpunkte_grundrente) * (1 - 0.125)
    out.loc[_cat4] = 0
    return out


def grundrente_vor_einkommensanrechnung(
    bonus_entgeltpunkte,
    grundrentenbewertungszeiten,
    rentenwert,
    zugangsfaktor,
    ges_renten_vers_params: dict,
):
    """ Calculate additional monthly pensions payments resulting from
    grundrente, before taking into account other income. According to
    the Grundrentengesetz, zugangsfaktor is limited to 1 for the
    Grundrentenzuschlag.
    Parameters
    ----------
    bonus_entgeltpunkte
    grundrentenbewertungszeiten
    rentenwert
    zugangsfaktor


    Returns
    -------

    """
    out = (
        bonus_entgeltpunkte
        * grundrentenbewertungszeiten.clip(
            upper=ges_renten_vers_params["grundrentenzeiten_upper"]
        )
        * rentenwert
        * zugangsfaktor.clip(upper=1)
    )
    return out


def grundrente1(
    grundrente_vor_einkommensanrechnung,
    bruttolohn_m,
    rente_anspr_m,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """ Implement income crediting rule as defined in Grundrentengesetz.
    Assumption for now: only other income is bruttolohn_m and
    rente_anspr_m.

    Parameters
    ----------
    grundrente_vor_einkommensanrechnung
    bruttolohn_m
    rente_anspr_m
    Returns
    -------

    """
    out = (
        grundrente_vor_einkommensanrechnung
        - (
            (
                (bruttolohn_m + rente_anspr_m).clip(
                    upper=ges_renten_vers_params["einkommensanrechnung_upper"]
                )
                - ges_renten_vers_params["einkommensanrechnung_lower"]
            ).clip(lower=0)
        )
        * 0.6
        - (
            (bruttolohn_m + rente_anspr_m)
            - ges_renten_vers_params["einkommensanrechnung_upper"]
        ).clip(lower=0)
    ).clip(lower=0)
    return out


def grundrentenberechtigt(grundrentenzeiten, ges_renten_vers_params: dict):
    """ Indicates that person is entitled to Freibetragsregelung.

    Parameters
    ----------

    grundrentenzeiten

    Returns
    -------

    """
    return grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten_lower"]


def nicht_grundrentenberechtigt(grundrentenzeiten, ges_renten_vers_params: dict):
    """ Indicates that person is not entitled to Freibetragsregelung.

    Parameters
    ----------

    grundrentenzeiten

    Returns
    -------

    """
    return grundrentenzeiten < ges_renten_vers_params["grundrentenzeiten_lower"]


def anzurechnende_rente(
    rente_anspr_m,
    grundrente1,
    grundrentenberechtigt,
    nicht_grundrentenberechtigt,
    bruttolohn_m,
):
    """ Implement allowance for grundsicherung im alter.


    Parameters
    ----------
   rente_anspr_m
   grundrente1
   grundrentenberechtigt
   nicht_grundrentenberechtigt
   bruttolohn_m

    Returns
    -------

    """
    gesamtrente = rente_anspr_m + grundrente1 + bruttolohn_m

    out = grundrentenberechtigt.astype(float) * np.nan
    out.loc[nicht_grundrentenberechtigt] = gesamtrente
    out.loc[grundrentenberechtigt] = (
        gesamtrente - (100 + (gesamtrente - 100) * 0.3).clip(upper=0.5 * 432)
    ).clip(lower=0)
    return out


def grundsicherung_berechtigt(anzurechnende_rente):
    """ Indicates that person is entitled to Grundsicherung.

    Parameters
    ----------

    anzurechnende_rente

    Returns
    -------

    """
    return anzurechnende_rente < 932


def grundsicherung_nicht_berechtigt(anzurechnende_rente):
    """ Indicates that person is not entitled to Grundsicherung.

    Parameters
    ----------

    anzurechnende_rente

    Returns
    -------

    """
    return anzurechnende_rente >= 932


def grundsicherung(
    grundsicherung_berechtigt, grundsicherung_nicht_berechtigt, anzurechnende_rente
):
    """ Compute monthly payments of Grundsicherung

    Parameters
    ----------

    grundsicherung_berechtigt
    grundsicherung_nicht_berechtigt
    anzurechnende_rente

    Returns
    -------

    """
    out = grundsicherung_berechtigt.astype(float) * np.nan
    out.loc[grundsicherung_nicht_berechtigt] = 0
    out.loc[grundsicherung_berechtigt] = 932 - anzurechnende_rente

    return out


def grundsicherung_im_alter_2020(rente_anspr_m):
    out = ((432 + 500) - rente_anspr_m).clip(lower=0)
    return out
