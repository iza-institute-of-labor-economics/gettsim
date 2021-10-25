import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grundr_zuschlag_m(
    grundr_zuschlag_vor_eink_anr_m: FloatSeries,
    reduktion_angerechnetes_eink_gr_m: FloatSeries,
) -> FloatSeries:
    """Calculate Grundrentenzuschlag (additional monthly pensions payments
    resulting from Grundrente)

    Parameters
    ----------
    grundr_zuschlag_vor_eink_anr_m
        See :func:`grundr_zuschlag_vor_eink_anr_m`.
    reduktion_angerechnetes_eink_gr_m
        See :func:`reduktion_angerechnetes_eink_gr_m`.

    Returns
    -------

    """
    out = grundr_zuschlag_vor_eink_anr_m - reduktion_angerechnetes_eink_gr_m
    return out.clip(lower=0).round(2)


def reduktion_angerechnetes_eink_gr_m(
    ges_renten_vers_params: dict,
    alleinstehend_grundr: BoolSeries,
    zu_verst_eink_excl_grundr_zuschlag_m_tu: FloatSeries,
    rentenwert: FloatSeries,
    tu_id: IntSeries,
) -> FloatSeries:
    """Calculate reduction of Grundrentenzuschlag through income offsetting.

    Implement income crediting rule as defined in Grundrentengesetz.

    There are upper and lower thresholds for singles and couples. 60% of income between
    the upper and lower threshold is credited against the Grundrentenzuschlag. All the
    income above the upper threshold is credited against the Grundrentenzuschlag.

    Parameters
    ----------
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    alleinstehend_grundr
        See :func:`alleinstehend_grundr`.
    zu_verst_eink_excl_grundr_zuschlag_m_tu
        See :func:`zu_verst_eink_excl_grundr_zuschlag_m_tu`.
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
    upper = einkommensanrechnung_upper * rentenwert
    lower = einkommensanrechnung_lower * rentenwert

    # Calculate deducted income following the crediting rules.
    einkommen_grundr = tu_id.replace(zu_verst_eink_excl_grundr_zuschlag_m_tu)
    einkommen_btw_upper_lower = (einkommen_grundr.clip(upper=upper) - lower).clip(
        lower=0
    )
    einkommen_above_upper = (einkommen_grundr - upper).clip(lower=0)

    out = einkommen_btw_upper_lower * 0.6 + einkommen_above_upper

    return out.round(2)


def grundr_zuschlag_vor_eink_anr_m(
    bonus_entgeltpunkte_grundr: FloatSeries,
    gr_bewertungszeiten: IntSeries,
    rentenwert: FloatSeries,
    zugangsfaktor: FloatSeries,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """Calculate additional monthly pensions payments resulting from
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
    """Compute average number of Entgeltpunkte earned per month of Grundrentenzeiten.

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
    """Calculates the maximum allowed number of average Entgeltpunkte (per month)
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
    """Calculate additional Entgeltpunkte for pensioner.

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


def zu_verst_eink_excl_grundr_zuschlag_m_tu(
    zu_verst_eink_excl_grundr_zuschlag_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate the income relevant for income crediting rule of
    Grundrentenzuschlag on tax unit level.

    Parameters
    ----------
    zu_verst_eink_excl_grundr_zuschlag_m
        See :func:`zu_verst_eink_excl_grundr_zuschlag_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return zu_verst_eink_excl_grundr_zuschlag_m.groupby(tu_id).sum()


def zu_verst_eink_excl_grundr_zuschlag_m(
    proxy_rente_vorj_excl_grundr_zuschlag_m: FloatSeries,
    bruttolohn_vorj_m: FloatSeries,
    brutto_eink_1: FloatSeries,
    brutto_eink_6: FloatSeries,
    kapital_eink_minus_pauschbetr: FloatSeries,
) -> FloatSeries:
    """Income relevant for income crediting rule of Grundrentenzuschlag. The
    Grundrentenzuschlag (in previous years) is not part of the relevant income and
    does not lower the Grundrentenzuschlag.

    The Deutsche Rentenversicherung uses the income of the year two to three years
    ago to be able to use administrative data on this income for the calculation.

    "Es ist davon auszugehen, dass dem Finanzamt regelmäßig zwei Jahre nach dem Ablauf
    des Veranlagungszeitraums die Daten vorliegen, die von der Rentenversicherung
    abgerufen werden können. "

    Warning: Currently, earnings of dependend work and pensions are based on the
    last year, and other income on the current year instead of the year
    two years ago to avoid the need for several new input variables.

    #ToDo: Freibeträge for income are currently not considered
    #ToDO: as freibetraege_tu depends on pension income

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
    entgeltpunkte
        See :func:`entgeltpunkte`.

    Returns
    -------
    """

    # Earnings from self-employed work and rent income (assumption that they were
    # the same last year)
    earnings_work_rent = brutto_eink_1 + brutto_eink_6

    out = (
        proxy_rente_vorj_excl_grundr_zuschlag_m
        + bruttolohn_vorj_m
        + earnings_work_rent / 12
        + kapital_eink_minus_pauschbetr / 12
    )

    return out


def proxy_rente_vorj_excl_grundr_zuschlag_m(
    wohnort_ost: BoolSeries,
    ges_renten_vers_params: dict,
    prv_rente_m: FloatSeries,
    jahr_renteneintr: IntSeries,
    geburtsjahr: IntSeries,
    alter: IntSeries,
    entgeltpunkte: FloatSeries,
    zugangsfaktor: FloatSeries,
) -> FloatSeries:
    """Estimated amount of public pensions of last year excluding Grundrentenzuschlag.

    See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    prv_rente_m
        See basic input variable :ref:`prv_rente_m <prv_rente_m>`.
    entgeltpunkte
        See :func:`entgeltpunkte`.

    Returns
    -------
    """

    # Calculate pension in the last year in case the subject was already retired
    rentenwert_vorjahr = wohnort_ost.replace(
        {
            True: ges_renten_vers_params["rentenwert_vorjahr"]["ost"],
            False: ges_renten_vers_params["rentenwert_vorjahr"]["west"],
        }
    ).astype(float)

    # Assume prv_rente_m did not change
    out = entgeltpunkte * zugangsfaktor * rentenwert_vorjahr + prv_rente_m

    # Calculate if subect was retired last year
    # ToDo: Use current_year as input variable once we addressed issue #211
    current_year = geburtsjahr + alter
    rentner_vorjahr = jahr_renteneintr <= current_year - 1

    out.loc[~rentner_vorjahr] = 0
    return out


def nicht_grundrentenberechtigt(
    grundrentenzeiten: IntSeries, ges_renten_vers_params: dict
) -> BoolSeries:
    """Indicates that person is not entitled to Freibetragsregelung.

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


# def freibetrag_grunds_ia_grundr(
#     staatl_rente_m: FloatSeries,
#     arbeitsl_geld_2_params: dict,
#     nicht_grundrentenberechtigt: BoolSeries,
# ) -> FloatSeries:
#     """Compute allowance of Grundrente for Grundsicherung im Alter

#     Parameters
#     ----------
#     staatl_rente_m
#         See basic input variable :ref:`staatl_rente_m <staatl_rente_m>`.
#     arbeitsl_geld_2_params
#         See params documentation :ref:`arbeitsl_geld_2_params
# <arbeitsl_geld_2_params>`.
#     nicht_grundrentenberechtigt
#         See :func:`nicht_grundrentenberechtigt`.

#     Returns
#     -------

#     """
#     out = (
#         staatl_rente_m.clip(upper=100) + (staatl_rente_m - 100).clip(lower=0) * 0.3
#     ).clip(upper=0.5 * arbeitsl_geld_2_params["regelsatz"][1])
#     out.loc[nicht_grundrentenberechtigt] = 0
#     return out


def alleinstehend_grundr(anz_erwachsene_tu: IntSeries, tu_id: IntSeries) -> BoolSeries:
    """Indicates whether pensioner is single based on number of adults in the tax unit.

    Parameters
    ----------
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.

    Returns
    -------

    """
    return tu_id.replace(anz_erwachsene_tu < 2)
