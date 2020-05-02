def pensions(person, renten_daten, soz_vers_beitr_params):
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
    # We only have exogenous pension data from 2005 til 2016.
    year = soz_vers_beitr_params["jahr"]
    if year > 2016 or year < 2005:
        return person

    person = update_earnings_points(person, soz_vers_beitr_params, renten_daten)
    # ZF: Zugangsfaktor.
    ZF = _zugangsfaktor(person)

    rentenwert = renten_daten["rentenwert"][year]

    # use all three components for Rentenformel.
    # It's called 'pensions_sim' to emphasize that this is simulated.

    person["rente_anspr_m"] = max(
        0, round(person["entgeltpunkte"] * ZF * rentenwert, 2)
    )

    return person


def update_earnings_points(person, soz_vers_beitr_params, renten_daten):
    """Given earnings, social security rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """

    durchschnittslohn_dt = renten_daten["durchschnittslohn"][
        soz_vers_beitr_params["jahr"]
    ]

    out = _ep_for_earnings(person, soz_vers_beitr_params, durchschnittslohn_dt)
    out += _ep_for_care_periods(person, soz_vers_beitr_params)
    # Note: We might need some interaction between the two
    # ways to accumulate earnings points (e.g., how to
    # determine what constitutes a 'care period')
    person["entgeltpunkte"] += out
    return person


def _ep_for_earnings(person, soz_vers_beitr_params, durchschnittslohn_dt):
    """Return earning points for the wages earned in the last year."""
    wohnort = "ost" if person["wohnort_ost"] else "west"
    return (
        min(
            person["bruttolohn_m"],
            soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"][wohnort],
        )
        / durchschnittslohn_dt
    )


def _ep_for_care_periods(df, soz_vers_beitr_params):
    """Return earnings points for care periods."""
    return 0


def _zugangsfaktor(person):
    """ The zugangsfaktor depends on the age of entering pensions. At the
    regelaltersgrenze, the agent is allowed to get pensions with his full
    claim. For every year under the regelaltersgrenze, the agent looses 3.6% of his
    claim."""
    regelaltersgrenze = _regelaltersgrenze(person)

    return (person["alter"] - regelaltersgrenze) * 0.036 + 1


def _regelaltersgrenze(person):
    """Calculates the age, at which a worker is eligible to claim his full pension."""
    # If born after 1947, each birth year raises the age threshold by one month.
    if person["geburtsjahr"] > 1947:
        regelaltersgrenze = min(67, ((person["geburtsjahr"] - 1947) / 12) + 65)
    else:
        regelaltersgrenze = 65

    return regelaltersgrenze
