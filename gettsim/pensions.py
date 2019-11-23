import numpy as np


def pensions(person, soz_vers_beitr_params, ges_renten_vers_params):
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
    year = min(soz_vers_beitr_params["year"], 2016)

    person = update_earnings_points(
        person, soz_vers_beitr_params, ges_renten_vers_params, year
    )
    # ZF: Zugangsfaktor.
    ZF = _zugangsfaktor(person)

    rentenwert = ges_renten_vers_params["calc_rentenwert"](ges_renten_vers_params, year)

    # use all three components for Rentenformel.
    # It's called 'pensions_sim' to emphasize that this is simulated.

    person["pensions_sim"] = np.maximum(0, round(person["EP"] * ZF * rentenwert, 2))

    return person


def update_earnings_points(person, soz_vers_beitr_params, ges_renten_vers_params, year):
    """Given earnings, social security rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """

    out = _ep_for_earnings(person, soz_vers_beitr_params, ges_renten_vers_params, year)
    out += _ep_for_care_periods(person, soz_vers_beitr_params, ges_renten_vers_params)
    # Note: We might need some interaction between the two
    # ways to accumulate earnings points (e.g., how to
    # determine what constitutes a 'care period')
    person["EP"] += out
    return person


def _ep_for_earnings(person, soz_vers_beitr_params, ges_renten_vers_params, year):
    """Return earning points for the wages earned in the last year."""
    westost = "o" if person["east"] else "w"
    return (
        np.minimum(person["m_wage"], soz_vers_beitr_params["rvmaxek" + westost])
        / ges_renten_vers_params[f"meanwages_{year}"]
    )


def _ep_for_care_periods(df, soz_vers_beitr_params, ges_renten_vers_params):
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


def _rentenwert_until_2017(ges_renten_vers_params, year):
    """For the years until 2017, we use a exogenous value for the rentenwert."""
    return ges_renten_vers_params[f"rentenwert_ext_{year}"]


def _rentenwert_from_2018(ges_renten_vers_params, year):
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
    lohnkomponente = _lohnkomponente(ges_renten_vers_params, year)
    # Second riesterfaktor
    riesterfaktor = _riesterfactor(ges_renten_vers_params, year)
    # Nachhaltigskeitsfaktor
    nachhfaktor = _nachhaltigkeitsfaktor(ges_renten_vers_params, year)

    # Rentenwert must not be lower than in the previous year.
    renten_factor = lohnkomponente * riesterfaktor * nachhfaktor
    rentenwert = ges_renten_vers_params[f"rentenwert_ext_{year - 1}"] * min(
        1, renten_factor
    )
    return rentenwert


def _lohnkomponente(ges_renten_vers_params, year):
    """Returns the lohnkomponente for each year. It deppends on the average wages of
    the previous years. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return ges_renten_vers_params[f"meanwages_{year - 1}"] / (
        ges_renten_vers_params[f"meanwages_{year - 2}"]
        * (
            (
                ges_renten_vers_params[f"meanwages_{year - 2}"]
                / ges_renten_vers_params[f"meanwages_{year - 3}"]
            )
            / (
                ges_renten_vers_params[f"meanwages_sub_{year - 2}"]
                / ges_renten_vers_params[f"meanwages_sub_{year - 3}"]
            )
        )
    )


def _riesterfactor(ges_renten_vers_params, year):
    """This factor returns the riesterfactor, depending on the Altersvorsogeanteil
    and the contributions to the pension insurance. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return (
        100
        - ges_renten_vers_params[f"ava_{year - 1}"]
        - ges_renten_vers_params[f"rvbeitrag_{year - 1}"]
    ) / (
        100
        - ges_renten_vers_params[f"ava_{year - 2}"]
        - ges_renten_vers_params[f"rvbeitrag_{year - 2}"]
    )


def _nachhaltigkeitsfaktor(ges_renten_vers_params, year):
    """This factor mirrors the effect of the relationship between pension insurance
    receivers and contributes on the pensions. It depends on the rentnerquotienten and
    some correcting scalar alpha. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    rq_last_year = _rentnerquotienten(ges_renten_vers_params, year - 1)
    rq_two_years_before = _rentnerquotienten(ges_renten_vers_params, year - 2)
    # There is an additional 'Rentenartfaktor', equal to 1 for old-age pensions.
    return 1 + (
        (1 - (rq_last_year / rq_two_years_before))
        * ges_renten_vers_params[f"alpha_{year}"]
    )


def _rentnerquotienten(ges_renten_vers_params, year):
    """The rentnerquotient is the relationship between pension insurance receivers and
    contributes. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return (
        ges_renten_vers_params[f"rentenvol_{year}"]
        / ges_renten_vers_params[f"eckrente_{year}"]
    ) / (
        ges_renten_vers_params[f"beitragsvol_{year}"]
        / (
            ges_renten_vers_params[f"rvbeitrag_{year}"]
            / 100
            * ges_renten_vers_params[f"eckrente_{year}"]
        )
    )
