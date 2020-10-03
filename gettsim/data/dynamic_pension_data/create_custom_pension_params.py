"""
The following functions could be used to calculate the pension claim in future
years or alternative policy scenarios.
"""


def brechne_rentenwert_aus_daten(params, year):
    """From 2018 onwards we calculate the rentenwert with the formula given by law.
    The formula takes three factors, which will be calculated seperatly. For a
    detailed explanation see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    # Rentenwert: The monetary value of one 'entgeltpunkt'.
    # This depends, among others, of past developments.

    # First the Lohnkomponente which depands on the wage development of last years.
    lohn = lohnkomponente(params, year)
    # Second riesterfaktor
    riester = riesterfaktor(params, year)
    # Nachhaltigskeitsfaktor
    nachhfaktor = nachhaltigkeitsfaktor(params, year)

    # Rentenwert must not be lower than in the previous year.
    renten_factor = lohn * riester * nachhfaktor
    rentenwert = params[f"rentenwert_ext_{year - 1}"] * min(1, renten_factor)
    return rentenwert


def lohnkomponente(params, year):
    """Returns the lohnkomponente for each year. It deppends on the average wages of
    the previous years. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return params[f"meanwages_{year - 1}"] / (
        params[f"meanwages_{year - 2}"]
        * (
            (params[f"meanwages_{year - 2}"] / params[f"meanwages_{year - 3}"])
            / (
                params[f"meanwages_sub_{year - 2}"]
                / params[f"meanwages_sub_{year - 3}"]
            )
        )
    )


def riesterfaktor(params, year):
    """This factor returns the riesterfactor, depending on the Altersvorsogeanteil
    and the contributions to the pension insurance. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return (100 - params[f"ava_{year - 1}"] - params[f"rvbeitrag_{year - 1}"]) / (
        100 - params[f"ava_{year - 2}"] - params[f"rvbeitrag_{year - 2}"]
    )


def nachhaltigkeitsfaktor(params, year):
    """This factor mirrors the effect of the relationship between pension insurance
    receivers and contributes on the pensions. It depends on the rentnerquotienten and
    some correcting scalar alpha. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    rq_last_year = rentnerquotienten(params, year - 1)
    rq_two_years_before = rentnerquotienten(params, year - 2)
    # There is an additional 'Rentenartfaktor', equal to 1 for old-age pensions.
    return 1 + ((1 - (rq_last_year / rq_two_years_before)) * params[f"alpha_{year}"])


def rentnerquotienten(params, year):
    """The rentnerquotient is the relationship between pension insurance receivers and
    contributes. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    return (params[f"rentenvol_{year}"] / params[f"eckrente_{year}"]) / (
        params[f"beitragsvol_{year}"]
        / (params[f"rvbeitrag_{year}"] / 100 * params[f"eckrente_{year}"])
    )
