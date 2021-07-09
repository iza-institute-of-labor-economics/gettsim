from typing import Dict

import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grundrentenzuschlag_m(
    grundrentenzuschlag_vor_einkommensanrechnung: FloatSeries,
    ges_renten_vers_params: dict,
    alleinstehend: BoolSeries,
    einkommen_grundr: FloatSeries,
    rentenwert: FloatSeries,
) -> FloatSeries:
    """ Implement income crediting rule as defined in Grundrentengesetz.

    There are upper and lower thresholds for singles and couples. 60% of income between
    the upper and lower threshold is credited against the Grundrentenzuschlag. All the
    income above the upper threshold is credited against the Grundrentenzuschlag.

    Parameters
    ----------
    grundrentenzuschlag_vor_einkommensanrechnung
        See :func:`grundrentenzuschlag_vor_einkommensanrechnung`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    alleinstehend
        See basic input variable :ref:`alleinstehend <alleinstehend>`.
    einkommen_alleinstehend_grundr
        See :func:`einkommen_alleinstehend_grundr`.
    einkommen_paar_grundr
        See :func:`einkommen_paar_grundr`.
    rentenwert
        See :func:`rentenwert`.

    Returns
    -------

    """
    out = (
        grundrentenzuschlag_vor_einkommensanrechnung
        - (
            einkommen_grundr.clip(
                upper=(
                    ges_renten_vers_params["einkommensanrechnung"]["upper"] * rentenwert
                )
            )
            - ges_renten_vers_params["einkommensanrechnung"]["lower"] * rentenwert
        ).clip(lower=0)
        * 0.6
        - (
            einkommen_grundr
            - (ges_renten_vers_params["einkommensanrechnung"]["upper"] * rentenwert)
        ).clip(lower=0)
    ).clip(lower=0)

    condition = ~alleinstehend

    out.loc[condition] = (
        grundrentenzuschlag_vor_einkommensanrechnung
        - (
            einkommen_grundr.clip(
                upper=(
                    ges_renten_vers_params["einkommensanrechnung"]["upper_ehe"]
                    * rentenwert
                )
            )
            - ges_renten_vers_params["einkommensanrechnung"]["lower_ehe"] * rentenwert
        ).clip(lower=0)
        * 0.6
        - (
            einkommen_grundr
            - (ges_renten_vers_params["einkommensanrechnung"]["upper_ehe"] * rentenwert)
        ).clip(lower=0)
    ).clip(lower=0)

    return out.round(2)


def grundrentenzuschlag_vor_einkommensanrechnung(
    bonus_entgeltpunkte_grundr: FloatSeries,
    grundrentenbewertungszeiten: IntSeries,
    rentenwert: FloatSeries,
    zugangsfaktor: FloatSeries,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """ Calculate additional monthly pensions payments resulting from
    Grundrente, without taking into account income crediting rules.

    According to the Grundrentengesetz, the Zugangsfaktor is limited to 1
    and considered Grundrentezeiten are limited to 35 years (420 months).
    Parameters
    ----------
    bonus_entgeltpunkte_grundr
        See :func:`bonus_entgeltpunkte_grundr`.
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
        bonus_entgeltpunkte_grundr
        * grundrentenbewertungszeiten.clip(
            upper=ges_renten_vers_params["grundrentenzeiten"]["max"]
        )
        * rentenwert
        * zugangsfaktor.clip(upper=1)
    )
    return out.round(2)


def durchschnittl_entgeltpunkte_grundr(
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


def höchstwert_grundr(
    grundrentenzeiten: IntSeries, ges_renten_vers_params: dict
) -> FloatSeries:
    """ Caluclates the maximum allowed number of average Entgeltpunkte (per month)
    after adding bonus of Entgeltpunkte for a given number of Grundrentenzeiten.

    Parameters
    ----------
    grundrentenzeiten
        See basic input variable :ref:`grundrentenzeiten <grundrentenzeiten>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

    Returns
    -------

    """
    return ges_renten_vers_params["höchstwert"]["base"] + ges_renten_vers_params[
        "höchstwert"
    ]["increment"] * (
        grundrentenzeiten.clip(upper=ges_renten_vers_params["grundrentenzeiten"]["max"])
        - ges_renten_vers_params["grundrentenzeiten"]["min"]
    ).round(
        4
    )


def bonus_entgeltpunkte_grundr(
    durchschnittl_entgeltpunkte_grundr: FloatSeries,
    höchstwert_grundr: FloatSeries,
    grundrentenzeiten: IntSeries,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """ Calculate additional Entgeltpunkte for pensioner.

    In general, the average of monthly Entgeltpunkte earend in Grundrentenzeiten is
    doubled, or extended to the individual Höchstwert if doubling would exceed the
    Höchstwert. Then, the value is always multiplied by 0.875.

    Parameters
    ----------
    durchschnittl_entgeltpunkte_grundr
        See :func:`durchschnittl_entgeltpunkte_grundr`.
    höchstwert_grundr
        See :func:`höchstwert_grundr`.
    grundrentenzeiten
        See basic input variable :ref:`grundrentenzeiten <grundrentenzeiten>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

    Returns
    -------

    """
    _cat1 = grundrentenzeiten < ges_renten_vers_params["grundrentenzeiten"]["min"]
    _cat2 = (
        grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten"]["min"]
    ) & (durchschnittl_entgeltpunkte_grundr <= (0.5 * höchstwert_grundr))
    _cat3 = (
        (grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten"]["min"])
        & (durchschnittl_entgeltpunkte_grundr >= (0.5 * höchstwert_grundr))
        & (durchschnittl_entgeltpunkte_grundr < höchstwert_grundr)
    )
    _cat4 = (
        grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten"]["min"]
    ) & (durchschnittl_entgeltpunkte_grundr > höchstwert_grundr)

    out = _cat1.astype(float) * np.nan
    out.loc[_cat1] = 0
    out.loc[_cat2] = durchschnittl_entgeltpunkte_grundr * (1 - 0.125)
    out.loc[_cat3] = (höchstwert_grundr - durchschnittl_entgeltpunkte_grundr) * (
        1 - 0.125
    )
    out.loc[_cat4] = 0
    return out


def einkommen_grundr(
    proxy_eink_vorj_arbeitsl_geld: FloatSeries,
    tu_id: IntSeries,
    brutto_eink_5_tu: FloatSeries,
    eink_st_abzuege_params: Dict,
    alleinstehend: BoolSeries,
) -> FloatSeries:
    """Aggreate income relevant for income crediting rule of Grundrentenzuschlag.
    Relevant income consists of pension payments and other taxable income of the
    previous year. The Grundrentenzuschlag itself is excluded.
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
    alleinstehend
        See basic input variable :ref:`alleinstehend <alleinstehend>`.
    Returns
    -------
    """
    # todo: estmimate pension payments of previous year
    out = (
        proxy_eink_vorj_arbeitsl_geld
        # + (ges_rente_m_tu_jahr_vorvergangen - zu_verst_ges_rente_tu_jahr_vorvergangen)
        + (brutto_eink_5_tu - eink_st_abzuege_params["sparerpauschbetrag"]).clip(
            lower=0
        )
    )

    out.loc[~alleinstehend] = (
        proxy_eink_vorj_arbeitsl_geld
        # + (tu_id.replace(ges_rente_m_tu_jahr_vorvergangen)
        # - tu_id.replace(zu_verst_ges_rente_tu_jahr_vorvergangen))
        + (
            tu_id.replace(brutto_eink_5_tu)
            - 2 * eink_st_abzuege_params["sparerpauschbetrag"]
        ).clip(lower=0)
    )

    return np.ceil(out)


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
    return grundrentenzeiten < ges_renten_vers_params["grundrentenzeiten"]["min"]


def freibetrag_grundsicherung_grundr(
    staatl_rente_m: FloatSeries,
    arbeitsl_geld_2_params: dict,
    nicht_grundrentenberechtigt: BoolSeries,
) -> FloatSeries:
    """ Compute allowance of Grundrente for Grundsicherung im Alter

    Parameters
    ----------
    staatl_rente_m
        See basic input variable :ref:`staatl_rente_m <staatl_rente_m>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    nicht_grundrentenberechtigt
        See :func:`nicht_grundrentenberechtigt`.


    Returns
    -------

    """
    out = (
        staatl_rente_m.clip(upper=100) + (staatl_rente_m - 100).clip(lower=0) * 0.3
    ).clip(upper=0.5 * arbeitsl_geld_2_params["regelsatz"][1])
    out.loc[nicht_grundrentenberechtigt] = 0
    return out
