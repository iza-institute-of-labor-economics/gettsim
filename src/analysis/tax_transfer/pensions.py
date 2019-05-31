import numpy as np
import pandas as pd
from termcolor import cprint
from bld.project_paths import project_paths_join as ppj


def pensions(df, tb, tb_pens, mw, year, hypo):
    """ Old-Age Pensions

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    r = pd.DataFrame(index=df.index.copy())
    if hypo:
        r["pensions_sim"] = 0
        return r["pensions_sim"]

    cprint("Pensions", "red", "on_white")
    # mw is only filled until 2016
    yr = min(year, 2016)

    r["byear"] = df["byear"]
    r["exper"] = df["exper"]
    westost = [~df["east"], df["east"]]

    # individuelle monatl. Altersrente (Rentenartfaktor = 1):
    # R = EP * ZF * Rw

    # EP: Entgeltpunkte:
    # Take average values for entgeltpunkte by birth year from external statistics
    # (2015)
    avg_ep = pd.read_excel(ppj("IN_DATA", "grv_ep.xlsx"), header=3, nrows=40)
    avg_ep = avg_ep[~avg_ep["byear"].isna()]
    r = pd.merge(r, avg_ep[["byear", "avg_ep"]], how="outer")

    r["EP"] = r["avg_ep"] * r["exper"]
    # Add values for current year: ratio of own wage (up to the threshold)
    # to the mean wage
    r["EP"] = r["EP"] + np.select(
        westost,
        [
            np.minimum(df["m_wage"], tb["rvmaxekw"]) / mw["meanwages"][yr],
            np.minimum(df["m_wage"], tb["rvmaxeko"]) / mw["meanwages"][yr],
        ],
    )
    # ZF: Zugangsfaktor. Depends on the age of entering pensions
    r["regelaltersgrenze"] = 65
    # If born after 1947, each birth year raises the age threshold by one month.
    r.loc[r["byear"] > 1947, "regelaltersgrenze"] = np.minimum(
        67, ((r["byear"] - 1947) / 12) + 65
    )
    # For each year entering earlier (later) than the statutory retirement age,
    # you get a penalty (reward) of 3.6 pp.
    r["ZF"] = ((df["age"] - r["regelaltersgrenze"]) * 0.036) + 1

    # Rentenwert: The monetary value of one 'entgeltpunkt'.
    # This depends, among others, of past developments.
    # Hence, some calculations have been made
    # in the data preparation.
    lohnkomponente = mw["meanwages"][yr - 1] / (
        mw["meanwages"][yr - 2]
        * (
            (mw["meanwages"][yr - 2] / mw["meanwages"][yr - 3])
            / (mw["meanwages_sub"][yr - 2] / mw["meanwages_sub"][yr - 3])
        )
    )

    riesterfaktor = (100 - tb_pens["ava"][yr - 1] - tb_pens["rvbeitrag"][yr - 1]) / (
        100 - tb_pens["ava"][yr - 2] - tb_pens["rvbeitrag"][yr - 2]
    )
    # Rentnerquotienten
    rq = {}
    for t in [1, 2]:
        rq[t] = (tb_pens["rentenvol"][yr - t] / tb_pens["eckrente"][yr - t]) / (
            tb_pens["beitragsvol"][yr - t]
            / (tb_pens["rvbeitrag"][yr - t] / 100 * tb_pens["eckrente"][yr - t])
        )
    # Nachhaltigskeitsfaktor
    nachhfaktor = 1 + ((1 - (rq[1] / rq[2])) * tb_pens["alpha"][yr])
    # use external (SOEP) or internal value for rentenwert?
    if yr <= 2017:
        rentenwert = tb_pens["rentenwert_ext"][yr]
    else:
        # Rentenwert must not be lower than in the previous year.
        rentenwert = tb_pens["rentenwert_ext"][yr - 1] * min(
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
