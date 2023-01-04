"""The following functions could be used to calculate the pension claim in future years
or alternative policy scenarios.

The functions need some improvement and are not yet done.

"""
from __future__ import annotations


def berechne_rentenwert_aus_daten(ges_rente_params, year):
    """From 2018 onwards we calculate the rentenwert with the formula given by law.

    The formula takes three factors, which will be calculated seperatly. For a detailed
    explanation see https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """
    # Rentenwert: The monetary value of one 'entgeltpunkt'.
    # This depends, among others, of past developments.

    # First the Lohnkomponente which depands on the wage development of last years.
    lohn = lohnkomponente(ges_rente_params, year)
    # Second riesterfaktor
    riester = riesterfaktor(ges_rente_params, year)
    # Nachhaltigskeitsfaktor
    nachhfaktor = nachhaltigkeitsfaktor(ges_rente_params, year)

    # Rentenwert must not be lower than in the previous year.
    renten_factor = lohn * riester * nachhfaktor
    rentenwert = ges_rente_params[f"rentenwert_{year - 1}"] * min(1, renten_factor)
    return rentenwert


def lohnkomponente(ges_rente_params, year):
    """Returns the lohnkomponente for each year.

    It deppends on the average wages of the previous years. For details see
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """
    return ges_rente_params[f"durchschnittslohn_{year - 1}"] / (
        ges_rente_params[f"durchschnittslohn_{year - 2}"]
        * (
            (
                ges_rente_params[f"durchschnittslohn_{year - 2}"]
                / ges_rente_params[f"durchschnittslohn_{year - 3}"]
            )
            / (
                ges_rente_params[f"beitragspflichtiges_durchschnittsentgelt_{year - 2}"]
                / ges_rente_params[
                    f"beitragspflichtiges_durchschnittsentgelt_{year - 3}"
                ]
            )
        )
    )


def riesterfaktor(ges_rente_params, soz_vers_beitr_params, year):
    """This factor returns the riesterfactor, depending on the Altersvorsogeanteil and
    the contributions to the pension insurance.

    For details see https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """
    return (
        100
        - ges_rente_params[f"altersvorsogeanteil_{year - 1}"]
        - soz_vers_beitr_params[f"rvbeitrag_{year - 1}"]
    ) / (
        100
        - ges_rente_params[f"altersvorsogeanteil_{year - 2}"]
        - soz_vers_beitr_params[f"ges_rentenv_{year - 2}"]
    )


def nachhaltigkeitsfaktor(ges_rente_params, year):
    """This factor mirrors the effect of the relationship between pension insurance
    receivers and contributes on the pensions.

    It depends on the rentnerquotienten and some correcting scalar alpha. For details
    see https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """
    rq_last_year = rentnerquotienten(ges_rente_params, year - 1)
    rq_two_years_before = rentnerquotienten(ges_rente_params, year - 2)
    # There is an additional 'Rentenartfaktor', equal to 1 for old-age pensions.
    return 1 + (
        (1 - (rq_last_year / rq_two_years_before)) * ges_rente_params[f"alpha_{year}"]
    )


def rentnerquotienten(ges_rente_params, soz_vers_beitr_params, year):
    """The rentnerquotient is the relationship between pension insurance receivers and
    contributes.

    For details see https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """
    return (
        ges_rente_params[f"gesamtes_rentenvolumen_{year}"]
        / ges_rente_params[f"eckrente_{year}"]
    ) / (
        ges_rente_params[f"beitragsvolumen_{year}"]
        / (
            soz_vers_beitr_params[f"ges_rentenv_{year}"]
            / 100
            * ges_rente_params[f"eckrente_{year}"]
        )
    )
