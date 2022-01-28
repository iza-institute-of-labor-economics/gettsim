import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grundr_zuschlag_m(
    grundr_zuschlag_vor_eink_anr_m: FloatSeries, anr_eink_gr_m: FloatSeries
) -> FloatSeries:
    """Calculate Grundrentenzuschlag (additional monthly pensions payments
    resulting from Grundrente)

    Parameters
    ----------
    grundr_zuschlag_vor_eink_anr_m
        See :func:`grundr_zuschlag_vor_eink_anr_m`.
    anr_eink_gr_m
        See :func:`anr_eink_gr_m`.

    Returns
    -------

    """
    out = grundr_zuschlag_vor_eink_anr_m - anr_eink_gr_m
    return out.clip(lower=0).round(2)


def anr_eink_gr_m(
    gemeinsam_veranlagt: BoolSeries,
    eink_excl_grundr_zuschlag_m_tu: FloatSeries,
    rentenwert: FloatSeries,
    tu_id: IntSeries,
    ges_rentenv_params: dict,
) -> FloatSeries:
    """Calculate reduction of Grundrentenzuschlag through income offsetting.

    Implement income crediting rule as defined in Grundrentengesetz.

    There are upper and lower thresholds for singles and couples. 60% of income between
    the upper and lower threshold is credited against the Grundrentenzuschlag. All the
    income above the upper threshold is credited against the Grundrentenzuschlag.

    Parameters
    ----------
    gemeinsam_veranlagt
        See :func:`gemeinsam_veranlagt`.
    eink_excl_grundr_zuschlag_m_tu
        See :func:`eink_excl_grundr_zuschlag_m_tu`.
    rentenwert
        See :func:`rentenwert`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    ges_rentenv_params
        See params documentation :ref:`ges_rentenv_params <ges_rentenv_params>`.
    Returns
    -------

    """

    # Select correct thresholds of income crediting rule.
    einkommensanrechnung_upper = gemeinsam_veranlagt.replace(
        {
            False: ges_rentenv_params["einkommensanr_grundrente"]["upper"],
            True: ges_rentenv_params["einkommensanr_grundrente"]["upper_ehe"],
        }
    ).astype(float)

    einkommensanrechnung_lower = gemeinsam_veranlagt.replace(
        {
            False: ges_rentenv_params["einkommensanr_grundrente"]["lower"],
            True: ges_rentenv_params["einkommensanr_grundrente"]["lower_ehe"],
        }
    ).astype(float)
    upper = einkommensanrechnung_upper * rentenwert
    lower = einkommensanrechnung_lower * rentenwert

    # Calculate deducted income following the crediting rules.
    einkommen_grundr = tu_id.replace(eink_excl_grundr_zuschlag_m_tu)
    einkommen_btw_upper_lower = (einkommen_grundr.clip(upper=upper) - lower).clip(
        lower=0
    )
    einkommen_above_upper = (einkommen_grundr - upper).clip(lower=0)

    out = einkommen_btw_upper_lower * 0.6 + einkommen_above_upper

    return out.round(2)


def grundr_zuschlag_vor_eink_anr_m(
    bonus_entgeltpunkte_grundr: FloatSeries,
    g_r_bewertungsreiten: IntSeries,
    rentenwert: FloatSeries,
    zugangsfaktor: FloatSeries,
    ges_rentenv_params: dict,
) -> FloatSeries:
    """Calculate additional monthly pensions payments resulting from
    Grundrente, without taking into account income crediting rules.

    According to the Grundrentengesetz, the Zugangsfaktor is limited to 1
    and considered Grundrentezeiten are limited to 35 years (420 months).
    Parameters
    ----------
    bonus_entgeltpunkte_grundr
        See :func:`bonus_entgeltpunkte_grundr`.
    g_r_bewertungsreiten
        See basic input variable
        :ref:`g_r_bewertungsreiten <g_r_bewertungsreiten>`.
    rentenwert
        See :func:`rentenwert`.
    zugangsfaktor
        See :func:`zugangsfaktor`.
    ges_rentenv_params
        See params documentation :ref:`ges_rentenv_params <ges_rentenv_params>`.

    Returns
    -------

    """
    out = (
        bonus_entgeltpunkte_grundr
        * g_r_bewertungsreiten.clip(
            upper=ges_rentenv_params["grundrentenzeiten"]["max"]
        )
        * rentenwert
        * zugangsfaktor.clip(upper=1)
    )
    return out.round(2)


def durchschnittl_entgeltp_grundr(
    entgeltp_grundr: FloatSeries, g_r_bewertungsreiten: IntSeries
) -> FloatSeries:
    """Compute average number of Entgeltpunkte earned per month of Grundrentenzeiten.

    Parameters
    ----------
    entgeltp_grundr
        See basic input variable
        :ref:`entgeltp_grundr <entgeltp_grundr>`.
    g_r_bewertungsreiten
        See basic input variable
        :ref:`g_r_bewertungsreiten <g_r_bewertungsreiten>`.

    Returns
    -------

    """
    return entgeltp_grundr / g_r_bewertungsreiten


def höchstwert_grundr_m(
    grundrentenzeiten: IntSeries, ges_rentenv_params: dict
) -> FloatSeries:
    """Calculates the maximum allowed number of average Entgeltpunkte (per month)
    after adding bonus of Entgeltpunkte for a given number of Grundrentenzeiten.

    Parameters
    ----------
    grundrentenzeiten
        See basic input variable :ref:`grundrentenzeiten <grundrentenzeiten>`.
    ges_rentenv_params
        See params documentation :ref:`ges_rentenv_params <ges_rentenv_params>`.

    Returns
    -------

    """

    # Calculate number of months above minimum threshold
    months_above_thresh = (
        grundrentenzeiten.clip(upper=ges_rentenv_params["grundrentenzeiten"]["max"])
        - ges_rentenv_params["grundrentenzeiten"]["min"]
    )

    # Calculate höchstwert
    out = (
        ges_rentenv_params["höchstwert_grundrente"]["base"]
        + ges_rentenv_params["höchstwert_grundrente"]["increment"] * months_above_thresh
    )

    # Round to 4 digits
    return out.round(4)


def bonus_entgeltpunkte_grundr(
    durchschnittl_entgeltp_grundr: FloatSeries,
    höchstwert_grundr_m: FloatSeries,
    grundrentenzeiten: IntSeries,
    ges_rentenv_params: dict,
) -> FloatSeries:
    """Calculate additional Entgeltpunkte for pensioner.

    In general, the average of monthly Entgeltpunkte earnd in Grundrentenzeiten is
    doubled, or extended to the individual Höchstwert if doubling would exceed the
    Höchstwert. Then, the value is multiplied by 0.875.

    Legal reference: § 76g SGB VI

    Parameters
    ----------
    durchschnittl_entgeltp_grundr
        See :func:`durchschnittl_entgeltp_grundr`.
    höchstwert_grundr_m
        See :func:`höchstwert_grundr_m`.
    grundrentenzeiten
        See basic input variable :ref:`grundrentenzeiten <grundrentenzeiten>`.
    ges_rentenv_params
        See params documentation :ref:`ges_rentenv_params <ges_rentenv_params>`.

    Returns
    -------

    """
    out = grundrentenzeiten.astype(float) * np.nan

    # Case 1: Entgeltpunkte less than half of Höchstwert
    below_half_höchstwert = durchschnittl_entgeltp_grundr <= (0.5 * höchstwert_grundr_m)
    out.loc[below_half_höchstwert] = durchschnittl_entgeltp_grundr

    # Case 2: Entgeltpunkte more than half of Höchstwert, but below Höchstwert
    cond = ~below_half_höchstwert & (
        durchschnittl_entgeltp_grundr < höchstwert_grundr_m
    )
    out.loc[cond] = höchstwert_grundr_m - durchschnittl_entgeltp_grundr

    # Case 3: Entgeltpunkte above Höchstwert
    cond = durchschnittl_entgeltp_grundr > höchstwert_grundr_m
    out.loc[cond] = 0

    # Set to 0 if Grundrentenzeiten below minimum
    gr_zeiten_below_min = (
        grundrentenzeiten < ges_rentenv_params["grundrentenzeiten"]["min"]
    )
    out.loc[gr_zeiten_below_min] = 0

    # Multiply additional Engeltpunkte by factor
    out = out * ges_rentenv_params["faktor_bonus_grundrente"]

    return out


def eink_excl_grundr_zuschlag_m_tu(
    eink_excl_grundr_zuschlag_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate the income relevant for income crediting rule of
    Grundrentenzuschlag on tax unit level.

    Parameters
    ----------
    eink_excl_grundr_zuschlag_m
        See :func:`eink_excl_grundr_zuschlag_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return eink_excl_grundr_zuschlag_m.groupby(tu_id).sum()


def eink_excl_grundr_zuschlag_m(
    proxy_rente_vorj_excl_grundr_m: FloatSeries,
    bruttolohn_vorj_m: FloatSeries,
    brutto_eink_1: FloatSeries,
    brutto_eink_6: FloatSeries,
    kapitaleink_minus_pauschbetr: FloatSeries,
) -> FloatSeries:
    """Income relevant for income crediting rule of Grundrentenzuschlag. The
    Grundrentenzuschlag (in previous years) is not part of the relevant income and
    does not lower the Grundrentenzuschlag.

    The Deutsche Rentenversicherung uses the income of the year two to three years
    ago to be able to use administrative data on this income for the calculation.

    "It can be assumed that the tax office regularly has the data two years after
    the end of the assessment period, which can be retrieved from the pension
    insurance."

    Warning: Currently, earnings of dependend work and pensions are based on the
    last year, and other income on the current year instead of the year
    two years ago to avoid the need for several new input variables.

    #ToDo: Freibeträge for income are currently not considered
    #ToDO: as freibetraege_tu depends on pension income

    Parameters
    ----------
    proxy_rente_vorj_excl_grundr_m
        See :func:`proxy_rente_vorj_excl_grundr_m`.
    bruttolohn_vorj_m
        See :func:`bruttolohn_vorj_m`.
    brutto_eink_1
        See :func:`brutto_eink_1`.
    brutto_eink_6
        See :func:`brutto_eink_6`.
    kapitaleink_minus_pauschbetr
        See :func:`kapitaleink_minus_pauschbetr`.
    Returns
    -------
    """

    out = (
        proxy_rente_vorj_excl_grundr_m
        + bruttolohn_vorj_m
        + brutto_eink_1 / 12  # income from self-employment
        + brutto_eink_6 / 12  # income from rents
        + kapitaleink_minus_pauschbetr / 12
    )

    return out


def proxy_rente_vorj_excl_grundr_m(
    rentenwert_vorjahr: FloatSeries,
    priv_rente_m: FloatSeries,
    jahr_renteneintr: IntSeries,
    geburtsjahr: IntSeries,
    alter: IntSeries,
    entgeltpunkte: FloatSeries,
    zugangsfaktor: FloatSeries,
) -> FloatSeries:
    """Estimated amount of public pensions of last year excluding Grundrentenzuschlag.

    rentenwert_vorjahr
        See basic input variable :ref:`rentenwert_vorjahr <rentenwert_vorjahr>`.
    priv_rente_m
        See basic input variable :ref:`priv_rente_m <priv_rente_m>`.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    entgeltpunkte
        See basic input variable :ref:`entgeltpunkte <entgeltpunkte>`.
    zugangsfaktor
        See :func:`zugangsfaktor`.

    Returns
    -------
    """

    # Assume priv_rente_m did not change
    out = entgeltpunkte * zugangsfaktor * rentenwert_vorjahr + priv_rente_m

    # Calculate if subect was retired last year
    # ToDo: Use current_year as input variable once we addressed issue #211
    current_year = geburtsjahr + alter
    rentner_vorjahr = jahr_renteneintr <= current_year - 1

    out.loc[~rentner_vorjahr] = 0
    return out


def nicht_grundrentenberechtigt(
    grundrentenzeiten: IntSeries, ges_rentenv_params: dict
) -> BoolSeries:
    """Indicates that person is not entitled to Freibetragsregelung.

    Parameters
    ----------
    grundrentenzeiten
        See :func:`grundrentenzeiten`.
    ges_rentenv_params
        See params documentation :ref:`ges_rentenv_params <ges_rentenv_params>`.

    Returns
    -------

    """
    return grundrentenzeiten < ges_rentenv_params["grundrentenzeiten"]["min"]
