import numpy as np

# from termcolor import cprint


def _ep_for_earnings(df, tb, tb_pens):
    if df["east"].iloc[0]:
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


def pensions(df, tb, tb_pens, year):
    """ Old-Age Pensions

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    - In particular, it calculates the "entgeltpunkte" for the previous year, based on
      earnings of that year. These need to be related to average earnings
    - As we do not know previously collect Entgeltpunkte, we take an average
      value (to be improved)

    """
    r = df.copy()
    # cprint("Pensions", "red", "on_white")
    # meanwages is only filled until 2016
    yr = min(year, 2016)

    westost = [~df["east"], df["east"]]

    # individuelle monatl. Altersrente (Rentenartfaktor = 1):
    # R = EP * ZF * Rw

    # Add values for current year: ratio of own wage (up to the threshold)
    # to the mean wage
    r["EP"] += np.select(
        westost,
        [
            np.minimum(r["m_wage"], tb["rvmaxekw"]) / tb_pens.loc["meanwages", yr],
            np.minimum(r["m_wage"], tb["rvmaxeko"]) / tb_pens.loc["meanwages", yr],
        ],
    )
    # ZF: Zugangsfaktor. Depends on the age of entering pensions.
    # For each year entering earlier (later) than the statutory retirement age,
    # you get a penalty (reward) of 3.6 pp.
    r["regelaltersgrenze"] = 65
    # If born after 1947, each birth year raises the age threshold by one month.
    r.loc[r["byear"] > 1947, "regelaltersgrenze"] = np.minimum(
        67, ((r["byear"] - 1947) / 12) + 65
    )
    r["ZF"] = ((r["age"] - r["regelaltersgrenze"]) * 0.036) + 1

    # Rentenwert: The monetary value of one 'entgeltpunkt'.
    # This depends, among others, of past developments.
    # Hence, some calculations have been made
    # in the data preparation.
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
    # use external (SOEP) or internal value for rentenwert?
    if yr <= 2017:
        rentenwert = tb_pens.loc["rentenwert_ext", yr]
    else:
        # Rentenwert must not be lower than in the previous year.
        rentenwert = tb_pens.loc["rentenwert_ext", yr - 1] * min(
            1, lohnkomponente * riesterfaktor * nachhfaktor
        )
        print(
            "Änderung des Rentenwerts: "
            + str(min(1, lohnkomponente * riesterfaktor * nachhfaktor))
        )

    # use all three components for Rentenformel.
    # There is an additional 'Rentenartfaktor', equal to 1 for old-age pensions.
    # It's called 'pensions_sim' to emphasize that this is simulated.

    r["pensions_sim"] = np.maximum(0, round(r["EP"] * r["ZF"] * rentenwert, 2))

    return r["pensions_sim"]
