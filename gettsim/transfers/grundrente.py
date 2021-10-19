import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grundrentenzuschlag_m(
    grundrentenzuschlag_vor_einkommensanrechnung: FloatSeries,
    ges_renten_vers_params: dict,
    alleinstehend_grundr: BoolSeries,
    einkommen_grundr_tu: FloatSeries,
    rentenwert: FloatSeries,
    tu_id: IntSeries,
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
    alleinstehend_grundr
        See :func:`alleinstehend_grundr`.
    einkommen_grundr_tu
        See :func:`einkommen_grundr_tu`.
    rentenwert
        See :func:`rentenwert`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    Returns
    -------

    """
    # Select correct thresholds of income crediting rule.
    einkommensanrechnung_upper = alleinstehend_grundr.replace(
        {
            True: ges_renten_vers_params["einkommensanrechnung_gr"]["upper"],
            False: ges_renten_vers_params["einkommensanrechnung_gr"]["upper_ehe"],
        }
    ).astype(float)

    einkommensanrechnung_lower = alleinstehend_grundr.replace(
        {
            True: ges_renten_vers_params["einkommensanrechnung_gr"]["lower"],
            False: ges_renten_vers_params["einkommensanrechnung_gr"]["lower_ehe"],
        }
    ).astype(float)

    # Deduct income from Grundrentenzuschlag following the crediting rules.
    einkommen_grundr = tu_id.replace(einkommen_grundr_tu)
    out = (
        grundrentenzuschlag_vor_einkommensanrechnung
        - (
            einkommen_grundr.clip(upper=(einkommensanrechnung_upper * rentenwert))
            - einkommensanrechnung_lower * rentenwert
        ).clip(lower=0)
        * 0.6
        - (einkommen_grundr - (einkommensanrechnung_upper * rentenwert)).clip(lower=0)
    ).clip(lower=0)

    return out.round(2)


def grundrentenzuschlag_vor_einkommensanrechnung(
    bonus_entgeltpunkte_grundr: FloatSeries,
    gr_bewertungszeiten: IntSeries,
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
    gr_bewertungszeiten
        See basic input variable
        :ref:`gr_bewertungszeiten <gr_bewertungszeiten>`.
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
        * gr_bewertungszeiten.clip(
            upper=ges_renten_vers_params["grundrentenzeiten"]["max"]
        )
        * rentenwert
        * zugangsfaktor.clip(upper=1)
    )
    return out.round(2)


def durchschnittl_entgeltpunkte_grundr(
    entgeltpunkte_grundrente: FloatSeries, gr_bewertungszeiten: IntSeries
) -> FloatSeries:
    """ Compute average number of Entgeltpunkte earned per month of Grundrentenzeiten.

    Parameters
    ----------
    entgeltpunkte_grundrente
        See basic input variable
        :ref:`entgeltpunkte_grundrente <entgeltpunkte_grundrente>`.
    gr_bewertungszeiten
        See basic input variable
        :ref:`gr_bewertungszeiten <gr_bewertungszeiten>`.

    Returns
    -------

    """
    return entgeltpunkte_grundrente / gr_bewertungszeiten


def höchstwert_grundr_m(
    grundrentenzeiten: IntSeries, ges_renten_vers_params: dict
) -> FloatSeries:
    """ Calculates the maximum allowed number of average Entgeltpunkte (per month)
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

    # Calculate number of months above minimum threshold
    months_above_thresh = (
        grundrentenzeiten.clip(upper=ges_renten_vers_params["grundrentenzeiten"]["max"])
        - ges_renten_vers_params["grundrentenzeiten"]["min"]
    )

    # Calculate höchstwert
    out = (
        ges_renten_vers_params["höchstwert_gr"]["base"]
        + ges_renten_vers_params["höchstwert_gr"]["increment"] * months_above_thresh
    )

    # Round to 4 digits
    return out.round(4)


def bonus_entgeltpunkte_grundr(
    durchschnittl_entgeltpunkte_grundr: FloatSeries,
    höchstwert_grundr_m: FloatSeries,
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
    höchstwert_grundr_m
        See :func:`höchstwert_grundr_m`.
    grundrentenzeiten
        See basic input variable :ref:`grundrentenzeiten <grundrentenzeiten>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

    Returns
    -------

    """
    # Categories for distinct cases
    _cat1 = grundrentenzeiten < ges_renten_vers_params["grundrentenzeiten"]["min"]
    _cat2 = (
        grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten"]["min"]
    ) & (durchschnittl_entgeltpunkte_grundr <= (0.5 * höchstwert_grundr_m))
    _cat3 = (
        (grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten"]["min"])
        & (durchschnittl_entgeltpunkte_grundr >= (0.5 * höchstwert_grundr_m))
        & (durchschnittl_entgeltpunkte_grundr < höchstwert_grundr_m)
    )
    _cat4 = (
        grundrentenzeiten >= ges_renten_vers_params["grundrentenzeiten"]["min"]
    ) & (durchschnittl_entgeltpunkte_grundr > höchstwert_grundr_m)

    # Apply rule to compute bonus for each category
    out = _cat1.astype(float) * np.nan
    out.loc[_cat1] = 0
    out.loc[_cat2] = durchschnittl_entgeltpunkte_grundr * (1 - 0.125)
    out.loc[_cat3] = (höchstwert_grundr_m - durchschnittl_entgeltpunkte_grundr) * (
        1 - 0.125
    )
    out.loc[_cat4] = 0
    return out


def einkommen_grundr(
    proxy_eink_vorj: FloatSeries,
    brutto_eink_5: FloatSeries,
    eink_st_abzuege_params: dict,
    wohnort_ost: BoolSeries,
    ges_renten_vers_params: dict,
    prv_rente_m_vorj: FloatSeries,
    entgeltpunkte_update: FloatSeries,
) -> FloatSeries:
    """Income relevant for income crediting rule of Grundrentenzuschlag.
    Relevant income consists of pension payments and other taxable income of the
    previous year.
    Warning: The Grundrentenzuschlag itself is not considered at the moment.

    #ToDo: Needs to adjust this once we cleared up the meaning of tax unit. Only
    #ToDo: the income of married partners should be considered.

    Parameters
    ----------
    proxy_eink_vorj
        See :func:`proxy_eink_vorj`.
    brutto_eink_5
        See :func:`brutto_eink_5`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
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

    # Estimate amount of pensions of last year using rentenwert of previous year.
    # Zugangsfaktor and Grundrentenzuschlag are omitted.
    proxy_gesamte_rente_m_vorj = (
        entgeltpunkte_update * rentenwert_vorjahr + prv_rente_m_vorj
    )

    # Sum up components of income: earnings, pension, capital income
    out = (
        proxy_eink_vorj
        + proxy_gesamte_rente_m_vorj
        + (brutto_eink_5 - eink_st_abzuege_params["sparerpauschbetrag"]).clip(lower=0)
    )

    return np.ceil(out)


def einkommen_grundr_tu(einkommen_grundr: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate income relevant for Grundrentenzuschlag on tax unit level.

    Parameters
    ----------
    einkommen_grundr
        See :func:`einkommen_grundr`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return einkommen_grundr.groupby(tu_id).sum()


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


def alleinstehend_grundr(anz_erwachsene_tu: IntSeries, tu_id: IntSeries) -> BoolSeries:
    """ Indicates whether pensioner is single based on number of adults in the tax unit.

    Parameters
    ----------
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.

    Returns
    -------

    """
    return tu_id.replace(anz_erwachsene_tu < 2)
