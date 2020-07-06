import yaml

from gettsim.config import ROOT_DIR


def lade_exogene_renten_daten():

    data_year_range = range(2005, 2016 + 1)
    raw_pension_data = yaml.safe_load(
        (
            ROOT_DIR
            / "pre_processing"
            / "exogene_renten_daten"
            / "ges_renten_vers.yaml"
        ).read_text(encoding="utf-8")
    )

    pension_data = {"durchschnittslohn": {}, "rentenwert": {}}

    for key in pension_data.keys():
        for year in data_year_range:
            if key == "rentenwert":
                if year < 2017:
                    pension_data[key][year] = raw_pension_data["rentenwert_exogen"][
                        year
                    ]
                else:
                    # Here could be the manual calucaltion of rentenwert
                    pass
            else:
                pension_data[key][year] = raw_pension_data[key][year]
    return pension_data


# def _rentenwert_until_2017(params, year):
#     """For the years until 2017, we use a exogenous value for the rentenwert."""
#     return params[f"rentenwert_ext_{year}"]
#
#
# def _rentenwert_from_2018(params, year):
#     """From 2018 onwards we calculate the rentenwert with the formula given by law.
#     The formula takes three factors, which will be calculated seperatly. For a
#     detailed explanation see
#     https://de.wikipedia.org/wiki/Rentenanpassungsformel
#     """
#     # Rentenwert: The monetary value of one 'entgeltpunkt'.
#     # This depends, among others, of past developments.
#
#     # First the Lohnkomponente which depands on the wage development of last years.
#     lohnkomponente = _lohnkomponente(params, year)
#     # Second riesterfaktor
#     riesterfaktor = _riesterfactor(params, year)
#     # Nachhaltigskeitsfaktor
#     nachhfaktor = _nachhaltigkeitsfaktor(params, year)
#
#     # Rentenwert must not be lower than in the previous year.
#     renten_factor = lohnkomponente * riesterfaktor * nachhfaktor
#     rentenwert = params[f"rentenwert_ext_{year - 1}"] * min(1, renten_factor)
#     return rentenwert
#
#
# def _lohnkomponente(params, year):
#     """Returns the lohnkomponente for each year. It deppends on the average wages of
#     the previous years. For details see
#     https://de.wikipedia.org/wiki/Rentenanpassungsformel
#     """
#     return params[f"meanwages_{year - 1}"] / (
#         params[f"meanwages_{year - 2}"]
#         * (
#             (params[f"meanwages_{year - 2}"] / params[f"meanwages_{year - 3}"])
#             / (
#                 params[f"meanwages_sub_{year - 2}"]
#                 / params[f"meanwages_sub_{year - 3}"]
#             )
#         )
#     )
#
#
# def _riesterfactor(params, year):
#     """This factor returns the riesterfactor, depending on the Altersvorsogeanteil
#     and the contributions to the pension insurance. For details see
#     https://de.wikipedia.org/wiki/Rentenanpassungsformel
#     """
#     return (100 - params[f"ava_{year - 1}"] - params[f"rvbeitrag_{year - 1}"]) / (
#         100 - params[f"ava_{year - 2}"] - params[f"rvbeitrag_{year - 2}"]
#     )
#
#
# def _nachhaltigkeitsfaktor(params, year):
#     """This factor mirrors the effect of the relationship between pension insurance
#     receivers and contributes on the pensions. It depends on the rentnerquotienten and
#     some correcting scalar alpha. For details see
#     https://de.wikipedia.org/wiki/Rentenanpassungsformel
#     """
#     rq_last_year = _rentnerquotienten(params, year - 1)
#     rq_two_years_before = _rentnerquotienten(params, year - 2)
#     # There is an additional 'Rentenartfaktor', equal to 1 for old-age pensions.
#     return 1 + ((1 - (rq_last_year / rq_two_years_before)) * params[f"alpha_{year}"])
#
#
# def _rentnerquotienten(params, year):
#     """The rentnerquotient is the relationship between pension insurance receivers and
#     contributes. For details see
#     https://de.wikipedia.org/wiki/Rentenanpassungsformel
#     """
#     return (params[f"rentenvol_{year}"] / params[f"eckrente_{year}"]) / (
#         params[f"beitragsvol_{year}"]
#         / (params[f"rvbeitrag_{year}"] / 100 * params[f"eckrente_{year}"])
#     )
