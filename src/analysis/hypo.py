# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""
Created on Fri Jun 15 14:36:30 2018

@author: iza6354
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import itertools
from termcolor import cprint

# from check_hypo import check_hypo
from custompygraph.make_plot import make_plot
from bld.project_paths import project_paths_join as ppj

from src.model_code.hypo_helpers import (
    get_ref_text,
    hypo_graph_settings,
    get_reform_names,
    get_hh_text,
)
from src.model_code.imports import get_params, say_hello, tarif_ubi
from src.analysis.tax_transfer import tax_transfer
from src.analysis.tax_transfer_funcs.taxes import tarif
from src.analysis.tax_transfer_ubi import tax_transfer_ubi, ubi_settings


def flip(items, ncol):
    """Fill columns of legend first, then rows.
    """
    return list(itertools.chain(*[items[i::ncol] for i in range(ncol)]))


def get_lego_lists(lego_vars, colors, labels, spec):

    var_list = lego_vars[spec]
    color_list = []
    label_list = []

    for var in var_list:
        color_list.append(colors[var])
        label_list.append(labels[var])

    return var_list, color_list, label_list


def make_comp_plots(lego, t, maxinc, xlabels, ylabels, lang, settings, ref):
    """ Creates compositional plots
        args:
            lego: the source dataframe
            t (int): the household type to plot
            maxinc (int): maximum income to plot
            lang (str): Language
            settings (dict): settings
            ref (str): the reform
    """

    plt.clf()
    # fig = plt.figure(figsize=(7 * 1.618, 7))
    plt.figure(figsize=(7 * 1.618, 7))
    ax = plt.axes()

    p = lego.loc[(lego["typ_bud"] == t) & (lego["m_wage"] <= (maxinc / 12))]
    p["taxes"] = p["tax_l"] + p["sic_l"]
    labels = {
        "en": {
            "sic_l": "SIC",
            "tax_l": "PIT",
            "soli_l": "Soli",
            "net_l": "NetInc",
            "cb_l": "ChBen",
            "ub_l": "UB",
            "hb_l": "HB",
            "kiz_l": "KiZ",
            "uhv_l": "Alimony Advance",
            "ubi_l": "UBI",
            "dpi_l": "DPI",
        },
        "de": {
            "sic_l": "SV-Beiträge",
            "tax_l": "ESt",
            "soli_l": "Soli",
            "net_l": "NettoEink.",
            "cb_l": "Kindergeld",
            "ub_l": "ALG2",
            "hb_l": "Wohngeld",
            "kiz_l": "Kinderzuschlag",
            "uhv_l": "Unterhaltsvorschuss",
            "ubi_l": "BGE",
            "dpi_l": "Verf. Eink.",
        },
    }

    colors = {
        "sic_l": "royalblue",
        "tax_l": "navy",
        "soli_l": "mediumslateblue",
        "net_l": "forestgreen",
        "cb_l": "tomato",
        "ub_l": "orangered",
        "hb_l": "crimson",
        "kiz_l": "firebrick",
        "uhv_l": "lightcoral",
        "ubi_l": "orangered",
    }

    if t in [11, 31]:
        lego_vars = {
            "minus": ["sic_l", "tax_l", "soli_l"],
            "plus": ["net_l", "hb_l", "ub_l"],
        }
    elif t in [22, 24]:
        lego_vars = {
            "minus": ["sic_l", "tax_l", "soli_l"],
            "plus": ["net_l", "cb_l", "uhv_l", "ub_l", "hb_l", "kiz_l"],
        }
    else:
        lego_vars = {
            "minus": ["sic_l", "tax_l", "soli_l"],
            "plus": ["net_l", "cb_l", "ub_l", "hb_l", "kiz_l"],
        }

    for part in ["plus", "minus"]:
        # If UBI reform, replace new transfers with UBI
        if (part == "plus") and ("UBI" in ref):
            lego_vars[part].insert(0, "ubi_l")
            for el in ["cb", "ub", "hb", "kiz"]:
                try:
                    lego_vars[part].remove(el + "_l")
                except ValueError:
                    pass

        lego_areas, lego_colors, lego_labels = get_lego_lists(
            lego_vars, colors, labels[lang], part
        )

        ax.stackplot(
            p["m_wage"],
            p[lego_areas].T,
            labels=lego_labels,
            colors=lego_colors,
            alpha=0.7,
        )

    ax.plot(p["m_wage"], p["dpi_l"], label=labels[lang]["dpi_l"], color="black")

    plt.ylabel(ylabels["lego"], size=18)
    plt.xlabel(xlabels["lego"], size=18)
    plt.tick_params(axis="both", which="major", labelsize=14)
    plt.ylim(p["taxes"].min() * 1.1, p["dpi"].max() * 1.1)
    plt.xlim(0, (maxinc / 12))

    # plt.title(types[t], size=14)

    box = ax.get_position()
    ax.set_position(
        [
            box.x0,
            box.y0 + box.height * 0.2,
            1.05 * box.width,
            1.05 * (box.height * 0.85),
        ]
    )

    handles, labels = ax.get_legend_handles_labels()
    plt.grid(True, axis="y")
    ncol = 4
    # leg = ax.legend(
    #     flip(handles, ncol),
    #     flip(labels, ncol),
    #     loc="upper center",
    #     fontsize=16,
    #     bbox_to_anchor=(0.48, -0.15),
    #     ncol=ncol,
    #     frameon=False,
    # )
    ax.legend(
        flip(handles, ncol),
        flip(labels, ncol),
        loc="upper center",
        fontsize=16,
        bbox_to_anchor=(0.48, -0.15),
        ncol=ncol,
        frameon=False,
    )
    plt.savefig(ppj("OUT_FIGURES", "hypo/lego_{}_{}_{}.png".format(ref, t, lang)))


def create_hypo_data(settings, tb, types, rents, avg_wage=51286):
    """
    builds a dataset identical to original SOEP output,
    but with custom household types, for which earnings are varied.

    Hypothetical Household Types defined so far:
    11: Single, no children
    22: Single Parent, one child (3 years)
    24: Single Parent, two children (3 and 8 years)
    31: Single-Earner Couple, no children
    32: Single-Earner Couple, no children

    args:
        settings(dict)
        tb(dict)
        types(list): list of hh types
        rents(dict): rents assumed for each hh type
        avg_wage (int): average wage of a full-time male worker.
                        needed for secondary earner analyses

    returns:
        pd.Dataframe which looks identical to the SOEP data, but with made-up households
    """
    # DEFINE STEPS IN YEARLY WAGES. ideally, take a multiple of 12
    #                               in order to have round number on monthly level
    wagestep = 120
    if wagestep < 50:
        print("Wagestep is pretty low. Execution could take some time...")
    # Define maximum annual income (€)
    max_inc = 1e5

    # take original data for congruence.
    # df = pd.read_pickle(data_path + 'SOEP/taxben_input_2016')
    columns = [
        "hid",
        "pid",
        "syear",
        "marstat",
        "stell",
        "hhsize",
        "laborinc",
        "assetinc",
        "imp_rent",
        "sose_pension",
        "laborinc_ind",
        "retirement",
        "hweight",
        "pweight",
        "m_self",
        "divdy",
        "alg2",
        "tenure",
        "pgemplst",
        "expft",
        "exppt",
        "expue",
        "pnr",
        "sample1",
        "plb0021",
        "comm_freq",
        "comm_dist",
        "plc0131",
        "alg_m_l1",
        "alg_l1",
        "handcap_degree",
        "ple0097",
        "partner_id",
        "D_alg_current",
        "months_ft",
        "months_pt",
        "months_ue",
        "months_pen",
        "months_mj",
        "lb0285",
        "k_rel",
        "k_nrinhh",
        "k_inco",
        "k_pmum",
        "algII_m_l1",
        "algII_l1",
        "wgeld_m_l1",
        "wgeld_l1",
        "zinszahl",
        "D_kiz_current",
        "D_sozh_current",
        "D_wg_current",
        "D_alg2_current",
        "bula",
        "hgtyp1hh",
        "counter",
        "kinderdaten",
        "age",
        "byear",
        "female",
        "foreigner",
        "pensioner",
        "ineducation",
        "military",
        "parentalleave",
        "civilservant",
        "pubsector",
        "selfemployed",
        "renteneintritt",
        "east",
        "head",
        "spouse",
        "child",
        "othmem",
        "head_num",
        "main_unit",
        "old_dummy",
        "old_dummy_sum",
        "single_unit",
        "couple_unit",
        "new_unit",
        "n",
        "new_unit_id",
        "tu_id",
        "head_tu",
        "hhsize_tu",
        "child0_1_num",
        "child1_2_num",
        "child2_num",
        "child2_3_num",
        "child3_6_num",
        "child6_num",
        "child7_16_num",
        "child7_11_num",
        "child7_13_num",
        "child11_num",
        "child12_15_num",
        "child14_17_num",
        "child14_24_num",
        "child14_num",
        "child15_num",
        "child18_num",
        "child0_1_num_tu",
        "child1_2_num_tu",
        "child2_num_tu",
        "child2_3_num_tu",
        "child3_6_num_tu",
        "child6_num_tu",
        "child7_16_num_tu",
        "child7_11_num_tu",
        "child7_13_num_tu",
        "child11_num_tu",
        "child12_15_num_tu",
        "child14_17_num_tu",
        "child14_24_num_tu",
        "child14_num_tu",
        "child15_num_tu",
        "child18_num_tu",
        "child_num_tu",
        "child_num",
        "adult_num_tu",
        "hh_korr",
        "haskids",
        "handcap_dummy",
        "qualification",
        "unskilled",
        "university",
        "hhtyp",
        "alleinerz",
        "couple",
        "transfers",
        "alg_soep",
        "months",
        "pensions",
        "m_pensions",
        "m_transfers",
        "childinc",
        "m_kapinc",
        "m_vermiet",
        "m_imputedrent",
        "m_kapinc_tu",
        "m_vermiet_tu",
        "m_imputedrent_tu",
        "versbez",
        "welfare",
        "w_hours",
        "m_wage",
        "othwage_ly",
        "m_wage_l1",
        "months_l1",
        "months_ue_l1",
        "m_wage_l2",
        "months_l2",
        "wgeld_l2",
        "wgeld_m_l2",
        "alg_l2",
        "alg_m_l2",
        "months_ue_l2",
        "h_wage",
        "work_dummy",
        "missing_wage",
        "age2",
        "age3",
        "married",
        "ln_wage",
        "exper",
        "exper2",
        "expue2",
        "tenure2",
        "heck_wage",
        "h_wage_pred",
        "pkv",
        "eigentum",
        "hgsize_mean",
        "wohnfl",
        "baujahr",
        "cnstyr",
        "kaltmiete",
        "heizkost",
        "kapdienst",
        "miete",
        "zveranl",
    ]

    df = pd.DataFrame(columns=columns)

    # drop all rows
    df = df.iloc[0:0]

    # append rows with zeros
    s2 = pd.Series(np.zeros(len(list(df))), index=list(df))
    for i in range(0, 5):
        df = df.append(s2, ignore_index=True)

    # Some of them need to be boolean values
    df["selfemployed"] = False
    df["pkv"] = False
    df["ineducation"] = False

    df["months"] = 12
    df["typ"] = df.index + 1

    df_typ2 = df[df["typ"] == 2]
    # wir brauchen zwei Alleinerziehenden-Typen
    df = df.append([df_typ2], ignore_index=True)

    df_typ3 = df[df["typ"] == 3]
    # Paare mit und ohne kinder, verschiedene Lohn- und Erwerbskonstellationen
    df = df.append([df_typ3] * 7, ignore_index=True)

    df = df.sort_values(by=["typ"])
    df["n_typ"] = df.groupby(["typ"]).cumcount() + 1

    df.loc[df["typ"] == 1, "typ_bud"] = 11
    df.loc[df["typ"] == 2, "typ_bud"] = 20 + 2 * df["n_typ"]
    df.loc[df["typ"] == 3, "typ_bud"] = 30 + df["n_typ"]

    # Vervielfache die Reihen und erhöhe den Lohn
    df = df.append([df] * int(max_inc / wagestep), ignore_index=True)
    df = df.sort_values(by=["typ_bud"])
    df["n_typ_bud"] = df.groupby(["typ_bud"]).cumcount()
    df["y_wage"] = df["n_typ_bud"] * wagestep

    df["head"] = True
    df["head_tu"] = True
    df["age"] = 30

    df["child"] = False
    df["female"] = False

    # create partners
    df = df.append([df[df["typ_bud"] > 30]], ignore_index=True)
    df = df.sort_values(by=["typ_bud", "y_wage"])
    df["female"] = (df.groupby(["typ_bud", "y_wage"]).cumcount()) > 0

    # 'produziere' Kinder...klone hid etc. von Erwachsenen und manipuliere Alter.
    # Dann wieder dranmergen

    kids = df[df["typ_bud"].isin([22, 24, 32, 34, 36, 38]) & (df["y_wage"] == 0)]

    kids = kids.append([kids] * int(max_inc / wagestep), ignore_index=True)
    kids = kids.sort_values(by=["typ_bud"])
    kids["n_typ_bud"] = kids.groupby(["typ_bud"]).cumcount()
    kids["y_wage"] = kids["n_typ_bud"] * wagestep
    # dupliziere, aber nicht für ALleinerz. mit einem Kind
    kids = kids.append(kids[kids["typ_bud"] != 22])
    kids = kids.sort_values(by=["typ_bud", "y_wage"])
    kids["n"] = kids.groupby(["typ_bud", "y_wage"]).cumcount()
    # first kid is 3, second kid is 8
    kids["age"] = 3
    kids.loc[kids["n"] == 1, "age"] = 8
    kids["child"] = True
    kids["ineducation"] = True
    kids["female"] = True

    # append kids
    df = df.append(kids)
    df = df[df["typ_bud"].notna()]
    df["typ_bud"] = df["typ_bud"].astype(int)
    print(df["typ_bud"].value_counts())
    df = df.sort_values(by=["typ_bud", "y_wage"])
    df = df.reset_index(drop=True)

    # drop missings
    df = df.dropna(subset=["typ_bud"])

    # Personal ID
    df["pid"] = df.index
    # create household id
    df["hid"] = df["y_wage"] * 1000 + df["typ_bud"].astype(int)
    df["tu_id"] = df["hid"]

    # Children variables
    df = df.drop(["child_num", "child_num_tu"], 1)
    df = df.join(
        df.groupby(["hid"])["child"].sum(), on=["hid"], how="left", rsuffix="_num"
    )
    df["child_num_tu"] = df["child_num"]

    df["child3_6_num"] = 1 * ((df["typ_bud"] % 2) == 0)
    for var in ["7_11", "7_13", "7_16", "12_15"]:
        df["child" + var + "_num"] = (
            1 * (df["typ_bud"] >= 24) * (df["typ_bud"] % 2 == 0)
        )

    df["child6_num"] = df["child3_6_num"]
    for var in ["11", "15", "18", ""]:
        df["child{}_num".format(var)] = df["child3_6_num"] + df["child7_16_num"]

    # Erster Mann ist immer Head, der Rest sind Frauen und Mädchen
    df["head"] = ~df["female"]
    df["head_tu"] = df["head"]

    df["haskids"] = df["child_num"] > 0
    df["adult_num"] = 1 + (df["typ_bud"] >= 31) * 1
    df["hhsize"] = (df["adult_num"] + df["child_num"]).astype(int)

    print(pd.crosstab(df["typ_bud"], df["child_num"]))

    tuvars = [
        "child3_6",
        "child7_11",
        "child7_13",
        "child7_16",
        "child12_15",
        "child14_24",
        "child2",
        "child6",
        "child11",
        "child15",
        "child18",
        "child",
    ]
    for var in tuvars:
        df["{}num_tu".format(var)] = df["{}_num".format(var)]

    df["hhsize_tu"] = df["hhsize"]
    df["adult_num_tu"] = df["adult_num"]
    # Household types
    df.loc[(df["adult_num_tu"] == 1) & (df["child_num_tu"] == 0), "hhtyp"] = 1
    df.loc[(df["adult_num_tu"] == 1) & (df["child_num_tu"] > 0), "hhtyp"] = 2
    df.loc[(df["adult_num_tu"] == 2) & (df["child_num_tu"] == 0), "hhtyp"] = 3
    df.loc[(df["adult_num_tu"] == 2) & (df["child_num_tu"] > 0), "hhtyp"] = 4

    df["alleinerz"] = df["hhtyp"] == 2

    # Miete und Heizkosten.
    df["cnstyr"] = 2
    df["heizkost"] = np.nan
    df["miete"] = np.nan
    for t in types:
        df.loc[df["typ_bud"] == t, "heizkost"] = rents["heizkost"][t]
        df.loc[df["typ_bud"] == t, "miete"] = rents["miete"][t]

    df["east"] = False
    df["zveranl"] = (df["typ_bud"] >= 30) & ~df["child"]

    df["worker"] = ~df["child"] * df["m_wage"] > 0
    df["worker_sum"] = np.select([df["typ_bud"] <= 32, df["typ_bud"] > 32], [1, 2])
    df["hh_korr"] = 1

    # In one earner households, only the adult man has (increasing) earnings.
    df["y_wage_ind"] = df["y_wage"]
    df.loc[df["female"], "y_wage_ind"] = 0
    # Two-earner couples: men's earnings still vary, women gets fixed amount
    # (average full-time male employee). This is for ease of modelling. For the
    # interpreation, it makes sense to swap the genders.
    # for typ_bud> 32, y_wage is hence "secondary earnings"
    df.loc[
        df["female"] & ~df["child"] & (df["typ_bud"].isin([33, 34])), "y_wage_ind"
    ] = avg_wage
    # Drop all observations with y_wage < woman's earnings
    df = df.join(
        df.groupby("hid")["y_wage_ind"].sum(), on=["hid"], how="left", rsuffix="_sum"
    )

    df["m_wage"] = df["y_wage_ind"] / 12
    df.loc[df["m_wage"] > 0, "w_hours"] = 40

    df = df.sort_values(by=["typ_bud", "y_wage", "female"])
    df = df.dropna(subset=["typ_bud"])

    df = df[df["typ_bud"] <= 34]

    return df


def hypo_graphs(dfs, settings, types, lang):
    """
    creates a couple of graphs by hypothetical household type for debugging

    args:
        dfs (dict): Dictionary containing a dataframe for each reform
        settings (dict): the settings dictionary
        types (list): list of household types
        lang (str): language for graphs
    """

    cprint("Creating Hypothetical HH Graphs...", "red", "on_white")

    # plot data contains heads only and computes outcomes for each reform
    base = settings["Reforms"][0]
    plot = dfs[base][dfs[base]["head"]].copy()
    # prepare variables that are going to be plotted
    for ref in settings["Reforms"]:
        # reduce datasets to heads
        dfs[ref] = dfs[ref][dfs[ref]["head"]].copy()
        dfs[ref] = dfs[ref].sort_values(by=["typ_bud", "y_wage"])
        # Effective Marginal Tax Rate
        plot["emtr" + ref] = np.minimum(
            (
                1
                - (dfs[ref]["dpi"] - dfs[ref]["dpi"].shift(1))
                / (dfs[ref]["m_wage"] - dfs[ref]["m_wage"].shift(1))
            ),
            1.2,
        )
        if ref != base:
            plot["d_dpi" + ref] = dfs[ref]["dpi"] - dfs[base]["dpi"]
        # plot["emtr" + ref] = 100 * np.minimum(
        #     (
        #         1
        #         - (dfs[ref]["dpi"] - dfs[ref]["dpi"].shift(1))
        #         / (dfs[ref]["m_wage"] - dfs[ref]["m_wage"].shift(1))
        #     ),
        #     1.2,
        # )

        plot.loc[plot["emtr" + ref] < -1, "emtr" + ref] = np.nan
        # Disposable income by reform
        plot["dpi" + ref] = dfs[ref]["dpi"]
        # TODO: Other outcomes...Average Tax Rate...

        # There are distinct "Lego" Plots for each reform
        lego_vars = [
            "y_wage",
            "m_wage",
            "dpi",
            "kindergeld_hh",
            "m_alg2",
            "kiz",
            "wohngeld",
            "soli_tu",
            "svbeit",
            "incometax_tu",
            "uhv_hh",
            "typ_bud",
        ]
        if "UBI" in ref:
            lego_vars.append("ubi_hh")

        lego = dfs[ref].loc[dfs[ref]["head"], lego_vars]
        # Für Doppelverdiener-HH müssten auch m_wage und svbeit auf HH-Ebene sein.
        lego["net_l"] = (
            lego["m_wage"] - lego["svbeit"] - lego["incometax_tu"] - lego["soli_tu"]
        )
        lego["cb_l"] = lego["kindergeld_hh"]
        lego["ub_l"] = lego["m_alg2"]
        lego["hb_l"] = lego["wohngeld"]
        lego["kiz_l"] = lego["kiz"]
        lego["uhv_l"] = lego["uhv_hh"]
        if "UBI" in ref:
            lego["ubi_l"] = lego["ubi_hh"]

        lego["sic_l"] = lego["svbeit"] * (-1)
        lego["tax_l"] = lego["incometax_tu"] * (-1)
        lego["soli_l"] = lego["soli_tu"] * (-1)
        lego["dpi_l"] = lego["dpi"]

        for t in types:
            xlabels, ylabels, yvars, maxinc = hypo_graph_settings(lang, t)
            make_comp_plots(lego, t, maxinc, xlabels, ylabels, lang, settings, ref)

    # The other plots combine the various reforms
    for t in types:
        # Get graph settings
        xlabels, ylabels, yvars, maxinc = hypo_graph_settings(lang, t)
        # Reduce data
        sub = plot[(plot["y_wage"] <= maxinc) & (plot["typ_bud"] == t)]

        sub = plot[(plot["y_wage"] <= maxinc) & (plot["typ_bud"] == t)]

        for plottype in ["emtr", "bruttonetto"]:
            make_plot(
                {
                    ref: [sub["m_wage"], sub[yvars[plottype] + ref]]
                    for ref in settings["Reforms"]
                },
                ylab=ylabels[plottype],
                xlab=xlabels[plottype],
                ylim_low=0,
                xlim_low=0,
                xlim_high=maxinc / 12,
            ).savefig(ppj("OUT_FIGURES", "hypo/{}_{}_{}.png".format(plottype, t, lang)))

        # These plots are only for non-baseline reforms
        for plottype in ["budget_diff"]:
            make_plot(
                {
                    ref: [sub["m_wage"], sub[yvars[plottype] + ref]]
                    for ref in settings["Reforms"][1:]
                },
                ylab=ylabels[plottype],
                xlab=xlabels[plottype],
                xlim_low=0,
                xlim_high=maxinc / 12,
                showlegend=False,
                hline=[0],
            ).savefig(ppj("OUT_FIGURES", "hypo/{}_{}_{}.png".format(plottype, t, lang)))
    # Empty memory
    plt.clf()


def hypo_tex(settings, types, rents, lang):
    """ outputs graphs in latex along with explanatory text
    """
    refnames = get_reform_names(lang)
    graphheaders = {
        "en": {
            "bruttonetto": "Budget Lines",
            "budget_diff": "Income Difference",
            "emtr": "Effective Marginal Tax Rates",
            "lego": "Compositional Graphs",
        },
        "de": {
            "bruttonetto": "Budgetlinien",
            "budget_diff": "Einkommensänderung",
            "emtr": "Effektive Grenzbelastungen",
            "lego": "Zerlegungen",
        },
    }

    texfile = open(
        ppj("OUT_HYPO", "hypographs_{}_{}.tex".format(settings["Reforms"][0], lang)),
        "w",
    )
    # Header of Tex File
    texfile.write("\\documentclass{article} \n")
    if lang == "de":
        texfile.write("\\usepackage[ngerman]{babel} \n")
    texfile.write("\\usepackage[utf8]{inputenc} \n")
    texfile.write("\\usepackage{graphicx} \n")
    texfile.write("\\usepackage{eurosym} \n")
    texfile.write(
        """\\usepackage[bookmarks=true,urlbordercolor={1 1 1},
                                  linkbordercolor={1 1 1},
                                  citebordercolor={1 1 1},
                                  colorlinks=true,
                                  citecolor=blue,linkcolor=blue]{hyperref} \n"""
    )
    texfile.write(
        """\\usepackage[paper=a4paper,
                        headheight=0pt,
                        left=20mm,
                        right=25mm,
                        top=25mm,bottom=20mm]{geometry} \n"""
    )
    texfile.write("\\renewcommand{\\familydefault}{\\sfdefault} \n")
    texfile.write("\\begin{document} \n")
    texfile.write("\\begin{center} \n")
    if "lang" == "en":
        texfile.write("\\Large{{\\textbf{{IZADYNMOD --- Sample Households}}}} \\\\ \n")
    if "lang" == "de":
        texfile.write("\\Large{{\\textbf{{IZADYNMOD --- Beispielhaushalte}}}} \\\\ \n")
    texfile.write("\\large{\\today} \\\\ \n")
    texfile.write("\\end{center} \n")
    texfile.write(
        "\\large{{\\textbf{{Baseline: {} ({}). }}}} \\\\ \n".format(
            refnames[settings["Reforms"][0]], settings["Reforms"][0]
        )
    )
    texfile.write("\\large{{\\textbf{{Reforms:  }}}} \\\\ \n")
    texfile.write("\\begin{itemize} \n")
    for r in range(1, len(settings["Reforms"])):
        texfile.write(
            "\\item \\textbf{{{}}} ({}): {} \n".format(
                refnames[settings["Reforms"][r]],
                settings["Reforms"][r],
                get_ref_text(
                    settings["Reforms"][r],
                    get_params(ppj("IN_DATA"))["y" + str(settings["taxyear"][0])],
                ),
            )
        )
    texfile.write("\\end{itemize} \n")
    texfile.write("\\listoffigures \n")
    # START TO INSERT GRAPHS
    # "emtr" can also be added
    for graphtype in ["bruttonetto", "budget_diff", "lego"]:
        texfile.write("\\clearpage \n")
        texfile.write("\\section{{{}}} \n".format(graphheaders[lang][graphtype]))
        if graphtype != "lego":
            for t in types:
                texfile.write("\\begin{figure}[htb] \n")
                texfile.write("\\caption{{{}}} \n".format(types[t]))
                texfile.write(
                    """\\includegraphics[width=0.9\\textwidth]{{{}/hypo/{}_{}_{}.png}}
                     \\\\ \n""".format(
                        ppj("OUT_FIGURES").replace("\\", "/"), graphtype, t, lang
                    )
                )
                texfile.write("\\end{figure} \n")
        if graphtype == "lego":
            for ref in settings["Reforms"]:
                texfile.write("\\subsection{{ {}}} \n".format(refnames[ref]))
                for t in types:
                    texfile.write("\\begin{figure}[htb] \n")
                    texfile.write("\\caption{{{}}} \n".format(types[t]))
                    texfile.write(
                        """\\includegraphics[width=0.9\\textwidth]{{{}/hypo/lego
                        _{}_{}_{}.png}} \\\\ \n""".format(
                            ppj("OUT_FIGURES").replace("\\", "/"), ref, t, lang
                        )
                    )
                    texfile.write(
                        get_hh_text(lang, t, rents["miete"][t], rents["heizkost"][t])
                    )
                    texfile.write("\\end{figure} \n")
                texfile.write("\\clearpage \n")
    texfile.write("\\end{document} \n")
    texfile.close()


def taxgraphs(settings, tb, tb_ubi):
    """ Simple plot of the tax tariffs
    """
    incstep = 50
    df = pd.DataFrame({"zve": np.arange(0, 2e5, incstep)})
    df["tax_baseline"] = np.vectorize(tarif)(df["zve"], tb)
    df["tax_ubi"] = np.vectorize(tarif_ubi)(df["zve"], tb_ubi)

    for ref in ["baseline", "ubi"]:
        df["mtr" + ref] = (df["tax_" + ref] - df["tax_" + ref].shift(1)) / incstep

    make_plot(
        {ref: [df["zve"], df["mtr" + ref]] for ref in ["baseline", "ubi"]},
        ylab="MTR",
        xlab="taxable income",
        ylim_low=0,
        ylim_high=1,
        xlim_low=0,
        xlim_high=2e5,
    ).savefig(ppj("OUT_FIGURES", "hypo/taxtariffs.png"))


def hypo_excel(dfs, settings, types):
    """ Produces Excel Control Output
        args:
            dfs -- dictionary of dataframes, labelled with reform
            settings -- the settings dictionary
            types -- dictionary of budget types
    """

    out_vars = [
        "typ_bud",
        "female",
        "age",
        "head",
        "child",
        "y_wage",
        "m_wage",
        "w_hours",
        "dpi",
        "m_alg2",
        "wohngeld",
        "kiz",
        "kindergeld",
        "kindergeld_hh",
        "svbeit",
        "incometax",
        "soli",
        "incometax_tu",
        "soli_tu",
        "miete",
        "heizkost",
        "uhv_hh",
    ]

    # cprint('Producing Excel Output for debugging...', 'red', 'on_white')
    for ref, df in dfs.items():
        df = df.sort_values(by=["typ_bud", "y_wage"])
        writer = pd.ExcelWriter(ppj("OUT_DATA", "check_hypo_{}.xlsx".format(ref)))

        for typ in types:
            df.loc[(df["typ_bud"] == typ)].to_excel(
                writer,
                "Typ_" + str(typ),
                columns=out_vars,
                na_rep="NaN",
                freeze_panes=(1, 0),
            )
        writer.save()


# def hypo_analysis(data_path, settings, tb, lang):

if __name__ == "__main__":
    """
    Tax-Transfer analysis with sample households
        settings: the settings dictionary
        tb: the param dictionary
        lang: language; either "de" or "en", affects labelling of graphs and tex
        document.

    """
    settings = pd.read_json(ppj("IN_MODEL_SPECS", "settings.json"))
    tb = get_params(ppj("IN_DATA"))["y" + str(settings["taxyear"][0])]
    lang = settings["lang"][0]

    types = {
        "de": {
            11: "Single, keine Kinder",
            22: "Alleinerziehend, ein Kind (3 Jahre)",
            24: "Alleinerziehend, zwei Kinder (3 und 8 Jahre)",
            31: "Paar, Alleinverdiener HH, keine Kinder",
            32: "Paar, Alleinverdiener HH, zwei Kinder (3 und 8 Jahre)",
            33: "Paar, mittleres Partnereinkommen, keine Kinder",
            34: "Paar, mittleres Partnereinkommen, zwei Kinder",
        },
        "en": {
            11: "Single Household",
            22: "Single Parent, one child (3 years)",
            24: "Single Parent, two children (3 and 8 years)",
            31: "One-earner couple, no children",
            32: "One-earner couple, two children (3 and 8 years)",
            # 33: "Two-earner couple, avg. income of first earner",
            # 34: "Two-earner couple, avg. income of first earner, 2 children",
        },
    }
    # Monthly rent and heating cost for households. Source: Bundesagentur für Arbeit,
    # average amounts for benefit recipients.
    rents = {
        "heizkost": {
            11: 61,
            22: 90,
            24: 109,
            31: 92,
            32: 121,
            33: 92,
            34: 121,
            35: 92,
            36: 121,
        },
        "miete": {
            11: 265,
            22: 364,
            24: 428,
            31: 353,
            32: 482,
            33: 353,
            34: 482,
            35: 353,
            36: 482,
        },
    }

    # create hypo data
    df = create_hypo_data(settings, tb, types[lang], rents)

    # run them through tax_transfer_funcs
    # taxout_hypo is a dictionary containing dataframes for each reform
    taxout_hypo = {}
    for ref in settings["Reforms"]:
        say_hello(settings["taxyear"][0], ref, True)
        if "RS" in ref:
            taxout_hypo[ref] = tax_transfer(
                df, settings["taxyear"][0], settings["taxyear"][0], tb, hyporun=True
            )
        if "UBI" in ref:
            taxout_hypo[ref] = tax_transfer_ubi(
                df,
                settings["taxyear"][0],
                settings["taxyear"][0],
                ubi_settings(tb),
                hyporun=True,
            )

        # Export to check against Stata Output
        taxout_hypo[ref][taxout_hypo[ref]["head"]].to_json(
            ppj("OUT_DATA", "python_check_{}.json".format(ref))
        )

    # produce excel control output
    hypo_excel(taxout_hypo, settings, types[lang])
    # produce graphs
    hypo_graphs(taxout_hypo, settings, types[lang], lang)
    # produce latex output with these graphs
    hypo_tex(settings, types[lang], rents, lang)
    taxgraphs(settings, tb, ubi_settings(tb))
    # check against Stata output.
    # check_hypo(settings)
