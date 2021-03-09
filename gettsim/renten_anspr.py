from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def rente_anspr_m(
    zugangsfaktor: FloatSeries,
    entgeltpunkte_update: FloatSeries,
    rentenwert: FloatSeries,
) -> FloatSeries:
    """ This function calculates the Old-Age Pensions claim if the agent chooses to
    retire. The function basically follows the following equation:

    .. math::

        R = EP * ZF * Rw

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    - In particular, it calculates the "entgeltpunkte" for the previous year, based on
      earnings of that year. These need to be related to average earnings
    - As we do not know previously collect Entgeltpunkte, we take an average
      value (to be improved)

    Parameters
    ----------
    zugangsfaktor
        See :func:`zugangsfaktor`.
    entgeltpunkte_update
        See :func:`entgeltpunkte_update`.
    rentenwert
        See :func:`rentenwert`.

    Returns
    -------

    """

    return (entgeltpunkte_update * zugangsfaktor * rentenwert).clip(lower=0)


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
            True: ges_renten_vers_params["rentenwert_west"],
            False: ges_renten_vers_params["rentenwert_west"],
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
    rentenv_beitr_bemess_grenze: FloatSeries,
    ges_renten_vers_params: dict,
) -> FloatSeries:
    """Return earning points for the wages earned in the last year.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    rentenv_beitr_bemess_grenze
        See :func:`rentenv_beitr_bemess_grenze`.
    ges_renten_vers_params
        See params documentation :ref:`ges_renten_vers_params <ges_renten_vers_params>`.
    Returns
    -------

    """
    durchschnittslohn_dt = (1 / 12) * ges_renten_vers_params[
        "beitragspflichtiger_durchschnittslohn"
    ]
    return bruttolohn_m.clip(upper=rentenv_beitr_bemess_grenze) / durchschnittslohn_dt


def zugangsfaktor(alter: IntSeries, regelaltersgrenze: FloatSeries) -> FloatSeries:
    """Calculate the zugangsfaktor determining depending on age your pension claim.

    At the regelaltersgrenze, the agent is allowed to get pensions with his full
    claim. For every year under the regelaltersgrenze, the agent looses 3.6% of his
    claim.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    regelaltersgrenze
        See :func:`regelaltersgrenze`.

    Returns
    -------

    """
    return (alter - regelaltersgrenze) * 0.036 + 1


def regelaltersgrenze(geburtsjahr: IntSeries) -> FloatSeries:
    """Calculates the age, at which a worker is eligible to claim his full pension.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.

    Returns
    -------
    """
    # Create 65 as standard
    out = geburtsjahr * 0 + 65
    # If born after 1947, each birth year raises the age threshold by one month.
    cond = geburtsjahr > 1947
    out.loc[cond] = ((geburtsjahr.loc[cond] - 1947) / 12 + 65).clip(upper=67)
    return out
