import numpy as np


def pensions(person, soz_vers_beitr_data, pension_data):
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
    # meanwages is only filled until 2016
    year = min(soz_vers_beitr_data["yr"], 2016)

    person = update_earnings_points(person, soz_vers_beitr_data, pension_data, year)
    # ZF: Zugangsfaktor.
    ZF = _zugangsfaktor(person)

    rentenwert = soz_vers_beitr_data["calc_rentenwert"](pension_data, year)

    # use all three components for Rentenformel.
    # It's called 'pensions_sim' to emphasize that this is simulated.

    person["pensions_sim"] = np.maximum(0, round(person["EP"] * ZF * rentenwert, 2))

    return person


def update_earnings_points(person, soz_vers_beitr_data, pension_data, year):
    """Given earnings, social security rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """

    out = _ep_for_earnings(person, soz_vers_beitr_data, pension_data, year)
    out += _ep_for_care_periods(person, soz_vers_beitr_data, pension_data)
    # Note: We might need some interaction between the two
    # ways to accumulate earnings points (e.g., how to
    # determine what constitutes a 'care period')
    person["EP"] += out
    return person


def _ep_for_earnings(person, soz_vers_beitr_data, pension_data, year):
    """Return earning points for the wages earned in the last year."""
    westost = "o" if person["east"] else "w"
    return (
        np.minimum(person["m_wage"], soz_vers_beitr_data["rvmaxek" + westost])
        / pension_data["meanwages"][year]
    )


def _ep_for_care_periods(df, soz_vers_beitr_data, pension_data):
    """Return earnings points for care periods."""
    return 0


def _zugangsfaktor(person):
    """ The zugangsfaktor depends on the age of entering pensions. At the
    regelaltersgrenze, the agent is allowed to get pensions with his full
    claim. For every year under the regelaltersgrenze, the agent looses 3.6% of his
    claim."""
    regelaltersgrenze = _regelaltersgrenze(person)

    return (person["age"] - regelaltersgrenze) * 0.036 + 1


def _regelaltersgrenze(person):
    """Calculates the age, at which a worker is eligible to claim his full pension."""
    # If born after 1947, each birth year raises the age threshold by one month.
    if person["byear"] > 1947:
        regelaltersgrenz = np.minimum(67, ((person["byear"] - 1947) / 12) + 65)
    else:
        regelaltersgrenz = 65

    return regelaltersgrenz


def _rentenwert_until_2017(pension_data, yr):
    """For the years until 2017, we use a exogenous value for the rentenwert."""
    return pension_data["rentenwert_ext"][yr]


def _rentenwert_from_2018(pension_data, yr):
    """From 2018 onwards we calculate the rentenwert with the formula given by law.
    The formula takes three factors, which will be calculated seperatly. For a
    detailed explanation see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    # Rentenwert: The monetary value of one 'entgeltpunkt'.
    # This depends, among others, of past developments.
    # Hence, some calculations have been made
    # in the data preparation.
    # First the Lohnkomponente which depands on the wage development of last years.
    lohnkomponente = _lohnkomponente(pension_data, yr)
    # Second riesterfaktor
    riesterfaktor = _riesterfactor(pension_data, yr)
    # Nachhaltigskeitsfaktor
    nachhfaktor = _nachhaltigkeitsfaktor(pension_data, yr)

    # Rentenwert must not be lower than in the previous year.
    renten_factor = lohnkomponente * riesterfaktor * nachhfaktor
    rentenwert = pension_data["rentenwert_ext"][yr - 1] * min(1, renten_factor)
    return rentenwert


def _lohnkomponente(pension_data, yr):
    """Returns the lohnkomponente for each year. It deppends on the average wages of
    the previous years. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return pension_data["meanwages"][yr - 1] / (
        pension_data["meanwages"][yr - 2]
        * (
            (pension_data["meanwages"][yr - 2] / pension_data["meanwages"][yr - 3])
            / (
                pension_data["meanwages_sub"][yr - 2]
                / pension_data["meanwages_sub"][yr - 3]
            )
        )
    )


def _riesterfactor(pension_data, yr):
    """This factor returns the riesterfactor, depending on the Altersvorsogeanteil
    and the contributions to the pension insurance. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return (100 - pension_data["ava"][yr - 1] - pension_data["rvbeitrag"][yr - 1]) / (
        100 - pension_data["ava"][yr - 2] - pension_data["rvbeitrag"][yr - 2]
    )


def _nachhaltigkeitsfaktor(pension_data, yr):
    """This factor mirrors the effect of the relationship between pension insurance
    receivers and contributes on the pensions. It depends on the rentnerquotienten and
    some correcting scalar alpha. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    rq_last_year = _rentnerquotienten(pension_data, yr - 1)
    rq_two_years_before = _rentnerquotienten(pension_data, yr - 2)
    # There is an additional 'Rentenartfaktor', equal to 1 for old-age pensions.
    return 1 + ((1 - (rq_last_year / rq_two_years_before)) * pension_data["alpha"][yr])


def _rentnerquotienten(pension_data, yr):
    """The rentnerquotient is the relationship between pension insurance receivers and
    contributes. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return (pension_data["rentenvol"][yr] / pension_data["eckrente"][yr]) / (
        pension_data["beitragsvol"][yr]
        / (pension_data["rvbeitrag"][yr] / 100 * pension_data["eckrente"][yr])
    )
