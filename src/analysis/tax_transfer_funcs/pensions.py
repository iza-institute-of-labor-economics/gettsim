import numpy as np

# from termcolor import cprint


def _ep_for_earnings(df, tb, tb_pens):
    if df["east"]:
        westost = "o"
    else:
        westost = "w"
    return np.minimum(df["m_wage"], tb["rvmaxek" + westost]) / tb_pens["meanwages"]


def _ep_for_care_periods(df, tb, tb_pens):
    """Return earnings points for care periods."""
    return 0.0


# @numba.jit(nopython=True)
def update_earnings_points(df, tb, tb_pens):
    """Given earnings, social security rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    """

    out = _ep_for_earnings(df, tb, tb_pens)
    out += _ep_for_care_periods(df, tb, tb_pens)
    # Note: We might need some interaction between the two
    # ways to accumulate earnings points (e.g., how to
    # determine what constitutes a 'care period')

    return df["EP"] + out


def calc_regelaltersgrenze(df_row):
    # If born after 1947, each birth year raises the age threshold by one month.
    if df_row["byear"] > 1947:
        return np.minimum(67, ((df_row["byear"] - 1947) / 12) + 65)
    else:
        return 65


def calc_rentenwert_from_2018(tb_pens, yr):
    # Rentenwert: The monetary value of one 'entgeltpunkt'.
    # This depends, among others, of past developments.
    # Hence, some calculations have been made
    # in the data preparation.
    # First the Lohnkomponente which depands on the wage development of last years.
    lohnkomponente = tb_pens.loc["meanwages", yr - 1] / (
        tb_pens.loc["meanwages", yr - 2]
        * (
            (tb_pens.loc["meanwages", yr - 2] / tb_pens.loc["meanwages", yr - 3])
            / (
                tb_pens.loc["meanwages_sub", yr - 2]
                / tb_pens.loc["meanwages_sub", yr - 3]
            )
        )
    )
    riesterfaktor = (
        100 - tb_pens.loc["ava", yr - 1] - tb_pens.loc["rvbeitrag", yr - 1]
    ) / (100 - tb_pens.loc["ava", yr - 2] - tb_pens.loc["rvbeitrag", yr - 2])
    # Rentnerquotienten
    rq = {}
    for t in [1, 2]:
        rq[t] = (tb_pens.loc["rentenvol", yr - t] / tb_pens.loc["eckrente", yr - t]) / (
            tb_pens.loc["beitragsvol", yr - t]
            / (tb_pens.loc["rvbeitrag", yr - t] / 100 * tb_pens.loc["eckrente", yr - t])
        )
    # Nachhaltigskeitsfaktor
    nachhfaktor = 1 + ((1 - (rq[1] / rq[2])) * tb_pens.loc["alpha", yr])
    # Rentenwert must not be lower than in the previous year.
    rentenwert = tb_pens.loc["rentenwert_ext", yr - 1] * min(
        1, lohnkomponente * riesterfaktor * nachhfaktor
    )
    print(
        "Änderung des Rentenwerts: "
        + str(min(1, lohnkomponente * riesterfaktor * nachhfaktor))
    )
    return rentenwert


def calc_rentenwert_until_2017(tb_pens, yr):
    return tb_pens.loc["rentenwert_ext", yr]


def pensions(df_row, tb, tb_pens):
    """
    This function calculates the Old-Age Pensions claim if the agent chooses to
    retire. The function basicly follows the following equation
    # R = EP * ZF * Rw

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    - In particular, it calculates the "entgeltpunkte" for the previous year, based on
      earnings of that year. These need to be related to average earnings
    - As we do not know previously collect Entgeltpunkte, we take an average
      value (to be improved)

    """
    # cprint("Pensions", "red", "on_white")
    # meanwages is only filled until 2016
    yr = min(df_row["year"], 2016)

    EP = update_earnings_points(df_row, tb, tb_pens[yr])
    # ZF: Zugangsfaktor. Depends on the age of entering pensions.
    # At the regelaltersgrenze, the agent is allowed to get pensions with his full
    # claim.
    regelaltersgrenze = calc_regelaltersgrenze(df_row)

    ZF = ((df_row["age"] - regelaltersgrenze) * 0.036) + 1

    # individuelle monatl. Altersrente (Rentenartfaktor = 1):
    # Calculate rentenwert either using external (SOEP) or internal value for
    # rentenwert.
    rentenwert = tb["calc_rentenwert"](tb_pens, yr)

    # use all three components for Rentenformel.
    # There is an additional 'Rentenartfaktor', equal to 1 for old-age pensions.
    # It's called 'pensions_sim' to emphasize that this is simulated.

    pensions_sim = np.maximum(0, round(EP * ZF * rentenwert, 2))

    return pensions_sim
