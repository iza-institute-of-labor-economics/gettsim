import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grundrentenzuschlag_m(
    grundrente_vor_einkommensanrechnung: FloatSeries,
    ges_renten_vers_params: dict,
    alleinstehend: BoolSeries,
    einkommen_alleinstehend: FloatSeries,
    einkommen_paar: FloatSeries,
    rentenwert: FloatSeries,
) -> FloatSeries:
    """ Implement income crediting rule as defined in Grundrentengesetz.

    Parameters
    ----------
    grundrente_vor_einkommensanrechnung
        See :func:`grundrente_vor_einkommensanrechnung`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    alleinstehend
        See basic input variable :ref:`alleinstehend <alleinstehend>`.
    einkommen_alleinstehend
        See :func:`einkommen_alleinstehend`.
    einkommen_paar
        See :func:`einkommen_paar`.
    rentenwert
        See :func:`rentenwert`.

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


def grundrente_vor_einkommensanrechnung(
    bonus_entgeltpunkte: FloatSeries,
    grundrentenbewertungszeiten: IntSeries,
    rentenwert: FloatSeries,
    zugangsfaktor: FloatSeries,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """ Calculate additional monthly pensions payments resulting from
    grundrente, before taking into account other income. According to
    the Grundrentengesetz, zugangsfaktor is limited to 1 for the
    Grundrentenzuschlag.

    Parameters
    ----------
    bonus_entgeltpunkte
        See :func:`bonus_entgeltpunkte`.
    grundrentenbewertungszeiten
        See basic input variable
        :ref:`grundrentenbewertungszeiten <grundrentenbewertungszeiten>`.
    rentenwert
        See :func:`rentenwert`.
    zugangsfaktor
        See :func:`zugangsfaktor`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

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


def durchschnittl_entgeltpunkte_grundrente(
    entgeltpunkte_grundrente: FloatSeries, grundrentenbewertungszeiten: IntSeries
) -> FloatSeries:
    """ Compute average number of Entgeltpunkte earned per month of Grundrentenzeiten.

    Parameters
    ----------
    entgeltpunkte_grundrente
        See basic input variable
        :ref:`entgeltpunkte_grundrente <entgeltpunkte_grundrente>`.
    grundrentenbewertungszeiten
        See basic input variable
        :ref:`grundrentenbewertungszeiten <grundrentenbewertungszeiten>`.

    Returns
    -------

    """
    return entgeltpunkte_grundrente / grundrentenbewertungszeiten


def höchstwert(
    grundrentenzeiten: IntSeries, ges_renten_vers_params: dict
) -> FloatSeries:
    """ Maximum  number of average Entgeltpunkte (per month)
    after adding bonus of Entgeltpunkte, only values > 33*12
    lead to useful results, lower values will still lead to
    correct final result, but höchstwert cannot be interpreted.

    Parameters
    ----------
    grundrentenzeiten
        See basic input variable :ref:`grundrentenzeiten <grundrentenzeiten>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

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
    durchschnittl_entgeltpunkte_grundrente: FloatSeries,
    höchstwert: FloatSeries,
    grundrentenzeiten: IntSeries,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """ Calculate additional Entgeltpunkte for person.

    Parameters
    ----------
    durchschnittl_entgeltpunkte_grundrente
        See :func:`durchschnittl_entgeltpunkte_grundrente`.
    höchstwert
        See :func:`höchstwert`.
    grundrentenzeiten
        See basic input variable :ref:`grundrentenzeiten <grundrentenzeiten>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

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


def einkommen_paar(
    zu_verst_eink_kinderfreib_tu: FloatSeries,
    ges_rente_m_tu: FloatSeries,
    zu_verst_ges_rente_tu: FloatSeries,
    brutto_eink_5_tu: FloatSeries,
    eink_st_abzuege_params: dict,
    tu_id,
) -> FloatSeries:
    """Aggreate income of couple relevant for income crediting rule of Grundrentenzuschlag.

    Parameters
    ----------
    zu_verst_eink_kinderfreib_tu
        See :func:`zu_verst_eink_kinderfreib_tu`.
    ges_rente_m_tu
        See :func:`ges_rente_m_tu`.
    zu_verst_ges_rente_tu
        See :func:`zu_verst_ges_rente_tu`.
    brutto_eink_5_tu
        See :func:`brutto_eink_5_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    out = (
        (1 / 12) * tu_id.replace(zu_verst_eink_kinderfreib_tu)
        + (tu_id.replace(ges_rente_m_tu) - tu_id.replace(zu_verst_ges_rente_tu))
        + (
            tu_id.replace(brutto_eink_5_tu)
            - 2 * eink_st_abzuege_params["sparerpauschbetrag"]
        ).clip(lower=0)
    )
    return out


def einkommen_alleinstehend(
    zu_verst_ges_rente: FloatSeries,
    zu_verst_eink_kinderfreib_tu: FloatSeries,
    ges_rente_m: FloatSeries,
    brutto_eink_5: FloatSeries,
    eink_st_abzuege_params: dict,
    tu_id: IntSeries,
) -> FloatSeries:
    """Aggreate income of single relevant for income crediting rule of Grundrentenzuschlag.

    Parameters
    ----------
    zu_verst_ges_rente
        See :func:`zu_verst_ges_rente`.
    zu_verst_eink_kinderfreib_tu
        See :func:`zu_verst_eink_kinderfreib_tu`.
    ges_rente_m
        See basic input variable :ref:`ges_rente_m <ges_rente_m>`.
    brutto_eink_5
        See :func:`brutto_eink_5`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    out = (
        (1 / 12) * tu_id.replace(zu_verst_eink_kinderfreib_tu)
        + (ges_rente_m - zu_verst_ges_rente)
        + (brutto_eink_5 - eink_st_abzuege_params["sparerpauschbetrag"]).clip(lower=0)
    )
    return out


def nicht_grundrentenberechtigt(
    grundrentenzeiten: IntSeries, ges_renten_vers_params: dict
) -> BoolSeries:
    """ Indicates that person is not entitled to Freibetragsregelung.

    Parameters
    ----------
    grundrentenzeiten
        See :func:`grundrentenzeiten`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

    Returns
    -------

    """
    return grundrentenzeiten < ges_renten_vers_params["grundrentenzeiten_lower"]


def freibetrag_grundsicherung_grundrente(
    ges_rente_m: FloatSeries,
    arbeitsl_geld_2_params: dict,
    nicht_grundrentenberechtigt: BoolSeries,
) -> FloatSeries:
    """ Compute allowance of Grundrente for Grundsicherung im Alter

    Parameters
    ----------
    ges_rente_m
        See basic input variable :ref:`ges_rente_m <ges_rente_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    nicht_grundrentenberechtigt
        See :func:`nicht_grundrentenberechtigt`.


    Returns
    -------

    """
    out = (ges_rente_m.clip(upper=100) + (ges_rente_m - 100).clip(lower=0) * 0.3).clip(
        upper=0.5 * arbeitsl_geld_2_params["regelsatz"][1]
    )
    out.loc[nicht_grundrentenberechtigt] = 0
    return out
