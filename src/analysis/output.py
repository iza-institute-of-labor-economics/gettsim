# -*- coding: utf-8 -*-
"""
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.model_code.hypo_helpers import get_reform_names
from bld.project_paths import project_paths_join as ppj


def output(settings):
    """ Tax-Benefit Output Tool.
        Produces differences in
        - total tax revenue
        - Benefit recipients

    """
    # TODO: Collect results in dataframes and calculate differences
    budget = pd.DataFrame(columns=settings["Reforms"])
    recip = pd.DataFrame(columns=settings["Reforms"])
    dpis = pd.DataFrame(columns=settings["Reforms"])

    base = settings["Reforms"][0]

    for ref in settings["Reforms"]:
        taxvars = ["incometax", "soli", "gkvbeit", "rvbeit", "pvbeit", "avbeit"]
        benvars = ["m_alg1", "m_alg2", "wohngeld", "kiz", "kindergeld", "ubi"]
        budgetvars = taxvars + benvars

        # load reform-specific results
        df = pd.read_json(ppj("OUT_DATA", "taxben_results_{}.json".format(ref)))
        # print("Number of adults: {}".format(df[df['age']>=18]['pweight'].sum()))
        # print("Number of children: {}".format(df[df['age']<18]['pweight'].sum()))

        # create weighted annual sums
        for var in budgetvars:
            # produce ubi for compatibility reasons
            if "ubi" not in df.columns:
                df["ubi"] = 0
            # For benefits, avoid double counting by only using the tu head
            if var in ["m_alg2", "wohngeld", "kiz"]:
                df.loc[df["head_tu"], var + "_w"] = df[var] * df["hweight"] * 12
                # also count recipients
                df.loc[df["head_tu"] & (df[var] > 0), var + "_recip"] = df["hweight"]
            else:
                df[var + "_w"] = df[var] * df["pweight"] * 12
            if var in benvars:
                df[var + "_w"] = df[var + "_w"] * (-1)

        budget[ref] = df.filter(regex="_w$").sum() / 1e9
        recip[ref] = df.filter(regex="recip$").sum() / 1000

        # also calculate equivalized income
        df["eq_scale"] = (
                1 + 0.5 * np.maximum((df["hhsize"] - df["child14_num"] - 1), 0) + 0.3 * (df["child14_num"])
        )

        dpis[ref]["dpi_eq"] = df["dpi"] / df["eq_scale"]
        dpis[ref]["dpi_per_head"] = df["dpi"] / df["hhsize"]
        dpis[ref]["dpi"]    = df["dpi"]
        dpis[ref]["pweight"] = df["pweight"]
        if ref != base:
            dpis[ref]["d_dpi"] = dpis[ref]["dpi_per_head"] - dpis[base]["dpi_per_head"]
            # print(dpis[ref]["d_dpi"].describe())



    # calculate total budget
    budget.loc["TOTAL"] = budget.sum()
    # Calculate Differences to baseline
    base = settings["Reforms"][0]
    diff_rev = pd.DataFrame(columns=settings["Reforms"][1:])
    recip_rev = pd.DataFrame(columns=settings["Reforms"][1:])
    for ref in settings["Reforms"]:
        # print(budget[ref])
        if ref != base:
            diff_rev[ref] = budget[ref] - budget[base]
            recip_rev[ref] = recip[ref] - recip[base]


    print("-" * 80)
    print("Budget Differences (bn € per year)")
    print(diff_rev)
    print("Recipient Differences (Households, in 1000)")
    print(recip_rev)
    print("-" * 80)

    # TODO: output to HD
    # DISTRIBUTIONAL OUTPUT
    # Density Plots. Note that these are unweighted!
    fig = plt.figure(figsize=(8,5))
    for ref in settings["Reforms"]:
        sns.distplot(dpis[ref]["dpi_eq"][dpis[ref]["dpi_eq"].between(0,5000)],
                     kde=True,
                     hist=False,
                     kde_kws={'shade': True,
                              'bw': 100},
                     label=get_reform_names("en")[ref]
                     )
    plt.title('Income Distributions')
    plt.xlabel('Personal Income')
    plt.ylabel('Density')
    plt.savefig(ppj("OUT_FIGURES", "income_densities.png"))

    # Winner/Loser Analysis
    for ref in settings["Reforms"][1:]:
        dpis[ref]["winner"] = df["pweight"] * (dpis[ref]["dpi"] > (dpis[base]["dpi"] + 5))
        dpis[ref]["loser"]  = df["pweight"] * (dpis[ref]["dpi"] < (dpis[base]["dpi"] - 5))
        winshare = 100 * (dpis[ref]["winner"].sum() / dpis[ref]["pweight"].sum())
        loseshare = 100 * (dpis[ref]["loser"].sum() / dpis[ref]["pweight"].sum())
        winavg = dpis[ref]["d_dpi"][dpis[ref]["winner"] > 0].mean()
        losavg = dpis[ref]["d_dpi"][dpis[ref]["loser"] > 0].mean()
        print("Income Gains: {}".format(dpis[ref]["d_dpi"][dpis[ref]["winner"] > 0].describe()))
        print("Income Losses: {}".format(dpis[ref]["d_dpi"][dpis[ref]["loser"] > 0].describe()))

        fig = plt.figure(figsize=(8,5))
        sns.distplot(dpis[ref]["d_dpi"][dpis[ref]["d_dpi"].between(-5000,2000)],
                     kde=True,
                     hist=False,
                     kde_kws={'shade': True,
                              'bw': 100},
                     )
#        sns.distplot(dpis[ref]["d_dpi"][dpis[ref]["d_dpi"].between(.01,2000)],
#                     kde=True,
#                     hist=False,
#                     kde_kws={'shade': True,
#                              'bw': 100},
#                     label="Winners"
#                     )
        plt.text(-2000, .0004, "{:.2f}% Losers \nAverage Loss: € {:.0f}".format(loseshare,
                         losavg * (-1)))
        plt.text(500, .0006, "{:.2f}% Winners \nAverage Gain: € {:.0f}".format(winshare,
                 winavg))
        plt.axvline(0)
        plt.title('Distribution of income change')
        plt.xlabel('Monthly income per person')
        plt.ylabel('Density')
        plt.savefig(ppj("OUT_FIGURES", "d_inc_per_person_{}.png".format(ref)))


#    print(df["dpi_eq"].describe())
#    plt.clf()
#    ax.set_title("Distribution of equivalized disp. income " + str(ref))
#    # print(graph_path + 'dist_dpi_' + ref + '.png')
#    # plt.savefig(graph_path + 'dist_dpi_' + ref + '.png')
#    print("-" * 80)
#    print("Gini-Coefficient Disp. Income: ", gini(df["dpi_eq"], df["pweight"]))
#    print("-" * 80)
#    '''

if __name__ == "__main__":
    settings = pd.read_json(ppj("IN_MODEL_SPECS", "settings.json"))
    output(settings)
