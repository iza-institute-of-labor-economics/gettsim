# -*- coding: utf-8 -*-
"""
"""
import pandas as pd
from termcolor import cprint
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

    for ref in settings["Reforms"]:
        taxvars = ["incometax", "soli", "gkvbeit", "rvbeit", "pvbeit", "avbeit"]
        benvars = ["m_alg1", "m_alg2", "wohngeld", "kiz", "kindergeld", "ubi"]
        budgetvars = taxvars + benvars

        # load reform-specific results
        df = pd.read_json(ppj("OUT_DATA", "taxben_results_{}.json".format(ref)))

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

    # calculate total budget
    budget.loc["TOTAL"] = budget.sum()
    # Calculate Differences to baseline
    base = settings["Reforms"][0]
    diff_rev = pd.DataFrame(columns=settings["Reforms"][1:])
    recip_rev = pd.DataFrame(columns=settings["Reforms"][1:])
    for ref in settings["Reforms"]:
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


#    # Check Income Distribution:
#    # Equivalence Scale (modified OECD scale)
#    df["eq_scale"] = (
#        1 + 0.5 * np.maximum((df["hhsize"] - df["child14_num"] - 1), 0) + 0.3 * (df["child14_num"])
#    )
#    df["dpi_eq"] = df["dpi"] / df["eq_scale"]
#    print(df["dpi_eq"].describe())
#    plt.clf()
#    ax = df["dpi_eq"].plot.kde(xlim=(0, 4000))
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
