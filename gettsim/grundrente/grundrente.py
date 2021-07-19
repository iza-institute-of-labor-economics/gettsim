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

    In general, the average of monthly Entgeltpunkte earnd in Grundrentenzeiten is
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
    wohnort_ost: BoolSeries,
    ges_renten_vers_params: Dict,
    prv_rente_m_vorj: FloatSeries,
    entgeltpunkte_update: FloatSeries,
) -> FloatSeries:
    """Aggreate income relevant for income crediting rule of Grundrentenzuschlag.
    Relevant income consists of pension payments and other taxable income of the
    previous year.
    Warning: The Grundrentenzuschlag itself is not considered at the moment.

    Parameters
    ----------
    proxy_eink_vorj_arbeitsl_geld
        See :func:`proxy_eink_vorj_arbeitsl_geld`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    brutto_eink_5_tu
        See :func:`brutto_eink_5_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    alleinstehend
        See basic input variable :ref:`alleinstehend <alleinstehend>`.
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    prv_rente_m_vorj
        See basic input variable :ref:`prv_rente_m_vorj <prv_rente_m_vorj>`.
    entgeltpunkte_update
        See :func:`entgeltpunkte_update`.
    Returns
    -------
    """

    rentenwert_vorjahr = wohnort_ost.replace(
        {
            True: ges_renten_vers_params["rentenwert_vorjahr"]["ost"],
            False: ges_renten_vers_params["rentenwert_vorjahr"]["west"],
        }
    ).astype(float)

    proxy_ges_rente_m_tu_vorj = (
        (entgeltpunkte_update * rentenwert_vorjahr + prv_rente_m_vorj)
        .groupby(tu_id)
        .sum()
    )
    proxy_eink_vorj_arbeitsl_geld_tu = proxy_eink_vorj_arbeitsl_geld.groupby(
        tu_id
    ).sum()

    out = (tu_id.replace(proxy_eink_vorj_arbeitsl_geld_tu)) + (
        tu_id.replace(proxy_ges_rente_m_tu_vorj)
        + (
            tu_id.replace(brutto_eink_5_tu)
            - eink_st_abzuege_params["sparerpauschbetrag"]
        ).clip(lower=0)
    )

    out.loc[~alleinstehend] = (tu_id.replace(proxy_eink_vorj_arbeitsl_geld_tu)) + (
        tu_id.replace(proxy_ges_rente_m_tu_vorj)
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
