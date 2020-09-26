def rente_anspr_m(
    zugangsfaktor, entgeltpunkte_update, renten_daten, soz_vers_beitr_params
):
    """
    This function calculates the Old-Age Pensions claim if the agent chooses to
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

    """

    rentenwert = renten_daten["rentenwert"][soz_vers_beitr_params["year"]]

    out = (entgeltpunkte_update * zugangsfaktor * rentenwert).clip(lower=0)

    return out


def entgeltpunkte_update(entgeltpunkte, entgeltpunkte_lohn):
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
    entgeltpunkte_lohn

    Returns
    -------

    """

    # Note: We might need some interaction between the two
    # ways to accumulate earnings points (e.g., how to
    # determine what constitutes a 'care period')
    out = entgeltpunkte + entgeltpunkte_lohn
    return out


def entgeltpunkte_lohn(
    bruttolohn_m, _rentenv_beitr_bemess_grenze, soz_vers_beitr_params, renten_daten
):
    """Return earning points for the wages earned in the last year.

    Parameters
    ----------
    bruttolohn_m
    _rentenv_beitr_bemess_grenze
    soz_vers_beitr_params
    renten_daten

    Returns
    -------

    """
    durchschnittslohn_dt = renten_daten["durchschnittslohn"][
        soz_vers_beitr_params["jahr"]
    ]
    return bruttolohn_m.clip(upper=_rentenv_beitr_bemess_grenze) / durchschnittslohn_dt


def zugangsfaktor(alter, regelaltersgrenze):
    """The zugangsfaktor depends on the age of entering pensions. At the
    regelaltersgrenze, the agent is allowed to get pensions with his full
    claim. For every year under the regelaltersgrenze, the agent looses 3.6% of his
    claim.

    Parameters
    ----------
    alter
    regelaltersgrenze

    Returns
    -------

    """

    out = (alter - regelaltersgrenze) * 0.036 + 1
    return out


def regelaltersgrenze(geburtsjahr):
    """Calculates the age, at which a worker is eligible to claim his full pension.

    Parameters
    ----------
    geburtsjahr

    Returns
    -------

    """
    # Create 65 as standard
    out = geburtsjahr * 0 + 65
    # If born after 1947, each birth year raises the age threshold by one month.
    cond = geburtsjahr > 1947
    out.loc[cond] = ((geburtsjahr.loc[cond] - 1947) / 12 + 65).clip(upper=67)
    return out
