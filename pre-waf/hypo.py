# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 14:36:30 2018

@author: iza6354
"""
from imports import *
from tt_list import *
from check_hypo import check_hypo
from settings import hypo_graph_settings

import itertools


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


def create_hypo_data(data_path, settings, tb):
    """
    builds a dataset identical to original SOEP output,
    but with custom household types, for which earnings are varied.

    Hypothetical Household Types defined so far:
    11: Single, keine Kinder
    22: Alleinerziehend, ein Kind (3 Jahre)
    24: Alleinerziehend, zwei Kinder (3 und 8 Jahre)
    31: Paar, Alleinverdiener HH, keine Kinder
    32: Paar, Alleinverdiener HH, zwei Kinder
    """
    # DEFINE STEPS IN YEARLY WAGES
    wagestep = 200

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
        "adult_num",
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
    # Alleinerziehende
    df = df.append([df_typ2], ignore_index=True)

    df_typ3 = df[df["typ"] == 3]
    # Paare mit und ohne kinder
    df = df.append([df_typ3] * 7, ignore_index=True)

    df = df.sort_values(by=["typ"])
    df["n_typ"] = df.groupby(["typ"]).cumcount() + 1

    df.loc[df["typ"] == 1, "typ_bud"] = 11
    df.loc[df["typ"] == 2, "typ_bud"] = 20 + 2 * df["n_typ"]
    df.loc[df["typ"] == 3, "typ_bud"] = 30 + df["n_typ"]

    df[["typ", "typ_bud"]]

    # Vervielfache die Reihen und erhöhe den Lohn
    df = df.append([df] * 500, ignore_index=True)
    df = df.sort_values(by=["typ_bud"])
    df["n_typ_bud"] = df.groupby(["typ_bud"]).cumcount()
    df["y_wage"] = df["n_typ_bud"] * wagestep

    df["head"] = True
    df["head_tu"] = True
    df["age"] = 30

    df["child"] = False
    df["female"] = False

    # verdopple die Reihen mit Paarhaushalten
    df = df.append([df[df["typ_bud"] > 30]], ignore_index=True)
    df = df.sort_values(by=["typ_bud", "y_wage"])
    df["female"] = (df.groupby(["typ_bud", "y_wage"]).cumcount()) > 0

    # 'produziere' Kinder...klone hid etc. von Erwachsenen und manipuliere Alter.
    # Dann wieder dranmergen

    kids = df[df["typ_bud"].isin([22, 24, 32, 34, 36, 38]) & (df["y_wage"] == 0)]

    kids = kids.append([kids] * 500, ignore_index=True)
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
    df = df.join(df.groupby(["hid"])["child"].sum(), on=["hid"], how="left", rsuffix="_num")
    df["child_num_tu"] = df["child_num"]

    df["child3_6_num"] = 1 * ((df["typ_bud"] % 2) == 0)
    for var in ["7_11", "7_13", "7_16", "12_15"]:
        df["child" + var + "_num"] = 1 * (df["typ_bud"] >= 24) * (df["typ_bud"] % 2 == 0)

    df["child6_num"] = df["child3_6_num"]
    for var in ["11", "15", "18", ""]:
        df["child{}_num".format(var)] = df["child3_6_num"] + df["child7_16_num"]

    # Erster Mann ist immer Head, der Rest sind Frauen und Mädchen
    df["head"] = ~df["female"]
    df["head_tu"] = df["head"]

    df["haskids"] = df["child_num"] > 0
    df["adult_num"] = 1 + (df["typ_bud"] >= 31) * 1
    df["hhsize"] = df["adult_num"] + df["child_num"]

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
    df.loc[df["hhsize"] == 1, "heizkost"] = 56
    df.loc[df["typ_bud"].isin([22, 24, 31, 33, 35, 37]), "heizkost"] = 90
    df.loc[df["typ_bud"].isin([32, 34, 36, 38]), "heizkost"] = 110

    df.loc[df["hhsize"] == 1, "miete"] = 380 - df["heizkost"]
    df.loc[df["typ_bud"].isin([22, 24, 31, 33, 35, 37]), "miete"] = 510 - df["heizkost"]
    df.loc[df["typ_bud"].isin([32, 34, 36, 38]), "miete"] = 600 - df["heizkost"]

    df["east"] = False
    df["zveranl"] = (df["typ_bud"] >= 30) * ~df["child"]
    df["worker"] = ~df["child"] * df["m_wage"] > 0
    df["worker_sum"] = np.select([df["typ_bud"] <= 32, df["typ_bud"] > 32], [1, 2])
    df["hh_korr"] = 1

    # Teile das Jahreseinkommen auf für Paare...
    # s gibt erstmal nur alleinverdiener
    df["y_wage_ind"] = df["y_wage"]
    df.loc[df["female"], "y_wage_ind"] = 0
    df["m_wage"] = df["y_wage_ind"] / 12
    df.loc[df["m_wage"] > 0, "w_hours"] = 40

    df = df.sort_values(by=["typ_bud", "y_wage", "female"])
    df = df.dropna(subset=["typ_bud"])
    # Drop Doppeltverdiener for the moment.
    df = df.query("typ_bud < 33")

    return df


def hypo_graphs(dfs, settings):
    """
    creates a couple of graphs by hypothetical household type for debugging
    dfs: Dictionary containing a dataframe for each reform
    settings: the settings dictionary
    """
    print("Creating Hypothetical HH Graphs...")
    # Get graph settings
    xlabels, ylabels, yvars, maxinc = hypo_graph_settings()

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
    ]
    # Excel Control output
    print("Producing Excel Output for debugging...")
    for ref, df in dfs.items():
        df = df.sort_values(by=["typ_bud", "y_wage"])
        for typ in [11, 22, 24, 31, 32]:
            df.loc[(df["typ_bud"] == typ)].to_excel(
                settings["DATA_PATH"] + "check_hypo_" + ref + "_" + str(typ) + ".xlsx",
                columns=out_vars,
                na_rep="NaN",
                freeze_panes=(1, 0),
            )

    # plot data contains heads only and computes outcomes for each reform
    base = settings["Reforms"][0]
    plot = dfs[base][dfs[base]["head"]]
    # prepare variables that are going to be plotted
    for ref in settings["Reforms"]:
        # reduce datasets to heads
        dfs[ref] = dfs[ref][dfs[ref]["head"]]
        # Effective Marginal Tax Rate
        plot["emtr" + ref] = 100 * np.minimum(
            (
                1
                - (dfs[ref]["dpi"] - dfs[ref]["dpi"].shift(1))
                / (dfs[ref]["m_wage"] - dfs[ref]["m_wage"].shift(1))
            ),
            1.2,
        )
        plot.loc[plot["emtr" + ref] < -1, "emtr" + ref] = np.nan
        # Disposable income by reform
        plot["dpi" + ref] = dfs[ref]["dpi"]
        # Other outcomes...Average Tax Rate...

    # Lego graphs so far only for the baseline scenario
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
        "typ_bud",
    ]
    lego = dfs[base].loc[dfs[base]["head"] == True, lego_vars]
    # Für Doppelverdiener-HH müssten auch m_wage und svbeit auf HH-Ebene sein.
    lego["net_l"] = lego["m_wage"] - lego["svbeit"] - lego["incometax_tu"] - lego["soli_tu"]
    lego["cb_l"] = lego["kindergeld_hh"]
    lego["ub_l"] = lego["m_alg2"]
    lego["hb_l"] = lego["wohngeld"]
    lego["kiz_l"] = lego["kiz"]

    lego["sic_l"] = lego["svbeit"] * (-1)
    # lego['tax_l'] = lego['sic_l'] - lego['incometax']
    lego["tax_l"] = (lego["incometax_tu"] + lego["soli_tu"]) * (-1)
    lego["dpi_l"] = lego["dpi"]

    # Actual plotting starts here
    for t in [11, 22, 24, 31, 32]:
        # Reduce data
        sub = plot[(plot["y_wage"] <= maxinc) & (plot["typ_bud"] == t)]

        for plottype in ["emtr", "bruttonetto"]:
            plt.clf()
            ax = plt.axes()
            for ref in settings["Reforms"]:
                ax.plot(sub["m_wage"], sub[yvars[plottype] + ref])

            plt.ylabel(ylabels[plottype], size=14)
            plt.xlabel(xlabels[plottype], size=14)

            plt.savefig("{}hypo/{}_{}.png".format(settings["GRAPH_PATH"], plottype, t))

        # Lego Plots...
        plt.clf()
        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes()

        p = lego.loc[(lego["typ_bud"] == t) & (lego["m_wage"] <= (maxinc / 12))]
        p["taxes"] = p["tax_l"] + p["sic_l"]
        labels = {
            "sic_l": "SIC",
            "tax_l": "PIT",
            "net_l": "NetInc",
            "cb_l": "ChBen",
            "ub_l": "ALG2",
            "hb_l": "HB",
            "kiz_l": "KiZ",
        }

        colors = {
            "sic_l": "orangered",
            "tax_l": "royalblue",
            "net_l": "grey",
            "cb_l": "darkgreen",
            "ub_l": "gold",
            "hb_l": "purple",
            "kiz_l": "darkorange",
        }

        if t in [11, 31]:

            lego_vars = {"minus": ["sic_l", "tax_l"], "plus": ["net_l", "hb_l", "ub_l"]}

        else:

            lego_vars = {
                "minus": ["sic_l", "tax_l"],
                "plus": ["net_l", "cb_l", "ub_l", "hb_l", "kiz_l"],
            }

        for part in ["plus", "minus"]:
            lego_areas, lego_colors, lego_labels = get_lego_lists(lego_vars, colors, labels, part)

            ax.stackplot(p["m_wage"], p[lego_areas].T, labels=lego_labels, colors=lego_colors)

        ax.plot(p["m_wage"], p["dpi_l"], label="DPI", color="black")

        plt.ylabel(ylabels["lego"], size=14)
        plt.xlabel(xlabels["lego"], size=14)

        plt.ylim(p["taxes"].min() * 1.1, p["dpi"].max() * 1.1)
        plt.xlim(0, (maxinc / 12))

        types = {
            11: "Single, keine Kinder",
            22: "Alleinerziehend, ein Kind (3 Jahre)",
            24: "Alleinerziehend, zwei Kinder (3 und 8 Jahre)",
            31: "Paar, Alleinverdiener HH, keine Kinder",
            32: "Paar, Alleinverdiener HH, zwei Kinder",
        }

        plt.title(types[t], size=14)

        box = ax.get_position()
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.2, 1.05 * box.width, 1.05 * (box.height * 0.85)]
        )

        handles, labels = ax.get_legend_handles_labels()

        ncol = 4
        leg = ax.legend(
            flip(handles, ncol),
            flip(labels, ncol),
            loc="upper center",
            fontsize=14,
            bbox_to_anchor=(0.48, -0.15),
            ncol=ncol,
        )

        plt.savefig("{}hypo/lego_{}.png".format(settings["GRAPH_PATH"], t))


def hypo_analysis(data_path, settings, tb):
    """
    Tax-Transfer analysis with hypothetical households


    """
    # create hypo data
    df = create_hypo_data(data_path, settings, tb)

    # run them through tax_transfer
    # taxout_hypo collects all result dataframes
    taxout_hypo = {}
    for ref in settings["Reforms"]:
        say_hello(settings["taxyear"], ref, True)
        if "RS" in ref:
            taxout_hypo[ref] = tax_transfer(
                df, settings["taxyear"], settings["taxyear"], tb, hyporun=True
            )
        if "UBI" in ref:
            taxout_hypo[ref] = tax_transfer_ubi(
                df, settings["taxyear"], settings["taxyear"], tb, hyporun=True
            )

        # Export to check against Stata Output
        taxout_hypo[ref][taxout_hypo[ref]["head"]].to_json(
            data_path + "hypo/python_check" + str(ref) + ".json"
        )

    # produce graphs
    hypo_graphs(taxout_hypo, settings)
    # check against Stata output.
    check_hypo(settings)
