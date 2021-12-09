# import pandas as pd
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def gesamte_rente_m(
    prv_rente_m: FloatSeries, staatl_rente_m: FloatSeries
) -> FloatSeries:
    """Calculate total pension as sum of private and public pension.

    Parameters
    ----------
    prv_rente_m
        See basic input variable :ref:`prv_rente_m <prv_rente_m>`.
    staatl_rente_m
        See :func:`staatl_rente_m`.

    Returns
    -------

    """
    out = prv_rente_m + staatl_rente_m
    return out


def staatl_rente_m(
    staatl_rente_excl_gr_m: FloatSeries,
    grundr_zuschlag_m: FloatSeries,
    rentner: BoolSeries,
) -> FloatSeries:
    """Calculate total public pension.

    Parameters
    ----------
    staatl_rente_excl_gr_m
        See :func:`staatl_rente_excl_gr_m`.
    grundr_zuschlag_m
        See :func:`grundr_zuschlag_m`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------

    """
    out = staatl_rente_excl_gr_m + grundr_zuschlag_m

    # Return 0 if person not yet retired
    out.loc[~rentner] = 0
    return out.round(2)


def staatl_rente_excl_gr_m(
    zugangsfaktor: FloatSeries,
    entgeltpunkte_update: FloatSeries,
    rentenwert: FloatSeries,
    rentner: BoolSeries,
) -> FloatSeries:
    """ This function calculates the Old-Age Pensions claim (without Grundrentenzuschlag).
    The function follows the following equation:

    .. math::

        R = EP * ZF * Rw

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel


    Parameters
    ----------
    zugangsfaktor
        See :func:`zugangsfaktor`.
    entgeltpunkte_update
        See :func:`entgeltpunkte_update`.
    rentenwert
        See :func:`rentenwert`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------

    """

    out = entgeltpunkte_update * zugangsfaktor * rentenwert

    # Return 0 if subject not yet retired
    out.loc[~rentner] = 0
    return out


def rente_anspr_m(
    rente_anspr_excl_gr_m: FloatSeries, grundr_zuschlag_m: FloatSeries,
) -> FloatSeries:
    """ This function calculates the Old-Age Pensions claim (including the
    Grundrentenzuschlag) if the agent chooses to retire at Regelaltersgrenze.

    Parameters
    ----------
    rente_anspr_excl_gr_m
        See :func:`rente_anspr_excl_gr_m`.
    grundr_zuschlag_m
        See :func:`grundr_zuschlag_m`.

    Returns
    -------

    """

    return rente_anspr_excl_gr_m + grundr_zuschlag_m


def rente_anspr_excl_gr_m(
    entgeltpunkte_update: FloatSeries, rentenwert: FloatSeries,
) -> FloatSeries:
    """ This function calculates the Old-Age Pensions claim (without Grundrentenzuschlag) if
    the agent chooses to retire at Regelaltersgrenze. It is hence assumed that the
    Zugangsfaktor is 1.


    Parameters
    ----------
    entgeltpunkte_update
        See :func:`entgeltpunkte_update`.
    rentenwert
        See :func:`rentenwert`.

    Returns
    -------

    """

    return (entgeltpunkte_update * rentenwert).clip(lower=0)


def rentenwert(wohnort_ost: BoolSeries, ges_renten_vers_params: dict) -> FloatSeries:
    """Select the rentenwert depending on place of living.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

    Returns
    -------

    """
    out = wohnort_ost.replace(
        {
            True: ges_renten_vers_params["rentenwert"]["ost"],
            False: ges_renten_vers_params["rentenwert"]["west"],
        }
    ).astype(float)
    return out


def rentenwert_vorjahr(
    wohnort_ost: BoolSeries, ges_renten_vers_params: dict
) -> FloatSeries:
    """Select the rentenwert of the last year depending on place of living.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

    Returns
    -------

    """
    out = wohnort_ost.replace(
        {
            True: ges_renten_vers_params["rentenwert_vorjahr"]["ost"],
            False: ges_renten_vers_params["rentenwert_vorjahr"]["west"],
        }
    ).astype(float)
    return out


def entgeltpunkte_update(
    entgeltpunkte: FloatSeries, entgeltpunkte_lohn: FloatSeries
) -> FloatSeries:
    """Update earning points.

    Given earnings, social security rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    Parameters
    ----------
    entgeltpunkte
        See basic input variable :ref:`entgeltpunkte <entgeltpunkte>`.
    entgeltpunkte_lohn
        See :func:`entgeltpunkte_lohn`.

    Returns
    -------

    """

    # Note: We might need some interaction between the two
    # ways to accumulate earnings points (e.g., how to
    # determine what constitutes a 'care period')
    return entgeltpunkte + entgeltpunkte_lohn


def entgeltpunkte_lohn(
    bruttolohn_m: FloatSeries,
    wohnort_ost: BoolSeries,
    rentenv_beitr_bemess_grenze: FloatSeries,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """Return earning points for the wages earned in the last year.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    wohnort_ost
        See :func:`wohnort_ost`.
    rentenv_beitr_bemess_grenze
        See :func:`rentenv_beitr_bemess_grenze`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    Returns
    -------

    """

    # Scale bruttolohn up if earned in eastern Germany
    bruttolohn_scaled_east = bruttolohn_m
    bruttolohn_scaled_east.loc[wohnort_ost] = (
        bruttolohn_scaled_east.loc[wohnort_ost]
        * ges_renten_vers_params["umrechnung_entgeltp_beitrittgebiet"]
    )

    # Calculate the (scaled) wage, which is subject to pension contributions.
    bruttolohn_scaled_rentenv = bruttolohn_scaled_east.clip(
        upper=rentenv_beitr_bemess_grenze
    )

    # Calculate monthly mean wage in Germany
    durchschnittslohn_m = (1 / 12) * ges_renten_vers_params[
        "beitragspflichtiger_durchschnittslohn"
    ]

    return bruttolohn_scaled_rentenv / durchschnittslohn_m


def zugangsfaktor(
    geburtsjahr: IntSeries,
    rentner: BoolSeries,
    jahr_renteneintr: IntSeries,
    regelaltersgrenze: FloatSeries,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """Calculate the zugangsfaktor based on the year the
    subject retired.

    At the regelaltersgrenze, the agent is allowed to get pensions with his full
    claim. If the agent retires earlier or later, the Zugangsfaktor and therefore
    the pension claim is higher or lower.

    Legal reference: § 77 Abs. 2 Nr. 2 SGB VI

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    regelaltersgrenze
        See :func:`regelaltersgrenze`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.

    Returns
    -------

    """

    # Calc age at retirement
    alter_renteneintritt = jahr_renteneintr - geburtsjahr

    # Calc difference to Regelaltersgrenze
    diff = alter_renteneintritt - regelaltersgrenze

    # Zugangsfactor lower if retired before Regelaltersgrenze
    out = diff.copy()
    faktor_pro_jahr_vorzeitig = ges_renten_vers_params[
        "zugangsfaktor_veränderung_pro_jahr"
    ]["vorzeitiger_renteneintritt"]
    out.loc[diff < 0] = 1 + (out.loc[diff < 0] * faktor_pro_jahr_vorzeitig)

    # Zugangsfactor larger if retired before Regelaltersgrenze
    faktor_pro_jahr_später = ges_renten_vers_params[
        "zugangsfaktor_veränderung_pro_jahr"
    ]["späterer_renteneintritt"]
    out.loc[diff >= 0] = 1 + (out.loc[diff >= 0] * faktor_pro_jahr_später)

    # Return 0 if person not yet retired
    out.loc[~rentner] = 0

    return out


def regelaltersgrenze(
    geburtsjahr: IntSeries, ges_renten_vers_params: dict
) -> FloatSeries:
    """Calculates the age, at which a worker is eligible to claim his full pension.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.

    Returns
    -------
    """
    out = piecewise_polynomial(
        x=geburtsjahr,
        thresholds=ges_renten_vers_params["regelaltersgrenze"]["thresholds"],
        rates=ges_renten_vers_params["regelaltersgrenze"]["rates"],
        intercepts_at_lower_thresholds=ges_renten_vers_params["regelaltersgrenze"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out
