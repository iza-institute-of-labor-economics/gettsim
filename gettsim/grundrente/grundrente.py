import numpy as np

from gettsim.typing import BoolSeries
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


def einkommen_paar(
    zu_verst_eink_kinderfreib_tu,
    ges_rente_m_tu,
    zu_verst_ges_rente_tu,
    brutto_eink_5_tu,
    eink_st_abzuege_params,
) -> FloatSeries:
    """Aggreate pension payments subject to taxation inn tax unit.

    Parameters
    ----------
    zu_verst_ges_rente
        See :func:`zu_verst_ges_rente`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    out = (
        (1 / 12) * zu_verst_eink_kinderfreib_tu
        + (ges_rente_m_tu - zu_verst_ges_rente_tu)
        + (brutto_eink_5_tu - 2 * eink_st_abzuege_params["sparerpauschbetrag"]).clip(
            lower=0
        )
    )
    return out


def einkommen_alleinstehend(
    zu_verst_ges_rente: FloatSeries,
    zu_verst_eink_kinderfreib_tu,
    ges_rente_m,
    brutto_eink_5,
    eink_st_abzuege_params,
):
    out = (
        (1 / 12) * zu_verst_eink_kinderfreib_tu
        + (ges_rente_m - zu_verst_ges_rente)
        + (brutto_eink_5 - eink_st_abzuege_params["sparerpauschbetrag"]).clip(lower=0)
    )
    return out


def grundrentenzuschlag_m(
    grundrente_vor_einkommensanrechnung,
    ges_renten_vers_params: dict,
    alleinstehend: BoolSeries,
    einkommen_alleinstehend,
    einkommen_paar,
    rentenwert,
) -> FloatSeries:
    """ Implement income crediting rule as defined in Grundrentengesetz.

    Parameters
    ----------
    grundrente_vor_einkommensanrechnung
    bruttolohn_m
    rente_anspr_m
    Returns
    -------

    """
    out = grundrente_vor_einkommensanrechnung - (
        (
            einkommen_alleinstehend.clip(
                upper=(
                    ges_renten_vers_params["einkommensanrechnung_upper"] * rentenwert
                )
            )
            - (ges_renten_vers_params["einkommensanrechnung_lower"] * rentenwert)
        ).clip(lower=0)
        * 0.6
        - (
            einkommen_alleinstehend
            - (ges_renten_vers_params["einkommensanrechnung_upper"] * rentenwert)
        ).clip(lower=0)
    ).clip(lower=0)

    condition = ~alleinstehend

    out.loc[condition] = grundrente_vor_einkommensanrechnung - (
        (
            einkommen_paar.clip(
                upper=(
                    ges_renten_vers_params["einkommensanrechnung_upper_ehe"]
                    * rentenwert
                )
            )
            - (ges_renten_vers_params["einkommensanrechnung_lower_ehe"] * rentenwert)
        ).clip(lower=0)
        * 0.6
        - (
            einkommen_paar
            - (ges_renten_vers_params["einkommensanrechnung_upper_ehe"] * rentenwert)
        ).clip(lower=0)
    ).clip(lower=0)
    return out


def nicht_grundrentenberechtigt(grundrentenzeiten, ges_renten_vers_params: dict):
    """ Indicates that person is not entitled to Freibetragsregelung.

    Parameters
    ----------

    grundrentenzeiten

    Returns
    -------

    """
    return grundrentenzeiten < ges_renten_vers_params["grundrentenzeiten_lower"]


def freibetrag_grundsicherung_grundrente(
    ges_rente_m, arbeitsl_geld_2_params, nicht_grundrentenberechtigt
):
    out = (ges_rente_m.clip(upper=100) + (ges_rente_m - 100).clip(lower=0) * 0.3).clip(
        upper=0.5 * arbeitsl_geld_2_params["regelsatz"][1]
    )
    out.loc[nicht_grundrentenberechtigt] = 0
    return out
